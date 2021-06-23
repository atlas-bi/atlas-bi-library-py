"""Celery tasks to keep project search up to date."""
from datetime import datetime

import pysolr
import pytz
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_chunked_iterator import iterator
from etl.tasks.functions import chunker, clean_doc
from index.models import Projects


@receiver(post_delete, sender=Projects)
def deleted_project(sender, **kwargs):
    """When project is delete, remove it from search."""
    # print(sender, **kwargs)
    print("ok")


@receiver(post_save, sender=Projects)
def updated_project(sender, **kwargs):
    """When project is updated, add it to search."""
    # print(sender, **kwargs)
    print("ok")


@shared_task
def reset_projects():
    """Reset project group in solr.

    1. Delete all projects from Solr
    2. Query all existing projects
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:projects")
    solr.optimize()

    projects = (
        Projects.objects.select_related("ops_owner")
        .select_related("exec_owner")
        .select_related("analytics_owner")
        .select_related("data_owner")
        .select_related("financial_impact")
        .select_related("strategic_importance")
        .select_related("modified_by")
        .select_related("initiative")
        .prefetch_related("term_annotations")
        .prefetch_related("term_annotations__term")
        .prefetch_related("report_annotations")
        .prefetch_related("report_annotations__report")
        .prefetch_related("report_annotations__report__docs")
        .all()
    )

    load_projects(projects)


def load_projects(projects):
    """Load a group of projects to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    docs = []

    for project in iterator(projects):
        doc = {
            "id": "/projects/%s" % project.project_id,
            "atlas_id": project.project_id,
            "type": "projects",
            "name": str(project),
            "visible": "Y",
            "orphan": "N",
            "runs": 10,
            "description": [project.purpose, project.description],
            "operations_owner": str(project.ops_owner),
            "executive_owner": str(project.exec_owner),
            "analytics_owner": str(project.analytics_owner),
            "data_owner": str(project.data_owner),
            "financial_impact": str(project.financial_impact),
            "strategic_importance": str(project.strategic_importance),
            "external_url": project.external_documentation_url,
            "last_updated": (
                datetime.strftime(
                    project._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if project._modified_at
                else None
            ),
            "updated_by": str(project.modified_by),
            "related_initiatives": [],
            "related_terms": [],
            "related_reports": [],
            "linked_name": [],
            "linked_description": [],
        }

        if project.initiative:
            doc["related_initiatives"].append(str(project.initiative))
            doc["linked_description"].append(project.initiative.description)

        for term_annotation in project.term_annotations.all():
            doc["related_terms"].append(str(term_annotation.term))
            doc["linked_description"].extend(
                [
                    term_annotation.term.summary,
                    term_annotation.term.technical_definition,
                    term_annotation.annotation,
                ]
            )

        for report_annotation in project.report_annotations.all():
            doc["related_reports"].append(str(report_annotation.report))

            doc["linked_name"].extend(
                [report_annotation.report.name, report_annotation.report.title]
            )

            doc["linked_description"].extend(
                [
                    report_annotation.report.description,
                    report_annotation.report.detailed_description,
                ]
            )

            if report_annotation.report.has_docs():
                doc["linked_description"].extend(
                    [
                        report_annotation.report.docs.description,
                        report_annotation.report.docs.assumptions,
                    ]
                )

        docs.append(clean_doc(doc))

    # load the results in batches of 1k.
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    for doc in chunker(docs, 1000):
        solr.add(doc)
