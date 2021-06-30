"""Celery tasks to keep lookup values up to date."""
import contextlib

import pysolr
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_chunked_iterator import batch_iterator
from etl.tasks.functions import clean_doc, solr_date
from index.models import (
    FinancialImpact,
    Fragility,
    FragilityTag,
    InitiativeContacts,
    MaintenanceLogStatus,
    MaintenanceSchedule,
    OrganizationalValue,
    ProjectMilestoneFrequency,
    ProjectMilestoneTemplates,
    Projects,
    RunFrequency,
    StrategicImportance,
    UserRoles,
)


@receiver(pre_delete, sender=FinancialImpact)
def deleted_financial_impact(sender, instance, **kwargs):
    """When financial_impac is delete, remove it from search."""
    delete_lookup.delay("financial_impact", instance.impact_id)


@receiver(post_save, sender=FinancialImpact)
def updated_financial_impact(sender, instance, **kwargs):
    """When financial_impac is updated, add it to search."""
    load_lookup.delay("financial_impact", instance.impact_id, str(instance))


@receiver(pre_delete, sender=RunFrequency)
def deleted_financial_impact(sender, instance, **kwargs):
    """When financial_impac is delete, remove it from search."""
    delete_lookup.delay("run_frequency", instance.frequency_id)


@receiver(post_save, sender=RunFrequency)
def updated_financial_impact(sender, instance, **kwargs):
    """When financial_impac is updated, add it to search."""
    load_lookup.delay("run_frequency", instance.frequency_id, str(instance))


@receiver(pre_delete, sender=OrganizationalValue)
def deleted_organizational_value(sender, instance, **kwargs):
    """When organizational_value is delete, remove it from search."""
    delete_lookup.delay("organizational_value", instance.value_id)


@receiver(post_save, sender=OrganizationalValue)
def updated_organizational_value(sender, instance, **kwargs):
    """When organizational_value is updated, add it to search."""
    load_lookup.delay("organizational_value", instance.value_id, str(instance))


@receiver(pre_delete, sender=Fragility)
def deleted_fragility(sender, instance, **kwargs):
    """When fragility is delete, remove it from search."""
    delete_lookup.delay("fragility", instance.fragility_id)


@receiver(post_save, sender=Fragility)
def updated_fragility(sender, instance, **kwargs):
    """When fragility is updated, add it to search."""
    load_lookup.delay("fragility", instance.fragility_id, str(instance))


@receiver(pre_delete, sender=MaintenanceSchedule)
def deleted_maintenance_schedule(sender, instance, **kwargs):
    """When maintenance_schedule is delete, remove it from search."""
    delete_lookup.delay("maintenance_schedule", instance.schedule_id)


@receiver(post_save, sender=MaintenanceSchedule)
def updated_maintenance_schedule(sender, instance, **kwargs):
    """When maintenance_schedule is updated, add it to search."""
    load_lookup.delay("maintenance_schedule", instance.schedule_id, str(instance))


@receiver(pre_delete, sender=FragilityTag)
def deleted_fragility_tag(sender, instance, **kwargs):
    """When fragility_tag is delete, remove it from search."""
    delete_lookup.delay("fragility_tag", instance.tag_id)


@receiver(post_save, sender=FragilityTag)
def updated_fragility_tag(sender, instance, **kwargs):
    """When fragility_tag is updated, add it to search."""
    load_lookup.delay("fragility_tag", instance.tag_id, str(instance))


@receiver(pre_delete, sender=MaintenanceLogStatus)
def deleted_maintenance_log_status(sender, instance, **kwargs):
    """When maintenance_log_status is delete, remove it from search."""
    delete_lookup.delay("maintenance_log_status", instance.status_id)


@receiver(post_save, sender=MaintenanceLogStatus)
def updated_maintenance_log_status(sender, instance, **kwargs):
    """When maintenance_log_status is updated, add it to search."""
    load_lookup.delay("maintenance_log_status", instance.status_id, str(instance))


