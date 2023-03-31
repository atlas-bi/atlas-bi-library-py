"""Custom template tag to render markdown."""
# pylint: disable=R0911, R0912
import re
from typing import Any, Dict, Optional, Union

from django import template
from django.http import HttpRequest
from django.urls import reverse
from index.models import ReportAttachments, Reports

register = template.Library()


def run_authorization(report: Reports, request: HttpRequest) -> bool:
    """User authorization for Crystal Report & Reporting Workbench reports."""
    if report.type.name not in ["Epic-Crystal Report", "Reporting Workbench Report"]:
        return True

    user_groups = request.user.get_group_ids
    report_groups = report.get_group_ids

    # check hrx
    if set(report_groups) < set(user_groups):
        return True

    # check hrg
    return any(
        set(parent_report.get_group_ids) < set(user_groups)
        for parent_report in Reports.objects.filter(
            parent__child=report.report_id
        ).all()
    )


@register.simple_tag(takes_context=True)
def attachment_url(context: Dict[Any, Any], attachment: ReportAttachments) -> str:
    """Build a url to open a file attachment."""
    if context["is_hyperspace"]:
        return (
            "EpicAct:AC_RW_WEB_BROWSER,LaunchOptions:2,runparams:"
            + context.request.build_absolute_uri(  # type: ignore[attr-defined]
                reverse("report:attachment", kwargs={"pk": attachment.attachment_id})
            )
            + f"|FormCaption={attachment.name}|ActivityName={attachment.name}"
        )

    return context.request.build_absolute_uri(  # type: ignore[attr-defined]
        reverse("report:attachment", kwargs={"pk": attachment.attachment_id})
    )


@register.simple_tag(takes_context=True)
def viewer_url(context: Dict[Any, Any], report: Reports) -> Optional[str]:
    """Build a url to open a file attachment."""
    if context["is_hyperspace"] and report.system_id and report.system_identifier:
        return f"EpicAct:AR_RECORD_VIEWER,runparams:{report.system_identifier}|{report.system_id}"
    return None


@register.simple_tag(takes_context=True)
def run_url(context: Dict[Any, Any], report: Reports) -> Optional[Union[bool, str]]:
    """Build a report run url.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    if not run_authorization(report, context.request):  # type: ignore[attr-defined]
        return False

    if report.orphan == "Y":
        return False

    if report.name is None:
        return False

    nice_name = re.sub(r"[|=]", " ", report.name)

    enabled_for_hyperspace = bool(
        report.docs.enabled_for_hyperspace if report.has_docs() else False  # type: ignore[no-untyped-call]
    )

    if (
        report.system_run_url
        or (
            report.type.name
            not in ["SSRS Report", "SSRS File", "Source Radar Dashboard Component"]
            and context["is_hyperspace"]
        )
    ) and report.type.name not in ["Epic-Crystal Report", "Crystal Report"]:
        if (
            report.system_identifier == "HRX"
            and report.type.name != "SlicerDicer Session"
        ):
            return f"EpicAct:AC_RW_STATUS,RUNPARAMS:{report.system_template_id}|{report.system_id}"

        if report.system_identifier == "HGR":
            return f"EpicAct:AC_RW_STATUS,RUNPARAMS:{report.system_template_id}"

        if report.system_identifier == "IDM":
            return f"EpicAct:WM_DASHBOARD_LAUNCHER,runparams:{report.system_id}"

        if (
            report.type.name in ["SSRS Report", "SSRS File"]
            and context["is_hyperspace"]
        ):
            if enabled_for_hyperspace:
                return f"EpicAct:AC_RW_WEB_BROWSER,LaunchOptions:2,runparams:{report.system_run_url}&EPIC=1|FormCaption={nice_name}|ActivityName={nice_name}"

            return f"EpicAct:AC_RW_WEB_BROWSER,LaunchOptions:2,runparams:{report.system_run_url}|FormCaption={nice_name}|ActivityName={nice_name}"

        if report.system_identifier == "IDN":
            return f"EpicAct:WM_METRIC_EDITOR,INFONAME:IDNRECORDID,INFOVALUE:{report.system_id}"

        if report.system_identifier == "FDM" and report.system_id:
            return f"EpicACT:BI_SLICERDICER,LaunchOptions:16,RunParams:StartingDataModelId={report.system_id}"

        if report.type.name == "SlicerDicer Session" and report.system_id:
            return f"EpicACT:BI_SLICERDICER,RunParams:StartingPopulationId={report.system_id}"

        return report.system_run_url

    return False


@register.simple_tag(takes_context=True)
def edit_url(context: Dict[Any, Any], report: Reports) -> Union[bool, str]:
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    domain = context["domain"]
    if report.orphan == "Y":
        return False

    if report.system_path and context["is_hyperspace"] is False:
        return f"reportbuilder:Action=Edit&ItemPath={report.system_path}&Endpoint=https%3A%2F%2F{report.system_server}.{domain}%3A443%2FReportServer"

    if (
        report.system_identifier == "HGR"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:AC_NEW_REPORT_ADMIN,INFONAME:HGRRECORDID,INFOVALUE:{report.system_id}"

    if (
        report.system_identifier == "IDM"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:WM_DASHBOARD_EDITOR,INFONAME:IDMRECORDID,INFOVALUE:{report.system_id}"

    if (
        report.system_identifier == "IDB"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:WM_COMPONENT_EDITOR,INFONAME:IDBRECORDID,INFOVALUE:{report.system_id}"

    if (
        report.system_identifier == "HRX"
        and report.system_id
        and context["is_hyperspace"]
        and report.system_template_id
    ):
        return f"EpicAct:IP_REPORT_SETTING_POPUP,runparams:{report.system_template_id}|{report.system_id}"

    if (
        report.system_identifier == "IDN"
        and report.system_id
        and context["is_hyperspace"]
        and report.system_template_id
    ):
        return f"EpicAct:WM_METRIC_EDITOR,INFONAME:IDNRECORDID,INFOVALUE:{report.system_id}"

    return False


@register.simple_tag(takes_context=True)
def manage_url(context: Dict[Any, Any], report: Reports) -> Optional[str]:
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    if (
        report.type.name in ["SSRS Report", "SSRS File", "SSRS Report Link"]
        and context["is_hyperspace"] is False
    ):
        domain = context["domain"]
        return f"https://{report.system_server}.{domain}/Reports/manage/catalogitem/properties{report.system_path}"
    return None
