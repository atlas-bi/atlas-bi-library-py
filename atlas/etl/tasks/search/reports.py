"""Celery tasks to keep report search up to date."""
from datetime import datetime

import pysolr
import pytz
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_chunked_iterator import iterator
from etl.tasks.functions import chunker, clean_doc
from index.models import Reports


@receiver(post_delete, sender=Reports)
def deleted_report(sender, **kwargs):
    """When report is delete, remove it from search."""
    print(sender, **kwargs)


@receiver(post_save, sender=Reports)
def updated_report(sender, **kwargs):
    """When report is updated, add it to search."""
    print(sender, **kwargs)


@shared_task
def reset_reports():
    """Reset report group in solr.

    1. Delete all reports from Solr
    2. Query all existing reports
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:reports")
    solr.optimize()

    reports = (
        Reports.objects.select_related("created_by")
        .select_related("modified_by")
        .select_related("type")
        .prefetch_related("docs")
        .prefetch_related("docs__ops_owner")
        .prefetch_related("docs__requester")
        .prefetch_related("docs__org_value")
        .prefetch_related("docs__frequency")
        .prefetch_related("docs__fragility")
        .prefetch_related("docs__maintenance_schedule")
        .prefetch_related("docs__created_by")
        .prefetch_related("docs__modified_by")
        .prefetch_related("queries")
        .prefetch_related("docs__fragility_tags")
        .prefetch_related("docs__fragility_tags")
        .prefetch_related("docs__terms")
        .prefetch_related("projects")
        .prefetch_related("projects__project")
        .prefetch_related("projects__project__initiative")
        .all()
    )

    load_reports(reports)


def load_reports(reports):
    """Load a group of reports to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    docs = []

    for report in iterator(reports):
        doc = {
            "id": "/reports/%s" % report.report_id,
            "atlas_id": report.report_id,
            "type": "reports",
            "source_server": report.system_server,
            "source_database": report.system_db,
            "name": str(report),
            "description": [
                report.description,
                report.detailed_description,
                report.system_description,
            ],
            "certification": report.certification_tag,
            "report_type": report.type.short,
            "author": str(report.created_by),
            "report_last_updated_by": str(report.modified_by),
            "report_last_updated": (
                datetime.strftime(
                    report._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if report._modified_at
                else None
            ),
            "epic_master_file": report.system_identifier,
            "epic_record_id": report.system_id,
            "visible": report.visible,
            "orphan": report.orphan or "N",
            "runs": 10,
            "epic_template": report.system_template_id,
            "last_load_date": report.etl_date,
            "query": [],
            "fragility_tags": [],
            "related_terms": [],
            "linked_description": [],
            "related_projects": [],
            "related_initiatives": [],
        }
        for query in report.queries.all():
            doc["query"].append(query.query)

        if report.has_docs():
            doc["description"].extend(
                [report.docs.description, report.docs.assumptions]
            )
            doc["operations_owner"] = str(report.docs.ops_owner)
            doc["requester"] = str(report.docs.requester)
            doc["created"] = (
                datetime.strftime(
                    report.docs._created_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if report.docs._created_at
                else None
            )
            doc["organizational_value"] = str(report.docs.org_value)
            doc["estimated_run_frequency"] = str(report.docs.frequency)
            doc["fragility"] = str(report.docs.fragility)
            doc["executive_visibility"] = report.docs.executive_report or "N"
            doc["maintenance_schedule"] = str(report.docs.maintenance_schedule)
            doc["last_updated"] = (
                datetime.strftime(
                    report.docs._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if report.docs._modified_at
                else None
            )
            doc["created_by"] = str(report.docs.created_by)
            doc["updated_by"] = str(report.docs.modified_by)
            doc["enabled_for_hyperspace"] = report.docs.enabled_for_hyperspace
            doc["do_not_purge"] = report.docs.do_not_purge
            doc["documented"] = "Y"

            for tag_link in report.docs.fragility_tags.all():
                doc["fragility_tags"].append(str(tag_link.fragility_tag))

            for term_link in report.docs.terms.all():
                doc["related_terms"].append(str(term_link.term))
                doc["linked_description"].extend(
                    [term_link.term.summary, term_link.term.technical_definition]
                )

        for project_link in report.projects.all():
            doc["related_projects"].append(str(project_link.project))
            doc["linked_description"].extend(
                [
                    project_link.project.description,
                    project_link.project.purpose,
                    project_link.annotation,
                ]
            )

            if project_link.project.initiative:
                doc["related_initiatives"].append(str(project_link.project.initiative))
                doc["linked_description"].append(
                    project_link.project.initiative.description
                )

        docs.append(clean_doc(doc))

    # load the results in batches of 1k.
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    for doc in chunker(docs, 1000):
        solr.add(doc)