@receiver(pre_delete, sender=InitiativeContacts)
def deleted_initiative_contacts(sender, instance, **kwargs):
    """When initiative_contacts is delete, remove it from search."""
    delete_lookup.delay("initiative_contacts", instance.contact_id)


@receiver(post_save, sender=InitiativeContacts)
def updated_initiative_contacts(sender, instance, **kwargs):
    """When initiative_contacts is updated, add it to search."""
    load_lookup.delay("initiative_contacts", instance.contact_id, str(instance))


@receiver(pre_delete, sender=ProjectMilestoneFrequency)
def deleted_project_milestone_frequency(sender, instance, **kwargs):
    """When project_milestone_frequency is delete, remove it from search."""
    delete_lookup.delay("project_milestone_frequency", instance.frequency_id)


@receiver(post_save, sender=ProjectMilestoneFrequency)
def updated_project_milestone_frequency(sender, instance, **kwargs):
    """When project_milestone_frequency is updated, add it to search."""
    load_lookup.delay(
        "project_milestone_frequency", instance.frequency_id, str(instance)
    )


@receiver(pre_delete, sender=ProjectMilestoneTemplates)
def deleted_project_milestone_templates(sender, instance, **kwargs):
    """When project_milestone_templates is delete, remove it from search."""
    delete_lookup.delay("project_milestone_templates", instance.template_id)


@receiver(post_save, sender=ProjectMilestoneTemplates)
def updated_project_milestone_templates(sender, instance, **kwargs):
    """When project_milestone_templates is updated, add it to search."""
    load_lookup.delay(
        "project_milestone_templates", instance.template_id, str(instance)
    )


@receiver(pre_delete, sender=UserRoles)
def deleted_user_roles(sender, instance, **kwargs):
    """When user_roles is delete, remove it from search."""
    delete_lookup.delay("user_roles", instance.role_id)


@receiver(post_save, sender=UserRoles)
def updated_user_roles(sender, instance, **kwargs):
    """When user_roles is updated, add it to search."""
    load_lookup.delay("user_roles", instance.role_id, str(instance))


@receiver(pre_delete, sender=StrategicImportance)
def deleted_strategic_importance(sender, instance, **kwargs):
    """When strategic_importance is delete, remove it from search."""
    delete_lookup.delay("strategic_importance", instance.importance_id)


@receiver(post_save, sender=StrategicImportance)
def updated_strategic_importance(sender, instance, **kwargs):
    """When strategic_importance is updated, add it to search."""
    load_lookup.delay("strategic_importance", instance.importance_id, str(instance))


@shared_task
def delete_lookup(item_type, item_id, **kwargs):
    """Celery task to remove a initiative from search."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL, always_commit=True)

    solr.delete(
        q="id:%s_%s"
        % (
            item_type,
            str(item_id),
        )
    )


@shared_task
def load_lookup(item_type, item_id, item_name):
    """Celery task to reload a lookup in search."""
    solr = pysolr.Solr(settings.SOLR_LOOKUP_URL, always_commit=True)
    solr.add(
        [
            {
                "id": "%s_%s"
                % (
                    item_type,
                    str(item_id),
                ),
                "item_type": item_type,
                "item_name": item_name,
                "atlas_id": item_id,
            }
        ]
    )


@shared_task
def reset_lookups():
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
                "id": "initiative_contacts_" + str(value.contact_id),
                "item_type": "initiative_contacts",
                "item_name": value.name,
                "atlas_id": value.contact_id,
            }
            for value in InitiativeContacts.objects.all()
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
                "id": "project_milestone_frequency_" + str(value.frequency_id),
                "item_type": "project_milestone_frequency",
                "item_name": value.name,
                "atlas_id": value.frequency_id,
            }
            for value in ProjectMilestoneFrequency.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "project_milestone_templates_" + str(value.template_id),
                "item_type": "project_milestone_templates",
                "item_name": value.name,
                "atlas_id": value.template_id,
            }
            for value in ProjectMilestoneTemplates.objects.all()
        ]
    )
    docs.extend(
        [
            {
                "id": "frequency_id_" + str(value.frequency_id),
                "item_type": "frequency_id",
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
