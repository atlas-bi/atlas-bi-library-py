# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# create with "poetry run python manage.py inspectdb --database=dg_db > index/models-dev.py"
#
# to import from various schemas = make sure user owns the schema, and then change it to default
# for the user. run command for each schema.
#

import re
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserGroups(models.Model):
    group_id = models.AutoField(primary_key=True)
    account_name = models.TextField(blank=True, null=True)
    group_name = models.TextField(blank=True, null=True)
    group_email = models.TextField(blank=True, null=True)
    group_type = models.TextField(blank=True, null=True)
    group_source = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)
    epic_id = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.group_name


class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_key = models.TextField(blank=True, null=True)
    type = models.ForeignKey(
        "ReportTypes", blank=True, null=True, on_delete=models.CASCADE
    )
    name = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    system_description = models.TextField(blank=True, null=True)
    system_server = models.CharField(max_length=255)
    system_db = models.CharField(max_length=255)
    system_table = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        "Users",
        related_name="report_creator",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    modified_by = models.ForeignKey(
        "Users",
        related_name="report_modifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    _modified_at = models.DateTimeField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    system_identifier = models.CharField(max_length=3, blank=True, null=True)
    system_id = models.DecimalField(
        max_digits=18, decimal_places=0, blank=True, null=True
    )
    system_template_id = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    system_catalog_id = models.CharField(max_length=50, blank=True, null=True)
    visible = models.CharField(max_length=1, blank=True, null=True)
    orphan = models.CharField(max_length=1, blank=True, null=True)
    system_path = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)
    certification_tag = models.CharField(max_length=200, blank=True, null=True)

    @property
    def friendly_name(self):
        return self.title or self.name

    def __str__(self):
        return self.title or self.name

    def system_viewer_url(self, in_system):
        """Build system record viewer url."""
        if self.system_id and self.system_identifier and in_system:
            return "EpicAct:AR_RECORD_VIEWER,runparams:{}|{}".format(
                self.system_identifier,
                self.system_id,
            )

        return None

    def system_editor_url(self, in_system, domain):
        """Build system editor url."""
        url = None
        if self.system_path and in_system:
            url = "reportbuilder:Action=Edit&ItemPath={}&Endpoint=https://{}.:{}433/ReportServer".format(
                self.system_path,
                self.system_server,
                domain,
            )
        elif self.system_identifier == "FDM" and self.system_id and in_system:
            url = (
                "EpicACT:BI_SLICERDICER,LaunchOptions:16,RunParams:StartingDataModelId=%s"
                % self.system_id
            )
        elif self.system_identifier == "IDM" and self.system_id and in_system:
            url = (
                "EpicAct:WM_DASHBOARD_EDITOR,INFONAME:IDMRECORDID,INFOVALUE%s:"
                % self.system_id
            )
        elif self.system_identifier == "IDB" and self.system_id and in_system:
            url = (
                "EpicAct:WM_COMPONENT_EDITOR,INFONAME:IDBRECORDID,INFOVALUE:%s"
                % self.system_id
            )
        elif (
            self.system_identifier == "HRX"
            and self.system_id
            and in_system
            and self.system_template_id
        ):
            url = (
                "EpicAct:IP_REPORT_SETTING_POPUP,runparams:"
                + self.system_template_id
                + "|"
                + self.system_id
            )
        elif (
            self.system_identifier == "IDN"
            and self.system_id
            and in_system
            and self.system_template_id
        ):
            url = (
                "EpicAct:WM_METRIC_EDITOR,INFONAME:IDNRECORDID,INFOVALUE:%s"
                % self.system_id
            )

        return url

    def system_manage_url(self, in_system, domain):
        """Build system manage url."""
        if self.type_id.name == "SSRS Report" and not in_system:
            return "https://{}.{}/Reports/manage/catalogitem/properties{}".format(
                self.system_server,
                domain,
                self.system_path,
            )
        return None

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""

    def system_run_url(self):
        return None


