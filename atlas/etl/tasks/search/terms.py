"""Celery tasks to keep term search up to date."""
import contextlib

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import Terms


@receiver(pre_delete, sender=Terms)
def deleted_term(sender, instance, **kwargs):
    """When term is delete, remove it from search."""
    delete_term.delay(instance.term_id)


@receiver(post_save, sender=Terms)
def updated_term(sender, instance, **kwargs):
    """When term is updated, add it to search."""
    load_term.delay(instance.term_id)


@shared_task
def delete_term(term_id):
    """Celery task to remove a term from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:terms AND atlas_id:%s" % term_id)


@shared_task
def load_term(term_id):
    """Celery task to reload a term in search."""
    load_terms(term_id)


@shared_task
def reset_terms():
    """Reset term group in solr.

    1. Delete all terms from Solr
    2. Query all existing terms
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:terms")
    solr.optimize()

    load_terms()


def load_terms(term_id=None):
    """Load a group of terms to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    terms = (
        Terms.objects.select_related("approved_by")
        .select_related("modified_by")
        .prefetch_related("report_docs")
        .prefetch_related("report_docs__report_doc")
        .prefetch_related("report_docs__report_doc__report")
        .prefetch_related("projects")
        .prefetch_related("projects__project")
        .prefetch_related("projects__project__initiative")
    )

    if term_id:
        terms = terms.filter(term_id=term_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(terms.all(), batch_size=1000)))


def solr_load_batch(batch):
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(term):
    """Build term doc."""
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
        "approval_date": solr_date(term._approved_at),
        "approved_by": str(term.approved_by),
        "has_external_standard": "Y" if bool(term.has_external_standard) else "N",
        "external_url": term.has_external_standard,
        "valid_from": solr_date(term._valid_from),
        "valid_to": solr_date(term._valid_to),
        "last_updated": solr_date(term._modified_at),
        "updated_by": str(term.modified_by),
        "related_projects": [],
        "related_initiatives": [],
        "related_terms": [],
        "related_reports": [],
        "linked_name": [],
        "linked_description": [],
    }

    for project_link in term.projects.all():
        # Build term project doc.
        doc["related_projects"].append(str(project_link.project))
        doc["linked_description"].extend(
            [project_link.project.description, project_link.annotation]
        )

        with contextlib.suppress(AttributeError):
            doc["related_initiatives"].append(str(project_link.project.initiative))
            doc["linked_description"].append(
                project_link.project.initiative.description
            )

    for report_doc_link in term.report_docs.all():
        # Build term report doc.
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

    return clean_doc(doc)
