"""Atlas ETL for Search."""
import json
from datetime import datetime

import pysolr
import pytz
from django.conf import settings
from django.http import HttpResponse
from index.models import Initiatives


def index(request):
    """Test solr connections."""

    # will clear all and re-add
    reset_initiatives()

    return HttpResponse("ok")
    #        print(docs)

    ## daily drop and recreate
    ## after ETL/db changes trigger an update.

    ## if the report is changed to "exclude" from search, or becomes an orphan,
    # make sure it is removed from the search index.

    # after removing all records
    # solr.optimize()

    # 1 remove old report records from solr
    # reports
    # initiatives
    # projects
    # terms
    # users

    # for report_type in ['reports','initiatives','projects','terms','users']:
    #     print(report_type)
    #     print(solr.search(
    #         "*:*",
    #         fq="type:%s" % report_type,
    #         fl="atlas_id",
    #         start = 0,
    #         rows=0).hits)

    return HttpResponse("<body></body>")


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


def chunker(seq, size):
    """Split big list into parts.

    https://stackoverflow.com/a/434328/10265880
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))