class ReportGroupMemberships(models.Model):
    membership_id = models.AutoField(primary_key=True)
    group_id = models.ForeignKey("UserGroups", on_delete=models.CASCADE)
    report_id = models.ForeignKey(
        "Reports", on_delete=models.CASCADE, related_name="groups"
    )
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportHierarchies(models.Model):
    parent = models.OneToOneField(
        "Reports", related_name="parent", primary_key=True, on_delete=models.CASCADE
    )
    child = models.ForeignKey("Reports", related_name="child", on_delete=models.CASCADE)
    rank = models.IntegerField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportQueries(models.Model):
    query_id = models.AutoField(primary_key=True)
    report_id = models.ForeignKey(
        Reports,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="queries",
    )
    query = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.query


class ReportRuns(models.Model):
    report_id = models.OneToOneField(
        Reports, primary_key=True, on_delete=models.CASCADE
    )
    run_id = models.IntegerField()
    user_id = models.ForeignKey(
        "Users", blank=True, null=True, on_delete=models.CASCADE
    )
    start_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportSubscriptions(models.Model):
    subscriptions_id = models.AutoField(primary_key=True)
    report_id = models.ForeignKey(
        Reports,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    user_id = models.ForeignKey(
        "Users", blank=True, null=True, on_delete=models.CASCADE
    )
    unique_id = models.TextField(blank=True, null=True)
    inactive = models.IntegerField(blank=True, null=True)
    email_list = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    last_run = models.DateTimeField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.TextField()
    code = models.TextField(blank=True, null=True)
    short_name = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def short(self):
        return self.short_name or self.name


class Users(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.TextField()
    employee_id = models.TextField(blank=True, null=True)
    account_name = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    _full_name = models.TextField(blank=True, null=True)
    _first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    base = models.TextField(blank=True, null=True)
    system_id = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = True
    date_joined = None
    is_superuser = True  # check permissions for admin
    is_staff = True

    @property
    def is_admin(self):
        return self.role_links.filter(role_id=1).exists()

    def has_permission(self, perm, obj=None):
        # check if they have a permission
        return (
            self.role_links.filter(role_id=1).exists()
            or self.role_links.permission_links.filter(permissions_id=perm).exists()
        )

    def get_preferences(self):
        # return users preferences as queriable object
        return self.user_preferences

    def get_permissions(self):
        # return all permissions
        if self.role_links.filter(role_id=1).exists():
            return list(
                RolePermissions.objects.all().values_list("permissions_id", flat=True)
            )

        return list(
            self.role_links.values_list(
                "role_id__permission_links__permission_id", flat=True
            )
        ).append(
            # every one can get ``user`` permissions.
            list(
                RolePermissions.objects.filter(
                    role_permission_links__role_id=6
                ).values_list("permissions_id", flat=True)
            )
        )

    def get_roles(self):
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))

    def get_favorites(self):
        # return all favorites
        return list(self.favorites.values_list("item_type", "item_id"))

    def has_favorite(self, item_type, item_id, obj=None):
        # check if they have a permission
        return self.favorites.filter(item_type=item_type, item_id=item_id).exists()

    @property
    def active_role(self):
        if self.user_preferences.filter(key="ActiveRole").exists():
            return UserRoles.objects.filter(
                role_id=self.user_preferences.filter(key="ActiveRole").first().value
            ).first()
        return None

    @property
    def password(self):
        return 123

    @property
    def full_name(self):
        return self.build_full_name()

    @property
    def first_name(self):
        if self._first_name:
            return self._first_name

        # if the name format is "last, first" > "First Last"
        if self.account_name and "," in self.account_name:
            name = self.account_name.replace(", ", ",").split(" ")[0].split(",")
            if len(name) > 1:
                return name[1].title()

        # if the name format is "domain\first-last" > "First Last"
        if self.account_name:
            return re.sub(r".+?\\+", "", self.account_name).split("-")[0].title()

        # if the name format is "last, first" > "First Last"
        if self.username and "," in self.username:
            name = self.username.replace(", ", ",").split(" ")[0].split(",")
            if len(name) > 1:
                return name[1].title()

        # if the name format is "domain\first-last" > "First Last"
        if self.username:
            return re.sub(r".+?\\+", "", self.username).split("-")[0].title()

    def build_full_name(self):
        if self._full_name:
            return self._full_name

        # if the name format is "last, first" > "First Last"
        if self.account_name and "," in self.account_name:
            name = self.account_name.replace(", ", ",").split(" ")[0].split(",")
            if len(name) > 1:
                return ("{} {}".format(name[1], name[0])).title()

        # if the name format is "domain\first-last" > "First Last"
        if self.account_name:
            return re.sub(r".+?\\+", "", self.account_name).replace("-", " ").title()

        # if the name format is "last, first" > "First Last"
        if self.username and "," in self.username:
            name = self.username.replace(", ", ",").split(" ")[0].split(",")
            if len(name) > 1:
                return ("{} {}".format(name[1], name[0])).title()

        # if the name format is "domain\first-last" > "First Last"
        if self.username:
            return re.sub(r".+?\\+", "", self.username).replace("-", " ").title()

        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.build_full_name()


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, blank=True, null=True, on_delete=models.CASCADE)
    group_id = models.ForeignKey(
        UserGroups, blank=True, null=True, on_delete=models.CASCADE
    )
    etl_date = models.DateTimeField(blank=True, null=True)


