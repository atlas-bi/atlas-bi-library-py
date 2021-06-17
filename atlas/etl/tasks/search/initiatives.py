"""Celery tasks to keep initiative search up to date."""
from datetime import datetime

import pysolr
import pytz
from celery import shared_task
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from index.models import Initiatives

from ..functions import chunker


@receiver(post_delete, sender=Initiatives)
def deleted_initiative(sender, **kwargs):
    """When initiative is delete, remove it from search."""
    print(sender, **kwargs)


@receiver(post_save, sender=Initiatives)
def updated_initiative(sender, **kwargs):
    """When initiative is updated, add it to search."""
    print(sender, **kwargs)


@shared_task
def reset_initiatives():
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)

    # daily delete all
    # solr.delete(q='*:*')
    # solr.optimize()

    solr.delete(q="type:initiatives")
    initiatives = (
        Initiatives.objects.select_related("ops_owner")
        .select_related("exec_owner")
        .select_related("financial_impact")
        .select_related("strategic_importance")
        .select_related("modified_by")
        .prefetch_related("projects__terms")
        .prefetch_related("projects__terms__term")
        .prefetch_related("projects__reports")
        .prefetch_related("projects__reports__report")
        .prefetch_related("projects__reports__report__docs")
        .all()
    )

    load_initiatives(initiatives)


def load_initiatives(initiatives):
    solr = pysolr.Solr(settings.SOLR_URL, always_commit=True)
    docs = []

    for initiative in initiatives:
        doc = {
            "id": "/initiatives/%s" % initiative.initiative_id,
            "atlas_id": initiative.initiative_id,
            "type": "initiatives",
            "name": str(initiative),
            "visible": "Y",
            "orphan": "N",
            "runs": 10,
        }
        if initiative.ops_owner:
            doc["operations_owner"] = str(initiative.ops_owner)
        if initiative.description:
            doc["description"] = initiative.description
        if initiative.exec_owner:
            doc["executive_owner"] = str(initiative.exec_owner)
        if initiative.financial_impact:
            doc["financial_impact"] = str(initiative.financial_impact)
        if initiative.strategic_importance:
            doc["strategic_importance"] = str(initiative.strategic_importance)
        if initiative.modified_at:
            doc["last_updated"] = datetime.strftime(
                initiative._modified_at.astimezone(pytz.utc), "%Y-%m-%dT%H:%M:%SZ"
            )
        if initiative.modified_by:
            doc["updated_by"] = str(initiative.modified_by)

        if initiative.projects.exists():
            doc["related_projects"] = []
            doc["linked_description"] = []
            for project in initiative.projects.all():

                doc["related_projects"].append(str(project))
                doc["linked_description"].append(
                    (project.purpose or "") + "\n" + (project.description or "")
                )
                if project.terms.exists():
                    if "related_terms" not in doc:
                        doc["related_terms"] = []
                    for term in project.terms.all():
                        doc["related_terms"].append(str(term.term))
                        doc["linked_description"].append(
                            (term.term.summary or "")
                            + "\n"
                            + (term.term.technical_definition or "")
                            + "\n"
                            + (term.annotation or "")
                        )

                if project.reports.exists():
                    if "related_reports" not in doc:
                        doc["related_reports"] = []

                    for report in project.reports.all():

                        doc["related_reports"].append(str(report.report))

                        if "linked_name" not in doc:
                            doc["linked_name"] = []

                        doc["linked_name"].append(report.report.name)
                        doc["linked_name"].append(report.report.title)

                        doc["linked_description"].append(
                            (report.report.description or "")
                            + "\n"
                            + (report.report.detailed_description or "")
                            + (
                                (report.report.docs.description or "") + "\n"
                                if report.report.has_docs()
                                else ""
                            )
                            + (
                                (report.report.docs.assumptions or "") + "\n"
                                if report.report.has_docs()
                                else ""
                            )
                        )

        docs.append(doc)
    # load the results in batches of 1k.
    for doc in chunker(docs, 1):
        print("loading")
        solr.add(doc)
