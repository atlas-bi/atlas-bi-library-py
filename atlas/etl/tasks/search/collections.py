"""Celery tasks to keep collection search up to date."""
import contextlib

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import Collections


@receiver(pre_delete, sender=Collections)
def deleted_collection(sender, instance, **kwargs):
    """When collection is delete, remove it from search."""
    delete_collection.delay(instance.collection_id)


@receiver(post_save, sender=Collections)
def updated_collection(sender, instance, **kwargs):
    """When collection is updated, add it to search."""
    if instance.hidden == "Y":
        delete_collection.delay(instance.collection_id)
    else:
        load_collection.delay(instance.collection_id)


@shared_task
def delete_collection(collection_id):
    """Celery task to remove a collection from search."""
    delete_collection_function(collection_id)


def delete_collection_function(collection_id):
    """In process delete function."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:collections AND atlas_id:%s" % collection_id)


@shared_task
def load_collection(collection_id):
    """Celery task to reload a collection in search."""
    load_collections(collection_id)


@shared_task
def reset_collections():
    """Reset collection group in solr.

    1. Delete all collections from Solr
    2. Query all existing collections
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:collections")
    solr.optimize()

    load_collections()


def load_collections(collection_id=None):
    """Load a group of collections to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    collections = (
        Collections.objects.exclude(hidden="Y")
        .select_related("ops_owner")
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
    )

    if collection_id:
        collections = collections.filter(collection_id=collection_id)

    if len(collections) == 0:
        delete_collection_function(collection_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(collections.all(), batch_size=1000)))


def solr_load_batch(batch):
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(collection):
    """Build a collection doc."""
    doc = {
        "id": "/collections/%s" % collection.collection_id,
        "atlas_id": collection.collection_id,
        "type": "collections",
        "name": str(collection),
        "visible": "Y",
        "orphan": "N",
        "runs": 10,
        "description": [collection.purpose, collection.description],
        "operations_owner": str(collection.ops_owner),
        "executive_owner": str(collection.exec_owner),
        "analytics_owner": str(collection.analytics_owner),
        "data_owner": str(collection.data_owner),
        "financial_impact": str(collection.financial_impact),
        "strategic_importance": str(collection.strategic_importance),
        "external_url": collection.external_documentation_url,
        "last_updated": solr_date(collection._modified_at),
        "updated_by": str(collection.modified_by),
        "related_initiatives": [],
        "related_terms": [],
        "related_reports": [],
        "linked_name": [],
        "linked_description": [],
    }

    with contextlib.suppress(AttributeError):
        doc["related_initiatives"].append(str(collection.initiative))
        doc["linked_description"].append(collection.initiative.description)

    for term_annotation in collection.term_annotations.all():
        doc = build_collection_term_doc(term_annotation, doc)

    for report_annotation in collection.report_annotations.all():
        doc = build_collection_report_doc(report_annotation, doc)

    return clean_doc(doc)


def build_collection_term_doc(term_annotation, doc):
    """Build collection term doc."""
    doc["related_terms"].append(str(term_annotation.term))
    doc["linked_description"].extend(
        [
            term_annotation.term.summary,
            term_annotation.term.technical_definition,
            term_annotation.annotation,
        ]
    )

    return doc


def build_collection_report_doc(report_annotation, doc):
    """Build collection report doc."""
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

    with contextlib.suppress(AttributeError):
        doc["linked_description"].extend(
            [
                report_annotation.report.docs.description,
                report_annotation.report.docs.assumptions,
            ]
        )
    return doc
