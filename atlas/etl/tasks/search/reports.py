"""Celery tasks to keep report search up to date."""
import contextlib

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import Reports


@receiver(post_save, sender=Reports)
def updated_report(sender, instance, **kwargs):
    """When report is updated, add it to search."""
    load_report.delay(instance.report_id)


@shared_task
def delete_report(report_id):
    """Celery task to remove a report from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:reports AND atlas_id:%s" % report_id)


@shared_task
def load_report(report_id):
    """Celery task to reload a report in search."""
    load_reports(report_id)


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

    load_reports()


def load_reports(report_id=None):
    """Load a group of reports to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
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
    )

    if report_id:
        reports = reports.filter(report_id=report_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(reports.all(), batch_size=1000)))


def solr_load_batch(batch):
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(report):
    """Build a report doc."""
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
        "report_last_updated": solr_date(report._modified_at),
        "epic_master_file": report.system_identifier,
        "epic_record_id": report.system_id,
        "visible": report.visible,
        "orphan": report.orphan or "N",
        "runs": 10,
        "epic_template": report.system_template_id,
        "last_load_date": solr_date(report.etl_date),
        "query": [query.query for query in report.queries.all()],
        "fragility_tags": [],
        "related_terms": [],
        "linked_description": [],
        "related_projects": [],
        "related_initiatives": [],
    }

    with contextlib.suppress(AttributeError):
        doc = build_report_doc(report, doc)

    for project_link in report.projects.all():
        doc = build_report_project_docs(project_link, doc)

    return clean_doc(doc)


def build_report_doc(report, doc):
    """Build doc from report docs."""
    doc["description"].extend([report.docs.description, report.docs.assumptions])
    doc["operations_owner"] = str(report.docs.ops_owner)
    doc["requester"] = str(report.docs.requester)
    doc["created"] = solr_date(report.docs._created_at)
    doc["organizational_value"] = str(report.docs.org_value)
    doc["estimated_run_frequency"] = str(report.docs.frequency)
    doc["fragility"] = str(report.docs.fragility)
    doc["executive_visibility"] = report.docs.executive_report or "N"
    doc["maintenance_schedule"] = str(report.docs.maintenance_schedule)
    doc["last_updated"] = solr_date(report.docs._modified_at)
    doc["created_by"] = str(report.docs.created_by)
    doc["updated_by"] = str(report.docs.modified_by)
    doc["enabled_for_hyperspace"] = report.docs.enabled_for_hyperspace
    doc["do_not_purge"] = report.docs.do_not_purge
    doc["documented"] = "1"
    doc["fragility_tags"].extend(
        [str(tag_link.fragility_tag) for tag_link in report.docs.fragility_tags.all()]
    )

    for term_link in report.docs.terms.all():
        doc["related_terms"].append(str(term_link.term))
        doc["linked_description"].extend(
            [term_link.term.summary, term_link.term.technical_definition]
        )

    return doc


def build_report_project_docs(project_link, doc):
    """Build report project docs."""
    doc["related_projects"].append(str(project_link.project))
    doc["linked_description"].extend(
        [
            project_link.project.description,
            project_link.project.purpose,
            project_link.annotation,
        ]
    )

    with contextlib.suppress(AttributeError):
        doc["related_initiatives"].append(str(project_link.project.initiative))
        doc["linked_description"].append(project_link.project.initiative.description)

    return doc
