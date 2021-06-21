"""Celery tasks to keep term search up to date."""
from datetime import datetime

import pysolr
import pytz
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_chunked_iterator import iterator
from etl.tasks.functions import chunker, clean_doc
from index.models import Terms


@receiver(post_delete, sender=Terms)
def deleted_term(sender, **kwargs):
    """When term is delete, remove it from search."""
    print(sender, **kwargs)


@receiver(post_save, sender=Terms)
def updated_term(sender, **kwargs):
    """When term is updated, add it to search."""
    print(sender, **kwargs)


@shared_task
def reset_terms():
    """Reset term group in solr.

    1. Delete all terms from Solr
    2. Query all existing terms
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:aterms")
    solr.optimize()

    terms = (
        Terms.objects.select_related("approved_by")
        .select_related("modified_by")
        .prefetch_related("report_docs")
        .prefetch_related("report_docs__report_doc")
        .prefetch_related("report_docs__report_doc__report")
        .prefetch_related("projects")
        .prefetch_related("projects__project")
        .prefetch_related("projects__project__initiative")
        .all()
    )

    load_terms(terms)


def load_terms(terms):
    """Load a group of terms to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    docs = []

    for term in iterator(terms):
        doc = {
            "id": "/terms/%s" % term.term_id,
            "atlas_id": term.term_id,
            "type": "terms",
            "name": str(term),
            "visible": "Y",
            "orphan": "N",
            "runs": 10,
            "description": [term.summary, term.technical_definition],
            "approved": term.approved or "N",
            "approval_date": (
                datetime.strftime(
                    term._approved_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if term._approved_at
                else None
            ),
            "approved_by": str(term.approved_by),
            "has_external_standard": "Y" if bool(term.has_external_standard) else "N",
            "external_url": term.has_external_standard,
            "valid_from": (
                datetime.strftime(
                    term._valid_from.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if term._valid_from
                else None
            ),
            "valid_to": (
                datetime.strftime(
                    term._valid_to.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if term._valid_to
                else None
            ),
            "last_updated": (
                datetime.strftime(
                    term._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
                )
                if term._modified_at
                else None
            ),
            "updated_by": str(term.modified_by),
            "related_projects": [],
            "related_initiatives": [],
            "related_terms": [],
            "related_reports": [],
            "linked_name": [],
            "linked_description": [],
        }

        for project_link in term.projects.all():
            doc["related_projects"].append(str(project_link.project))
            doc["linked_description"].extend(
                [project_link.project.description, project_link.annotation]
            )

            if project_link.project.initiative:
                doc["related_initiatives"].append(str(project_link.project.initiative))
                doc["linked_description"].append(
                    project_link.project.initiative.description
                )

        for report_doc_link in term.report_docs.all():
            doc["related_reports"].append(str(report_doc_link.report_doc.report))

            doc["linked_name"].extend(
                [
                    report_doc_link.report_doc.report.name,
                    report_doc_link.report_doc.report.title,
                ]
            )

            doc["linked_description"].extend(
                [
                    report_doc_link.report_doc.description,
                    report_doc_link.report_doc.assumptions,
                    report_doc_link.report_doc.report.description,
                    report_doc_link.report_doc.report.detailed_description,
                ]
            )

        docs.append(clean_doc(doc))

    # load the results in batches of 1k.
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    for doc in chunker(docs, 1000):
        solr.add(doc)