class Analytics(models.Model):
    analytics_id = models.AutoField(primary_key=True)
    username = models.TextField(blank=True, null=True)
    app_code_name = models.TextField(blank=True, null=True)
    app_name = models.TextField(blank=True, null=True)
    app_version = models.TextField(blank=True, null=True)
    cookie_enabled = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    oscpu = models.TextField(blank=True, null=True)
    platform = models.TextField(blank=True, null=True)
    useragent = models.TextField(blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    href = models.TextField(blank=True, null=True)
    protocol = models.TextField(blank=True, null=True)
    search = models.TextField(blank=True, null=True)
    pathname = models.TextField(blank=True, null=True)
    unique_id = models.TextField(blank=True, null=True)
    screen_height = models.TextField(blank=True, null=True)
    screen_width = models.TextField(blank=True, null=True)
    origin = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    load_time = models.TextField(blank=True, null=True)
    access_date = models.DateTimeField(blank=True, null=True)
    referrer = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        blank=True,
        null=True,
        related_name="analytics",
        on_delete=models.CASCADE,
    )
    zoom = models.FloatField(blank=True, null=True)
    epic = models.IntegerField(blank=True, null=True)
    page_id = models.TextField(blank=True, null=True)
    session_id = models.TextField(blank=True, null=True)
    page_time = models.IntegerField(blank=True, null=True)
    session_time = models.IntegerField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)


class ProjectAgreements(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    _met_at = models.DateTimeField(blank=True, null=True)
    _effective_from = models.DateTimeField(blank=True, null=True)
    _modified_at = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        related_name="project_agreement_modifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    project_id = models.ForeignKey(
        "Projects",
        blank=True,
        null=True,
        related_name="agreements",
        on_delete=models.CASCADE,
    )
    rank = models.IntegerField(blank=True, null=True)

    @property
    def met_at(self):
        if self._met_at:
            return datetime.strftime(self._met_at, "%m/%d/%y")
        return ""

    @property
    def effective_from(self):
        if self._effective_from:
            return datetime.strftime(self._effective_from, "%m/%d/%y")
        return ""

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""


