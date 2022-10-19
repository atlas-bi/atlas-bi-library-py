"""Celery tasks to keep initiative search up to date."""
# pylint: disable=W0613
import contextlib
from typing import Any, Dict, Iterator, Optional

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import CollectionReports, Collections, Initiatives


@receiver(pre_delete, sender=Initiatives)
def deleted_initiative(
    sender: Initiatives, instance: Initiatives, **kwargs: Dict[Any, Any]
) -> None:
    """When initiative is delete, remove it from search."""
    delete_initiative.delay(instance.initiative_id)


@receiver(post_save, sender=Initiatives)
def updated_initiative(
    sender: Initiatives, instance: Initiatives, **kwargs: Dict[Any, Any]
) -> None:
    """When initiative is updated, add it to search."""
    load_initiative.delay(instance.initiative_id)


@shared_task
def delete_initiative(initiative_id: int) -> None:
    """Celery task to remove a initiative from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:initiatives AND atlas_id:%s" % initiative_id)


@shared_task
def load_initiative(initiative_id: int) -> None:
    """Celery task to reload a initiative in search."""
    load_initiatives(initiative_id)


@shared_task
def reset_initiatives() -> None:
    """Reset initiative group in solr.

    1. Delete all initiatives from Solr
    2. Query all existing initiatives
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:initiatives")
    solr.optimize()

    load_initiatives()


def load_initiatives(initiative_id: Optional[int] = None) -> None:
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
        .prefetch_related("collections__terms")
        .prefetch_related("collections__terms__term")
        .prefetch_related("collections__reports")
        .prefetch_related("collections__reports__report")
        .prefetch_related("collections__reports__report__docs")
    )

    if initiative_id:
        initiatives = initiatives.filter(initiative_id=initiative_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(initiatives.all(), batch_size=1000)))


def solr_load_batch(batch: Iterator) -> None:
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(initiative: Initiatives) -> Dict[Any, Any]:
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
        "last_updated": solr_date(initiative.modified_at),
        "updated_by": str(initiative.modified_by),
        "related_collections": [],
        "linked_description": [],
        "related_terms": [],
        "related_reports": [],
        "linked_name": [],
    }

    for collection in initiative.collections.all():
        doc = build_initiative_collection_doc(collection, doc)

    return clean_doc(doc)


def build_initiative_collection_doc(
    collection: Collections, doc: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Build initiative collection doc."""
    doc["related_collections"].append(str(collection))
    doc["linked_description"].extend(
        [collection.search_summary, collection.description]
    )

    for term_link in collection.terms.all():
        doc["related_terms"].append(str(term_link.term))
        doc["linked_description"].extend(
            [
                term_link.term.summary,
                term_link.term.technical_definition,
            ]
        )

    for report_link in collection.reports.all():
        doc = build_initiative_report_doc(report_link, doc)

    return doc


def build_initiative_report_doc(
    report_link: CollectionReports, doc: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Build initiative report doc."""
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
