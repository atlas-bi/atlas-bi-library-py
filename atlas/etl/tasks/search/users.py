"""Celery tasks to keep user search up to date."""
# disable qa until fixing user reload.
# flake8: noqa
from typing import Any, Dict, Iterator, Optional

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc
from index.models import Users

# this is somehow causing an endless loop when logging in?!
# @receiver(post_save, sender=Users)
# def updated_user(sender, instance, **kwargs):
#     """When user is updated, add it to search."""
#     load_user.delay(instance.user_id)


@shared_task
def delete_user(user_id: int) -> None:
    """Celery task to remove a user from search."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q=f"type:users AND atlas_id:{user_id}")


@shared_task
def load_user(user_id: int) -> None:
    """Celery task to reload a user in search."""
    load_users(user_id)


@shared_task
def reset_users() -> None:
    """Reset user group in solr.

    1. Delete all users from Solr
    2. Query all existing users
    3. Load data to solr.
    """
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.delete(q="type:users")
    solr.optimize()

    load_users()


def load_users(user_id: Optional[int] = None) -> None:
    """Load a group of users to solr database.

    1. Convert the objects to list of dicts
    2. Bulk load to solr in batchs of x
    """
    users = Users.objects

    if user_id:
        users = users.filter(user_id=user_id)

    # reset the batch. reports will be loaded to solr in batches
    # of "batch_size"
    list(map(solr_load_batch, batch_iterator(users.all(), batch_size=1000)))


def solr_load_batch(batch: Iterator) -> None:
    """Process batch."""
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    solr.add(list(map(build_doc, batch)))


def build_doc(user: Users) -> Dict[Any, Any]:
    """Build user doc."""
    doc = {
        "id": f"/users/{user.user_id}",
        "atlas_id": user.user_id,
        "type": "users",
        "name": str(user),
        "employee_id": user.employee_id,
        "email": user.email,
        "epic_record_id": user.system_id,
        "user_roles": [role[0] for role in user.get_roles()],
        "visible": "Y",
        "orphan": "N",
        "runs": 10,
    }

    return clean_doc(doc)