class ProjectAgreementUsers(models.Model):
    agreementusers_id = models.AutoField(primary_key=True)
    agreement_id = models.ForeignKey(
        ProjectAgreements, blank=True, null=True, on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(
        "Users",
        blank=True,
        null=True,
        related_name="project_agreement",
        on_delete=models.CASCADE,
    )
    modified_at = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        related_name="project_agreement_users_modifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )


class ProjectAttachments(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey("Projects", on_delete=models.CASCADE)
    rank = models.IntegerField()
    data = models.BinaryField()
    category = models.TextField()
    name = models.TextField(blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)


class InitiativeContacts(models.Model):
    contact_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=55, blank=True, null=True)
    company = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class InitiativeContactLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    initiative = models.ForeignKey(
        "Initiatives",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="contact_links",
    )
    contact = models.ForeignKey(
        InitiativeContacts,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="initiative_links",
    )

    def __str__(self):
        return "{} @{}".format(
            self.contact.name,
            self.contact.company,
        )


class Initiatives(models.Model):
    initiative_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ops_owner = models.ForeignKey(
        "Users",
        blank=True,
        null=True,
        related_name="initiative_ops_owner",
        on_delete=models.CASCADE,
    )
    exec_owner = models.ForeignKey(
        "Users",
        blank=True,
        null=True,
        related_name="initiative_exec_owner",
        on_delete=models.CASCADE,
    )

    financial_impact = models.ForeignKey(
        "Financialimpact", blank=True, null=True, on_delete=models.CASCADE
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance", blank=True, null=True, on_delete=models.CASCADE
    )
    _modified_at = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        related_name="initiative_modifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)

    initiative = models.ForeignKey(
        "Initiatives",
        blank=True,
        null=True,
        related_name="projects",
        on_delete=models.CASCADE,
    )

    name = models.TextField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ops_owner = models.ForeignKey(
        "Users",
        related_name="project_ops_owner",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    exec_owner = models.ForeignKey(
        "Users",
        related_name="project_exec_owner",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    analytics_owner = models.ForeignKey(
        "Users",
        related_name="project_analytics_owner",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    data_owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="project_data_owner",
        blank=True,
        null=True,
    )
    financial_impact = models.ForeignKey(
        "Financialimpact",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    external_documentation_url = models.TextField(blank=True, null=True)
    _modified_at = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="project_modifier",
        blank=True,
        null=True,
    )

    hidden = models.CharField(max_length=1, blank=True, null=True)

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""

    def __str__(self):
        return self.name


class ProjectChecklist(models.Model):
    checklist_id = models.AutoField(primary_key=True)
    task_id = models.ForeignKey(
        "DpMilestonetasks",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    item = models.TextField(blank=True, null=True)


class ProjectChecklistCompleted(models.Model):
    checklistcompleted_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    task_date = models.DateTimeField(blank=True, null=True)
    task_id = models.IntegerField(blank=True, null=True)
    checklist_id = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    completion_user = models.IntegerField(blank=True, null=True)


class ProjectMilestoneFrequency(models.Model):
    frequency_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)


class DpMilestonetasks(models.Model):
    milestonetaskid = models.AutoField(primary_key=True)
    milestonetemplateid = models.ForeignKey(
        "ProjectMilestoneTemplates",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    ownerid = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    startdate = models.DateTimeField(blank=True, null=True)
    enddate = models.DateTimeField(blank=True, null=True)
    lastupdateuser = models.IntegerField(blank=True, null=True)
    lastupdatedate = models.DateTimeField(blank=True, null=True)
    dataprojectid = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )


class DpMilestonetaskscompleted(models.Model):
    milestonetaskcompletedid = models.AutoField(primary_key=True)
    dataprojectid = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    completiondate = models.DateTimeField(blank=True, null=True)
    completionuser = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    owner = models.TextField(blank=True, null=True)
    duedate = models.DateTimeField(blank=True, null=True)


class ProjectMilestoneTemplates(models.Model):
    template_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    milestonetypeid = models.ForeignKey(
        ProjectMilestoneFrequency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    lastupdateuser = models.IntegerField(blank=True, null=True)
    lastupdatedate = models.DateTimeField(blank=True, null=True)
    interval = models.IntegerField(blank=True, null=True)


class ProjectReports(models.Model):
    annotation_id = models.AutoField(primary_key=True)
    annotation = models.TextField(blank=True, null=True)
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
        related_name="projects",
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_annotations",
    )
    rank = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.report.friendly_name


class ProjectTerms(models.Model):
    termannotationid = models.AutoField(primary_key=True)
    annotation = models.TextField(blank=True, null=True)

    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        related_name="projects",
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="term_annotations",
    )
    rank = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.term.name


class ProjectCommentStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(
        Projects,
        on_delete=models.CASCADE,
    )


class ProjectComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    stream_id = models.ForeignKey(
        ProjectCommentStream,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user_id = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="user_project_comments",
        blank=True,
        null=True,
    )
    message = models.CharField(max_length=4000, blank=True, null=True)
    posted_at = models.DateTimeField(blank=True, null=True)


class RunFrequency(models.Model):
    frequency_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class FinancialImpact(models.Model):
    impact_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Fragility(models.Model):
    fragility_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class FragilityTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Globalsitesettings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)


class MailConversations(models.Model):
    conversationid = models.AutoField(primary_key=True)
    messageid = models.ForeignKey(
        "MailMessages",
        on_delete=models.CASCADE,
    )


class MailDrafts(models.Model):
    draftid = models.AutoField(primary_key=True)
    subject = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    editdate = models.DateTimeField(blank=True, null=True)
    messagetypeid = models.IntegerField(blank=True, null=True)
    fromuserid = models.IntegerField(blank=True, null=True)
    messageplaintext = models.TextField(blank=True, null=True)
    recipients = models.TextField(blank=True, null=True)
    replytomessageid = models.IntegerField(blank=True, null=True)
    replytoconvid = models.IntegerField(blank=True, null=True)


class MailFoldermessages(models.Model):
    id = models.AutoField(primary_key=True)
    folderid = models.ForeignKey(
        "MailFolders",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    messageid = models.ForeignKey(
        "MailMessages",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )


class MailFolders(models.Model):
    folderid = models.AutoField(primary_key=True)
    parentfolderid = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)


class MailMessagetype(models.Model):
    messagetypeid = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)


