"""Celery tasks to keep collection search up to date."""
# pylint: disable=W0613
import contextlib
from typing import Any, Dict, Iterator, Optional

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import CollectionReports, Collections, CollectionTerms


@receiver(pre_delete, sender=Collections)
def deleted_collection(
    sender: Collections, instance: Collections, **kwargs: Dict[Any, Any]
) -> None:
    """When collection is delete, remove it from search."""
    delete_collection.delay(instance.collection_id)


@receiver(post_save, sender=Collections)
def updated_collection(
    sender: Collections, instance: Collections, **kwargs: Dict[Any, Any]
) -> None:
    """When collection is updated, add it to search."""
    if instance.hidden == "Y":
        delete_collection.delay(instance.collection_id)
    else:
        load_collection.delay(instance.collection_id)


@shared_task
def delete_collection(collection_id: int) -> None:
    """Celery task to remove a collection from search."""
    delete_collection_function(collection_id)


def delete_collection_function(collection_id: int) -> None:
    """In process delete function."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q=f"type:collections AND atlas_id:{collection_id}")


@shared_task
def load_collection(collection_id: int) -> None:
    """Celery task to reload a collection in search."""
    load_collections(collection_id)


@shared_task
def reset_collections() -> None:
    """Reset collection group in solr.

    1. Delete all collections from Solr
    2. Query all existing collections
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:collections")
    solr.optimize()

    load_collections()


def load_collections(collection_id: Optional[int] = None) -> None:
    """Load a group of collections to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    collections = (
        Collections.objects.filter(~Q(hidden="Y") | Q(hidden=None))
        .select_related("modified_by")
        .select_related("initiative")
        .prefetch_related("terms")
        .prefetch_related("terms__term")
        .prefetch_related("reports")
        .prefetch_related("reports__report")
        .prefetch_related("reports__report__docs")
    )

    if collection_id:
        collections = collections.filter(collection_id=collection_id)

    if len(collections) == 0 and collection_id:
        delete_collection_function(collection_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(collections.all(), batch_size=1000)))


def solr_load_batch(batch: Iterator) -> None:
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(collection: Collections) -> Dict[Any, Any]:
    """Build a collection doc."""
    doc = {
        "id": "/collections/%s" % collection.collection_id,
        "atlas_id": collection.collection_id,
        "type": "collections",
        "name": str(collection),
        "visible": "Y",
        "orphan": "N",
        "runs": 10,
        "description": [collection.search_summary, collection.description],
        "last_updated": solr_date(collection.modified_at),
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

    for term_link in collection.terms.all():
        doc = build_collection_term_doc(term_link, doc)

    for report_link in collection.reports.all():
        doc = build_collection_report_doc(report_link, doc)

    return clean_doc(doc)


def build_collection_term_doc(
    term_link: CollectionTerms, doc: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Build collection term doc."""
    doc["related_terms"].append(str(term_link.term))
    doc["linked_description"].extend(
        [
            term_link.term.summary,
            term_link.term.technical_definition,
        ]
    )

    return doc


def build_collection_report_doc(
    report_link: CollectionReports, doc: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Build collection report doc."""
    doc["related_reports"].append(str(report_link.report))

    doc["linked_name"].extend([report_link.report.name, report_link.report.title])

    doc["linked_description"].extend(
        [
            report_link.report.description,
            report_link.report.detailed_description,
        ]
    )

    with contextlib.suppress(AttributeError):
        doc["linked_description"].extend(
            [
                report_link.report.docs.description,
                report_link.report.docs.assumptions,
            ]
        )
    return doc
