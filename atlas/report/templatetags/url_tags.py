"""Custom template tag to render markdown."""
from django import template
from django.utils.http import urlencode

register = template.Library()
import re

from index.models import Reports


def run_authorization(report, request):
    # Only catch - Crystal Report (3) & Reporting Workbench (17)
    if report.type_id not in [3, 17]:
        return True

    user_groups = request.user.get_group_ids
    report_groups = report.get_group_ids

    # check hrx
    if set(report_groups) < set(user_groups):
        return True

    # check hrg
    for parent_report in Reports.objects.filter(parent__child=report.report_id).all():
        if set(parent_report.get_group_ids) < set(user_groups):
            return True

    return False


@register.simple_tag(takes_context=True)
def run_url(context, report):
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    if not run_authorization(report, context.request):
        return False

    if report.orphan == "Y":
        return False

    if report.name is None:
        return False

    nice_name = re.sub(r"[|=]", " ", report.name)

    enabled_for_hyperspace = bool(
        report.docs.enabled_for_hyperspace if report.has_docs() else False
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

        elif report.system_identifier == "HGR":
            return f"EpicAct:AC_RW_STATUS,RUNPARAMS:{report.system_template_id}"

        elif report.system_identifier == "IDM":
            return f"EpicAct:WM_DASHBOARD_LAUNCHER,runparams:{report.system_id}"

        elif (
            report.type.name in ["SSRS Report", "SSRS File"]
            and context["is_hyperspace"]
        ):

            if enabled_for_hyperspace:
                return f"EpicAct:AC_RW_WEB_BROWSER,LaunchOptions:2,runparams:{report.system_run_url}&EPIC=1|FormCaption={nice_name}|ActivityName={nice_name}"

            else:
                return f"EpicAct:AC_RW_WEB_BROWSER,LaunchOptions:2,runparams:{report.system_run_url}|FormCaption={nice_name}|ActivityName={nice_name}"

        elif report.system_identifier == "IDN":
            return f"EpicAct:WM_METRIC_EDITOR,INFONAME:IDNRECORDID,INFOVALUE:{report.system_id}"

        elif report.system_identifier == "FDM" and report.system_id:
            return f"EpicACT:BI_SLICERDICER,LaunchOptions:16,RunParams:StartingDataModelId={report.system_id}"

        elif report.type.name == "SlicerDicer Session" and report.system_id:
            return f"EpicACT:BI_SLICERDICER,RunParams:StartingPopulationId={report.system_id}"

        else:
            return report.system_run_url

    return False


@register.simple_tag(takes_context=True)
def edit_url(context, report):
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    domain = context["domain"]
    if report.orphan == "Y":
        return False

    if report.system_path and context["is_hyperspace"] is False:
        return f"reportbuilder:Action=Edit&ItemPath={report.system_path}&Endpoint=https%3A%2F%2F{report.system_server}.{domain}%3A443%2FReportServer"

    elif (
        report.system_identifier == "HGR"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:AC_NEW_REPORT_ADMIN,INFONAME:HGRRECORDID,INFOVALUE:{report.system_id}"

    elif (
        report.system_identifier == "IDM"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:WM_DASHBOARD_EDITOR,INFONAME:IDMRECORDID,INFOVALUE:{report.system_id}"

    elif (
        report.system_identifier == "IDB"
        and report.system_id
        and context["is_hyperspace"]
    ):
        return f"EpicAct:WM_COMPONENT_EDITOR,INFONAME:IDBRECORDID,INFOVALUE:{report.system_id}"

    elif (
        report.system_identifier == "HRX"
        and report.system_id
        and context["is_hyperspace"]
        and report.system_template_id
    ):
        return f"EpicAct:IP_REPORT_SETTING_POPUP,runparams:{report.system_template_id}|{report.system_id}"

    elif (
        report.system_identifier == "IDN"
        and report.system_id
        and context["is_hyperspace"]
        and report.system_template_id
    ):
        return f"EpicAct:WM_METRIC_EDITOR,INFONAME:IDNRECORDID,INFOVALUE:{report.system_id}"

    return False


@register.simple_tag(takes_context=True)
def manage_url(context, report):
    """Check if user is authorized to use favorites.

    :param value: list of permissions
    :returns: true/false if they have a 41
    """
    if (
        report.type.name in ["SSRS Report", "SSRS File", "SSRS Report Link"]
        and context["is_hyperspace"] is False
    ):
        return "https://{}.{}/Reports/manage/catalogitem/properties{}".format(
            report.system_server,
            context["domain"],
            report.system_path,
        )
    return None
