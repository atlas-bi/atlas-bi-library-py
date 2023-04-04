"""Celery tasks to keep lookup values up to date."""
# pylint: disable=W0613
from typing import Any, Dict

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from index.models import (
    FinancialImpact,
    Fragility,
    FragilityTag,
    MaintenanceLogStatus,
    MaintenanceSchedule,
    OrganizationalValue,
    RunFrequency,
    StrategicImportance,
    UserRoles,
)


@receiver(pre_delete, sender=FinancialImpact)
def deleted_financial_impact(
    sender: FinancialImpact, instance: FinancialImpact, **kwargs: Dict[Any, Any]
) -> None:
    """When financial_impac is delete, remove it from search."""
    delete_lookup.delay("financial_impact", instance.impact_id)


@receiver(post_save, sender=FinancialImpact)
def updated_financial_impact(
    sender: FinancialImpact, instance: FinancialImpact, **kwargs: Dict[Any, Any]
) -> None:
    """When financial_impac is updated, add it to search."""
    load_lookup.delay("financial_impact", instance.impact_id, str(instance))


@receiver(pre_delete, sender=RunFrequency)
def deleted_run_frequency(
    sender: RunFrequency, instance: RunFrequency, **kwargs: Dict[Any, Any]
) -> None:
    """When financial_impac is delete, remove it from search."""
    delete_lookup.delay("run_frequency", instance.frequency_id)


@receiver(post_save, sender=RunFrequency)
def updated_run_frequency(
    sender: RunFrequency, instance: RunFrequency, **kwargs: Dict[Any, Any]
) -> None:
    """When financial_impac is updated, add it to search."""
    load_lookup.delay("run_frequency", instance.frequency_id, str(instance))


@receiver(pre_delete, sender=OrganizationalValue)
def deleted_organizational_value(
    sender: OrganizationalValue, instance: OrganizationalValue, **kwargs: Dict[Any, Any]
) -> None:
    """When organizational_value is delete, remove it from search."""
    delete_lookup.delay("organizational_value", instance.value_id)


@receiver(post_save, sender=OrganizationalValue)
def updated_organizational_value(
    sender: OrganizationalValue, instance: OrganizationalValue, **kwargs: Dict[Any, Any]
) -> None:
    """When organizational_value is updated, add it to search."""
    load_lookup.delay("organizational_value", instance.value_id, str(instance))


@receiver(pre_delete, sender=Fragility)
def deleted_fragility(
    sender: Fragility, instance: Fragility, **kwargs: Dict[Any, Any]
) -> None:
    """When fragility is delete, remove it from search."""
    delete_lookup.delay("fragility", instance.fragility_id)


@receiver(post_save, sender=Fragility)
def updated_fragility(
    sender: Fragility, instance: Fragility, **kwargs: Dict[Any, Any]
) -> None:
    """When fragility is updated, add it to search."""
    load_lookup.delay("fragility", instance.fragility_id, str(instance))


@receiver(pre_delete, sender=MaintenanceSchedule)
def deleted_maintenance_schedule(
    sender: MaintenanceSchedule, instance: MaintenanceSchedule, **kwargs: Dict[Any, Any]
) -> None:
    """When maintenance_schedule is delete, remove it from search."""
    delete_lookup.delay("maintenance_schedule", instance.schedule_id)


@receiver(post_save, sender=MaintenanceSchedule)
def updated_maintenance_schedule(
    sender: MaintenanceSchedule, instance: MaintenanceSchedule, **kwargs: Dict[Any, Any]
) -> None:
    """When maintenance_schedule is updated, add it to search."""
    load_lookup.delay("maintenance_schedule", instance.schedule_id, str(instance))


@receiver(pre_delete, sender=FragilityTag)
def deleted_fragility_tag(
    sender: FragilityTag, instance: FragilityTag, **kwargs: Dict[Any, Any]
) -> None:
    """When fragility_tag is delete, remove it from search."""
    delete_lookup.delay("fragility_tag", instance.tag_id)


@receiver(post_save, sender=FragilityTag)
def updated_fragility_tag(
    sender: FragilityTag, instance: FragilityTag, **kwargs: Dict[Any, Any]
) -> None:
    """When fragility_tag is updated, add it to search."""
    load_lookup.delay("fragility_tag", instance.tag_id, str(instance))


