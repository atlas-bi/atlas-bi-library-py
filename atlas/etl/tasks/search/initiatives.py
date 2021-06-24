"""Celery tasks to keep initiative search up to date."""
import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import Initiatives


@receiver(pre_delete, sender=Initiatives)
def deleted_initiative(sender, instance, **kwargs):
    """When initiative is delete, remove it from search."""
    delete_initiative.delay(instance.initiative_id)


@receiver(post_save, sender=Initiatives)
def updated_initiative(sender, instance, **kwargs):
    """When initiative is updated, add it to search."""
    load_initiative.delay(instance.initiative_id)


@shared_task
def delete_initiative(initiative_id):
    """Celery task to remove a initiative from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:initiatives AND atlas_id:%s" % initiative_id)


@shared_task
def load_initiative(initiative_id):
    """Celery task to reload a initiative in search."""
    load_initiatives(initiative_id)


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

    load_initiatives()


def load_initiatives(initiative_id=None):
    """Load a group of initiatives to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    initiatives = (
        Initiatives.objects.select_related("ops_owner")
        .select_related("exec_owner")
        .select_related("financial_impact")
        .select_related("strategic_importance")
        .select_related("modified_by")
        .prefetch_related("projects__term_annotations")
        .prefetch_related("projects__term_annotations__term")
        .prefetch_related("projects__report_annotations")
        .prefetch_related("projects__report_annotations__report")
        .prefetch_related("projects__report_annotations__report__docs")
    )

    if initiative_id:
        initiatives = initiatives.filter(initiative_id=initiative_id)

    for initiative_batch in batch_iterator(initiatives, batch_size=1000):
        # reset the batch. reports will be loaded to solr in batches
        # of "batch_size"
        process_initiative_batch(initiative_batch)


def process_initiative_batch(initiative_batch):
    """Process a batch load."""
    docs = []

    for initiative in initiative_batch:

        docs.append(build_doc(initiative))

    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(docs)


def build_doc(initiative):
    """Build initiative doc."""
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
        "last_updated": solr_date(initiative._modified_at),
        "updated_by": str(initiative.modified_by),
        "related_projects": [],
        "linked_description": [],
        "related_terms": [],
        "related_reports": [],
        "linked_name": [],
    }

    for project in initiative.projects.all():
        doc = build_initiative_project_doc(project, doc)

    for report_annotation in project.report_annotations.all():
        doc = build_initiative_report_doc(report_annotation, doc)

    return clean_doc(doc)


def build_initiative_project_doc(project, doc):
    """Build initiative project doc."""
    doc["related_projects"].append(str(project))
    doc["linked_description"].extend([project.purpose, project.description])

    for term_annotation in project.term_annotations.all():
        doc["related_terms"].append(str(term_annotation.term))
        doc["linked_description"].extend(
            [
                term_annotation.term.summary,
                term_annotation.term.technical_definition,
                term_annotation.annotation,
            ]
        )

    return doc


def build_initiative_report_doc(report_annotation, doc):
    """Build initiative report doc."""
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

    return doc