class MailMessages(models.Model):
    messageid = models.AutoField(primary_key=True)
    subject = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    senddate = models.DateTimeField(blank=True, null=True)
    messagetypeid = models.ForeignKey(
        MailMessagetype,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    fromuserid = models.IntegerField(blank=True, null=True)
    messageplaintext = models.TextField(blank=True, null=True)


class MailRecipients(models.Model):
    id = models.AutoField(primary_key=True)
    messageid = models.ForeignKey(
        MailMessages,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    touserid = models.IntegerField(blank=True, null=True)
    readdate = models.DateTimeField(blank=True, null=True)
    alertdisplayed = models.IntegerField(blank=True, null=True)
    togroupid = models.IntegerField(blank=True, null=True)


class MailRecipientsDeleted(models.Model):
    id = models.AutoField(primary_key=True)
    messageid = models.IntegerField(blank=True, null=True)
    touserid = models.IntegerField(blank=True, null=True)
    readdate = models.DateTimeField(blank=True, null=True)
    alertdisplayed = models.IntegerField(blank=True, null=True)
    togroupid = models.IntegerField(blank=True, null=True)


class MaintenanceLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    maintainer = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_maintenance_logs",
    )
    maintained_at = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    status = models.ForeignKey(
        "MaintenancelogStatus",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="logs",
    )

    class Meta:
        ordering = ["maintained_at"]


class MaintenanceLogStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name


class OrganizationalValue(models.Model):
    value_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ReportTickets(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    number = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    report_id = models.OneToOneField(
        "ReportDocs",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    url = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.number


class ReportCommentStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    reportobjectid = models.IntegerField()
    report_id = models.ForeignKey("Reports", on_delete=models.CASCADE)


class ReportComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    stream_id = models.ForeignKey(
        "ReportCommentStream",
        on_delete=models.CASCADE,
    )
    user_id = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_report_comments",
    )
    message = models.TextField()
    posted_at = models.DateTimeField()


class ReportFragilityTags(models.Model):
    link_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        "ReportDocs", on_delete=models.CASCADE, related_name="fragility_tags"
    )
    fragility_tag = models.ForeignKey(
        FragilityTag, on_delete=models.CASCADE, related_name="reports"
    )

    class Meta:
        unique_together = (("report", "fragility_tag"),)


class ReportMaintenanceLogs(models.Model):
    link_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        "ReportDocs", on_delete=models.CASCADE, related_name="logs"
    )
    log = models.ForeignKey(
        MaintenanceLogs, on_delete=models.CASCADE, related_name="reports"
    )

    class Meta:
        unique_together = (("report", "log"),)
        ordering = ["-log__maintained_at"]


