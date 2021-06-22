"""Celery tasks to keep initiative search up to date."""
from datetime import datetime

import pysolr
import pytz
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_chunked_iterator import iterator
from etl.tasks.functions import chunker, clean_doc
from index.models import Initiatives


@receiver(post_delete, sender=Initiatives)
def deleted_initiative(sender, **kwargs):
    """When initiative is delete, remove it from search."""
    # print(sender, **kwargs)
    print("ok")


@receiver(post_save, sender=Initiatives)
def updated_initiative(sender, instance, **kwargs):
    """When initiative is updated, add it to search."""
    # print(sender, **kwargs)
    print("ok")


@shared_task
def reset_initiatives():
    """Reset initiative group in solr.

    1. Delete all initiatives from Solr
    2. Query all existing initiatives
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:initiatives")
    solr.optimize()

    initiatives = (
        Initiatives.objects.select_related("ops_owner")
        .select_related("exec_owner")
        .select_related("financial_impact")
        .select_related("strategic_importance")
        .select_related("modified_by")
        .prefetch_related("projects__terms")
        .prefetch_related("projects__terms__term")
        .prefetch_related("projects__reports")
        .prefetch_related("projects__reports__report")
        .prefetch_related("projects__reports__report__docs")
        .all()
    )

    load_initiatives(initiatives)


def load_initiatives(initiatives):
    """Load a group of initiatives to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    docs = []

    for initiative in iterator(initiatives):
        doc = {
            "id": "/initiatives/%s" % initiative.initiative_id,
            "atlas_id": initiative.initiative_id,
            "type": "initiatives",
            "name": str(initiative),
            "visible": "Y",
            "orphan": "N",
            "runs": 10,
            "operations_owner": str(initiative.ops_owner),
            "description": initiative.description,
            "executive_owner": str(initiative.exec_owner),
            "financial_impact": str(initiative.financial_impact),
            "strategic_importance": str(initiative.strategic_importance),
            "last_updated": (
                datetime.strftime(
                    initiative._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if initiative._modified_at
                else None
            ),
            "updated_by": str(initiative.modified_by),
            "related_projects": [],
            "linked_description": [],
            "related_terms": [],
            "related_reports": [],
            "linked_name": [],
        }

        for project in initiative.projects.all():

            doc["related_projects"].append(str(project))
            doc["linked_description"].extend([project.purpose, project.description])

            for term in project.terms.all():
                doc["related_terms"].append(str(term.term))
                doc["linked_description"].extend(
                    [term.term.summary, term.term.technical_definition, term.annotation]
                )

            for report in project.reports.all():

                doc["related_reports"].append(str(report.report))

                doc["linked_name"].extend([report.report.name, report.report.title])

                doc["linked_description"].extend(
                    [report.report.description, report.report.detailed_description]
                )

                if report.report.has_docs():
                    doc["linked_description"].extend(
                        [report.report.docs.description, report.report.docs.assumptions]
                    )

        docs.append(clean_doc(doc))

    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    # load the results in batches of 1k.
    for doc in chunker(docs, 1000):
        solr.add(doc)
