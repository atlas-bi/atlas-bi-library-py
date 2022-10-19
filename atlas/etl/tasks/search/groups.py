"""Celery tasks to keep group search up to date."""
# disable qa until fixing group reload.
# flake8: noqa
from typing import Any, Dict, Iterator, Optional

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc
from index.models import Groups

# this is somehow causing an endless loop when logging in?!
# @receiver(post_save, sender=Users)
# def updated_group(sender, instance, **kwargs):
#     """When group is updated, add it to search."""
#     load_group.delay(instance.group_id)


@shared_task
def delete_group(group_id: int) -> None:
    """Celery task to remove a group from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:groups AND atlas_id:%s" % group_id)


@shared_task
def load_group(group_id: int) -> None:
    """Celery task to reload a group in search."""
    load_groups(group_id)


@shared_task
def reset_groups() -> None:
    """Reset group group in solr.

    1. Delete all groups from Solr
    2. Query all existing groups
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:groups")
    solr.optimize()

    load_groups()


def load_groups(group_id: Optional[int] = None) -> None:
    """Load a group of groups to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    groups = Groups.objects

    if group_id:
        groups = groups.filter(group_id=group_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(groups.all(), batch_size=1000)))


def solr_load_batch(batch: Iterator) -> None:
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(group: Groups) -> Dict[Any, Any]:
    """Build group doc."""
    doc = {
        "id": "/groups/%s" % group.group_id,
        "atlas_id": group.group_id,
        "type": "groups",
        "name": str(group),
        "group_roles": [role[0] for role in group.get_roles()],
        "visible": "Y",
        "orphan": "N",
        "runs": 10,
    }

    return clean_doc(doc)