class ReportTerms(models.Model):
    link_id = models.AutoField(primary_key=True)
    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
        related_name="terms",
    )
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        related_name="report_docs",
    )

    class Meta:
        unique_together = (("report_doc", "term"),)


class ReportImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    report_id = models.ForeignKey(
        Reports,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="imgs",
    )
    image_rank = models.IntegerField()
    image_data = models.BinaryField()
    image_source = models.TextField(blank=True, null=True)


class Reportobjectruntime(models.Model):
    id = models.AutoField(primary_key=True)
    runuserid = models.IntegerField(blank=True, null=True)
    runs = models.IntegerField(blank=True, null=True)
    runtime = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    runweek = models.DateTimeField(blank=True, null=True)
    runweekstring = models.TextField(blank=True, null=True)


class Reportobjecttopruns(models.Model):
    id = models.AutoField(primary_key=True)
    reportobjectid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    runuserid = models.IntegerField(blank=True, null=True)
    runs = models.IntegerField(blank=True, null=True)
    runtime = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    lastrun = models.TextField(blank=True, null=True)
    reportobjecttypeid = models.IntegerField(blank=True, null=True)


class Reportobjectweightedrunrank(models.Model):
    reportobjectid = models.IntegerField()
    weighted_run_rank = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )


class ReportDocs(models.Model):
    ops_owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_ops_owner",
        blank=True,
        null=True,
    )
    requester = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_requester",
        blank=True,
        null=True,
    )
    project_url = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assumptions = models.TextField(blank=True, null=True)
    org_value = models.ForeignKey(
        OrganizationalValue,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    frequency = models.ForeignKey(
        RunFrequency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    fragility = models.ForeignKey(
        Fragility,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    executive_report = models.CharField(max_length=1, blank=True, null=True)
    maintenance_schedule = models.ForeignKey(
        MaintenanceSchedule,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(blank=True, null=True)
    _created_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_creator",
        blank=True,
        null=True,
    )
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_modifier",
        blank=True,
        null=True,
    )
    enabled_for_hyperspace = models.CharField(max_length=1, blank=True, null=True)
    do_not_purge = models.CharField(max_length=1, blank=True, null=True)
    hidden = models.CharField(max_length=1, blank=True, null=True)

    report = models.OneToOneField(
        "Reports",
        related_name="docs",
        primary_key=True,
        on_delete=models.CASCADE,
    )

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""

    @property
    def created_at(self):
        if self._created_at:
            return datetime.strftime(self._created_at, "%m/%d/%y")
        return ""


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(primary_key=True)
    role_id = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission_id = models.ForeignKey(
        "RolePermissions",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="role_permission_links",
    )


class RolePermissions(models.Model):
    permissions_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class Searchtable(models.Model):
    id = models.AutoField(primary_key=True)
    itemid = models.IntegerField(blank=True, null=True)
    typeid = models.IntegerField(blank=True, null=True)
    itemtype = models.CharField(max_length=100, blank=True, null=True)
    itemrank = models.IntegerField(blank=True, null=True)
    searchfielddescription = models.CharField(max_length=100, blank=True, null=True)
    searchfield = models.TextField(blank=True, null=True)


class SearchBasicsearchdata(models.Model):
    id = models.AutoField(primary_key=True)
    itemid = models.IntegerField(blank=True, null=True)
    typeid = models.IntegerField(blank=True, null=True)
    itemtype = models.CharField(max_length=100, blank=True, null=True)
    itemrank = models.IntegerField(blank=True, null=True)
    searchfielddescription = models.CharField(max_length=100, blank=True, null=True)
    searchfield = models.TextField(blank=True, null=True)
    hidden = models.IntegerField(blank=True, null=True)
    visibletype = models.IntegerField(blank=True, null=True)
    orphaned = models.IntegerField(blank=True, null=True)


class SearchBasicsearchdataSmall(models.Model):
    id = models.AutoField(primary_key=True)
    itemid = models.IntegerField(blank=True, null=True)
    typeid = models.IntegerField(blank=True, null=True)
    itemtype = models.CharField(max_length=100, blank=True, null=True)
    itemrank = models.IntegerField(blank=True, null=True)
    searchfielddescription = models.CharField(max_length=100, blank=True, null=True)
    searchfield = models.TextField(blank=True, null=True)
    hidden = models.IntegerField(blank=True, null=True)
    visibletype = models.IntegerField(blank=True, null=True)
    orphaned = models.IntegerField(blank=True, null=True)


class SearchReportobjectsearchdata(models.Model):
    primk = models.AutoField(primary_key=True)
    id = models.IntegerField()
    columnname = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    lastmodifieddate = models.DateTimeField(blank=True, null=True)
    epicmasterfile = models.CharField(max_length=3, blank=True, null=True)
    defaultvisibilityyn = models.CharField(max_length=1, blank=True, null=True)
    orphanedreportobjectyn = models.CharField(max_length=1, blank=True, null=True)
    reportobjecttypeid = models.IntegerField(blank=True, null=True)
    authoruserid = models.IntegerField(blank=True, null=True)
    lastmodifiedbyuserid = models.IntegerField(blank=True, null=True)
    epicreporttemplateid = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    sourceserver = models.CharField(max_length=255)
    sourcedb = models.CharField(max_length=255)
    sourcetable = models.CharField(max_length=255)
    documented = models.IntegerField()
    docownerid = models.IntegerField(blank=True, null=True)
    docrequesterid = models.IntegerField(blank=True, null=True)
    docorgvalueid = models.IntegerField(blank=True, null=True)
    docrunfreqid = models.IntegerField(blank=True, null=True)
    docfragid = models.IntegerField(blank=True, null=True)
    docexecvis = models.CharField(max_length=1, blank=True, null=True)
    docmainschedid = models.IntegerField(blank=True, null=True)
    doclastupdated = models.DateTimeField(blank=True, null=True)
    doccreated = models.DateTimeField(blank=True, null=True)
    doccreatedby = models.IntegerField(blank=True, null=True)
    docupdatedby = models.IntegerField(blank=True, null=True)
    dochypeenabled = models.CharField(max_length=1, blank=True, null=True)
    docdonotpurge = models.CharField(max_length=1, blank=True, null=True)
    dochidden = models.CharField(max_length=1, blank=True, null=True)
    twoyearruns = models.IntegerField(blank=True, null=True)
    oneyearruns = models.IntegerField(blank=True, null=True)
    sixmonthsruns = models.IntegerField(blank=True, null=True)
    onemonthruns = models.IntegerField(blank=True, null=True)


class Shareditems(models.Model):
    id = models.AutoField(primary_key=True)
    sharedfromuserid = models.IntegerField(blank=True, null=True)
    sharedtouserid = models.IntegerField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    sharedate = models.DateTimeField(blank=True, null=True)


class StrategicImportance(models.Model):
    importance_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Terms(models.Model):
    term_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    summary = models.CharField(max_length=4000, blank=True, null=True)
    technical_definition = models.TextField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)
    _approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="term_approve_user",
        blank=True,
        null=True,
    )
    has_external_standard = models.CharField(max_length=1, blank=True, null=True)
    external_standard_url = models.CharField(max_length=4000, blank=True, null=True)
    _valid_from = models.DateTimeField(blank=True, null=True)
    _valid_to = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="term_modifier",
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)

    @property
    def approved_at(self):
        if self._approved_at:
            return datetime.strftime(self._approved_at, "%m/%d/%y")
        return ""

    @property
    def valid_from(self):
        if self._valid_from:
            return datetime.strftime(self._valid_from, "%m/%d/%y")
        return ""

    @property
    def valid_to(self):
        if self._valid_to:
            return datetime.strftime(self._valid_to, "%m/%d/%y")
        return ""

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""

    def __str__(self):
        return self.name


class TermCommentStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    term = models.ForeignKey(
        Terms,
        on_delete=models.CASCADE,
        related_name="comment_streams",
    )


class TermComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    stream = models.ForeignKey(
        TermCommentStream,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="term_comments",
    )
    message = models.CharField(max_length=4000)
    posted_at = models.DateTimeField(auto_now=True)


class FavoriteFolders(models.Model):
    folder_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="favorite_folders",
    )
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["rank"]


class Favorites(models.Model):
    favorites_id = models.AutoField(primary_key=True)
    item_type = models.TextField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    item_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="favorites",
    )
    name = models.TextField(blank=True, null=True)
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="favorites",
    )

    class Meta:
        ordering = ["rank"]

    @property
    def atlas_url(self):
        return "{}s/{}".format(
            self.item_type,
            self.item_id,
        )

    @property
    def system_run_url(self):
        if self.item_type.lower() == "report":
            return Reports.objects.get(report_id=self.item_id).system_run_url()

    @property
    def system_manage_url(self):
        if self.item_type.lower() == "report":
            return Reports.objects.get(report_id=self.item_id).system_manage_url()

    @property
    def system_editor_url(self):
        if self.item_type.lower() == "report":
            return Reports.objects.get(report_id=self.item_id).system_editor_url()

    @property
    def system_id(self):
        if self.item_type.lower() == "report":
            return Reports.objects.filter(report_id=self.item_id).first().system_id

        return None

    @property
    def system_identifier(self):
        if self.item_type.lower() == "report":
            return (
                Reports.objects.filter(report_id=self.item_id).first().system_identifier
            )

        return None

    @property
    def certification_tag(self):
        if self.item_type.lower() == "report":
            return (
                Reports.objects.filter(report_id=self.item_id).first().certification_tag
            )

        return None

    @property
    def description(self):
        if self.item_type.lower() == "report":
            report = Reports.objects.get(report_id=self.item_id)
            return (
                report.docs.description
                or report.description
                or report.detailed_descripion
                or report.docs.assumptions
            )
        elif self.item_type.lower() == "term":
            term = Terms.objects.get(term_id=self.item_id)
            return term.summary or term.technical_definition
        elif self.item_type.lower() == "project":
            project = Projects.objects.get(project_id=self.item_id)
            return project.purpose or project.description
        elif self.item_type.lower() == "initiative":
            return Initiatives.objects.get(initiative_id=self.item_id).description

    def __str__(self):
        if self.item_type.lower() == "report":
            return str(Reports.objects.get(report_id=self.item_id))
        elif self.item_type.lower() == "term":
            return str(Terms.objects.get(term_id=self.item_id).name)
        elif self.item_type.lower() == "project":
            return str(Projects.objects.get(project_id=self.item_id))
        elif self.item_type.lower() == "initiative":
            return str(Initiatives.objects.get(initiative_id=self.item_id))


class UserPreferences(models.Model):
    preference_id = models.AutoField(primary_key=True)
    key = models.TextField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    item_id = models.IntegerField(blank=True, null=True)
    user_id = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_preferences",
    )


class UserRolelinks(models.Model):
    rolelinks_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="role_users",
    )


class UserRoles(models.Model):
    role_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class UserNamedata(models.Model):
    userid = models.IntegerField(primary_key=True)
    fullname = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    lastname = models.TextField(blank=True, null=True)