@receiver(pre_delete, sender=MaintenanceLogStatus)
def deleted_maintenance_log_status(
    sender: MaintenanceLogStatus,
    instance: MaintenanceLogStatus,
    **kwargs: Dict[Any, Any],
) -> None:
    """When maintenance_log_status is delete, remove it from search."""
    delete_lookup.delay("maintenance_log_status", instance.status_id)


@receiver(post_save, sender=MaintenanceLogStatus)
def updated_maintenance_log_status(
    sender: MaintenanceLogStatus,
    instance: MaintenanceLogStatus,
    **kwargs: Dict[Any, Any],
) -> None:
    """When maintenance_log_status is updated, add it to search."""
    load_lookup.delay("maintenance_log_status", instance.status_id, str(instance))


@receiver(pre_delete, sender=UserRoles)
def deleted_user_roles(
    sender: UserRoles, instance: UserRoles, **kwargs: Dict[Any, Any]
) -> None:
    """When user_roles is delete, remove it from search."""
    delete_lookup.delay("user_roles", instance.role_id)


@receiver(post_save, sender=UserRoles)
def updated_user_roles(
    sender: UserRoles, instance: UserRoles, **kwargs: Dict[Any, Any]
) -> None:
    """When user_roles is updated, add it to search."""
    load_lookup.delay("user_roles", instance.role_id, str(instance))


@receiver(pre_delete, sender=StrategicImportance)
def deleted_strategic_importance(
    sender: StrategicImportance, instance: StrategicImportance, **kwargs: Dict[Any, Any]
) -> None:
    """When strategic_importance is delete, remove it from search."""
    delete_lookup.delay("strategic_importance", instance.importance_id)


@receiver(post_save, sender=StrategicImportance)
def updated_strategic_importance(
    sender: StrategicImportance, instance: StrategicImportance, **kwargs: Dict[Any, Any]
) -> None:
    """When strategic_importance is updated, add it to search."""
    load_lookup.delay("strategic_importance", instance.importance_id, str(instance))


@shared_task
def delete_lookup(item_type: str, item_id: int, **kwargs: Dict[Any, Any]) -> None:
    """Celery task to remove a initiative from search."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL, always_commit=True)

    solr.delete(q=f"id:{item_type}_{item_id}")


@shared_task
def load_lookup(item_type: str, item_id: int, item_name: str) -> None:
    """Celery task to reload a lookup in search."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL, always_commit=True)
    solr.add(
        [
            {
                "id": f"{item_type}_{item_id}",
                "item_type": item_type,
                "item_name": item_name,
                "atlas_id": item_id,
            }
        ]
    )


@shared_task
def reset_lookups() -> None:
    """Reset all lookups."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL, always_commit=True)
    solr.delete(q="*:*")
    solr.optimize()

    docs = [
        {
            "id": "financial_impact_" + str(value.impact_id),
            "item_type": "financial_impact",
            "item_name": value.name,
            "atlas_id": value.impact_id,
        }
        for value in FinancialImpact.objects.all()
    ]
    docs.extend(
        [
            {
                "id": "fragility_" + str(value.fragility_id),
                "item_type": "fragility",
                "item_name": value.name,
                "atlas_id": value.fragility_id,
            }
            for value in Fragility.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "fragility_tag_" + str(value.tag_id),
                "item_type": "fragility_tag",
                "item_name": value.name,
                "atlas_id": value.tag_id,
            }
            for value in FragilityTag.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "maintenance_log_status_" + str(value.status_id),
                "item_type": "maintenance_log_status",
                "item_name": value.name,
                "atlas_id": value.status_id,
            }
            for value in MaintenanceLogStatus.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "maintenance_schedule_" + str(value.schedule_id),
                "item_type": "maintenance_schedule",
                "item_name": value.name,
                "atlas_id": value.schedule_id,
            }
            for value in MaintenanceSchedule.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "organizational_value_" + str(value.value_id),
                "item_type": "organizational_value",
                "item_name": value.name,
                "atlas_id": value.value_id,
            }
            for value in OrganizationalValue.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "run_frequency" + str(value.frequency_id),
                "item_type": "run_frequency",
                "item_name": value.name,
                "atlas_id": value.frequency_id,
            }
            for value in RunFrequency.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "strategic_importance_" + str(value.importance_id),
                "item_type": "strategic_importance",
                "item_name": value.name,
                "atlas_id": value.importance_id,
            }
            for value in StrategicImportance.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "user_roles_" + str(value.role_id),
                "item_type": "user_roles",
                "item_name": value.name,
                "atlas_id": value.role_id,
            }
            for value in UserRoles.objects.all()
        ]
    )

    solr.add(docs)
