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


class ReportGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    group = models.ForeignKey("UserGroups", models.DO_NOTHING, db_column="GroupId")
    report = models.ForeignKey(
        "Reports", models.DO_NOTHING, db_column="ReportId", related_name="groups"
    )
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportGroupsMemberships"


class Reports(models.Model):
    report_id = models.AutoField(db_column="ReportObjectID", primary_key=True)
    report_key = models.TextField(db_column="ReportObjectBizKey", blank=True, null=True)
    type = models.ForeignKey(
        "ReportTypes",
        models.DO_NOTHING,
        db_column="ReportObjectTypeID",
        blank=True,
        null=True,
    )
    name = models.TextField(db_column="Name", blank=True, null=True)
    title = models.TextField(db_column="DisplayTitle", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    detailed_description = models.TextField(
        db_column="DetailedDescription", blank=True, null=True
    )
    system_description = models.TextField(
        db_column="RepositoryDescription", blank=True, null=True
    )
    system_server = models.CharField(db_column="SourceServer", max_length=255)
    system_db = models.CharField(db_column="SourceDB", max_length=255)
    system_table = models.CharField(db_column="SourceTable", max_length=255)
    created_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_creator",
        db_column="AuthorUserID",
        blank=True,
        null=True,
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_modifier",
        db_column="LastModifiedByUserID",
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(
        db_column="LastModifiedDate", blank=True, null=True
    )
    url = models.TextField(db_column="ReportObjectURL", blank=True, null=True)
    system_identifier = models.CharField(
        db_column="EpicMasterFile", max_length=3, blank=True, null=True
    )
    system_id = models.DecimalField(
        db_column="EpicRecordID", max_digits=18, decimal_places=0, blank=True, null=True
    )
    system_template_id = models.DecimalField(
        db_column="EpicReportTemplateId",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    system_catalog_id = models.CharField(
        db_column="ReportServerCatalogID", max_length=50, blank=True, null=True
    )
    visible = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, null=True
    )
    orphan = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, null=True
    )
    system_path = models.TextField(db_column="ReportServerPath", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    certification_tag = models.CharField(
        db_column="CertificationTag", max_length=200, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "ReportObject"

    def has_docs(self):
        return hasattr(self, "docs")

    @property
    def friendly_name(self):
        return self.title or self.name

    def __str__(self):
        return self.title or self.name

    def system_run_url(self, in_system):
        return "123.123"

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
            return datetime.strftime(self._modified_at, "%d/%m/%y")
        return ""


class ReportHierarchies(models.Model):
    parent = models.OneToOneField(
        "Reports",
        models.DO_NOTHING,
        related_name="parent",
        db_column="ParentReportObjectID",
        primary_key=True,
    )
    child = models.ForeignKey(
        "Reports",
        models.DO_NOTHING,
        related_name="child",
        db_column="ChildReportObjectID",
    )
    rank = models.IntegerField(db_column="Line", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectHierarchy"
        unique_together = (("parent", "child"),)


class ReportQueries(models.Model):
    query_id = models.AutoField(db_column="ReportObjectQueryId", primary_key=True)
    report_id = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        null=True,
        related_name="queries",
    )
    query = models.TextField(db_column="Query", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectQuery"

    def __str__(self):
        return self.query


class ReportRuns(models.Model):
    report_id = models.OneToOneField(
        Reports, models.DO_NOTHING, db_column="ReportObjectID", primary_key=True
    )
    run_id = models.IntegerField(db_column="RunID")
    user_id = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="RunUserID", blank=True, null=True
    )
    start_time = models.DateTimeField(db_column="RunStartTime", blank=True, null=True)
    duration_seconds = models.IntegerField(
        db_column="RunDurationSeconds", blank=True, null=True
    )
    status = models.CharField(
        db_column="RunStatus", max_length=100, blank=True, null=True
    )
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectRunData"
        unique_together = (("report_id", "run_id"),)


class ReportSubscriptions(models.Model):
    subscriptions_id = models.AutoField(
        db_column="ReportObjectSubscriptionsId", primary_key=True
    )
    report_id = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        null=True,
    )
    user_id = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="UserId", blank=True, null=True
    )
    unique_id = models.TextField(db_column="SubscriptionId", blank=True, null=True)
    inactive = models.IntegerField(db_column="InactiveFlags", blank=True, null=True)
    email_list = models.TextField(db_column="EmailList", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    status = models.TextField(db_column="LastStatus", blank=True, null=True)
    last_run = models.DateTimeField(db_column="LastRunTime", blank=True, null=True)
    email = models.TextField(db_column="SubscriptionTo", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectSubscriptions"


class ReportTypes(models.Model):
    type_id = models.AutoField(db_column="ReportObjectTypeID", primary_key=True)
    name = models.TextField(db_column="Name")
    short_name = models.TextField(db_column="ShortName", blank=True, null=True)
    code = models.TextField(db_column="DefaultEpicMasterFile", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectType"

    def __str__(self):
        return self.name

    @property
    def short(self):
        return self.short_name or self.name


class Users(AbstractUser):
    user_id = models.AutoField(db_column="UserID", primary_key=True)
    username = models.TextField(db_column="Username")
    employee_id = models.TextField(db_column="EmployeeID", blank=True, null=True)
    account_name = models.TextField(db_column="AccountName", blank=True, null=True)
    display_name = models.TextField(db_column="DisplayName", blank=True, null=True)
    _full_name = models.TextField(db_column="FullName", blank=True, null=True)
    _first_name = models.TextField(db_column="FirstName", blank=True, null=True)
    last_name = models.TextField(db_column="LastName", blank=True, null=True)
    department = models.TextField(db_column="Department", blank=True, null=True)
    title = models.TextField(db_column="Title", blank=True, null=True)
    phone = models.TextField(db_column="Phone", blank=True, null=True)
    email = models.TextField(db_column="Email", blank=True, null=True)
    base = models.TextField(db_column="Base", blank=True, null=True)
    epicid = models.TextField(db_column="EpicId", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    last_login = models.DateTimeField(db_column="LastLogin", blank=True, null=True)
    is_active = True
    date_joined = None
    is_superuser = True  # check permissions for admin
    is_staff = True

    class Meta:
        managed = False
        db_table = "User"

    @property
    def is_admin(self):
        return self.role_links.filter(role_id=1).exists()

    def has_permission(self, perm, obj=None):
        # check if they have a permission
        return (
            self.role_links.filter(role_id=1).exists()
            or self.role_links.permission_links.filter(permissions_id=perm).exists()
        )

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

    def get_preferences(self):
        # return users preferences as queriable object
        return self.user_preferences

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


class UserGroups(models.Model):
    group_id = models.AutoField(db_column="GroupId", primary_key=True)
    account_name = models.TextField(db_column="AccountName", blank=True, null=True)
    group_name = models.TextField(db_column="GroupName", blank=True, null=True)
    group_email = models.TextField(db_column="GroupEmail", blank=True, null=True)
    group_type = models.TextField(db_column="GroupType", blank=True, null=True)
    group_source = models.TextField(db_column="GroupSource", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    epic_id = models.TextField(db_column="EpicId", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserGroups"

    def __str__(self):
        return self.group_name


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    user_id = models.ForeignKey(
        Users, models.DO_NOTHING, db_column="UserId", blank=True, null=True
    )
    group_id = models.ForeignKey(
        UserGroups, models.DO_NOTHING, db_column="GroupId", blank=True, null=True
    )
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserGroupsMembership"


class Analytics(models.Model):
    analytics_id = models.AutoField(db_column="Id", primary_key=True)
    username = models.TextField(db_column="Username", blank=True, null=True)
    app_code_name = models.TextField(db_column="appCodeName", blank=True, null=True)
    app_name = models.TextField(db_column="appName", blank=True, null=True)
    app_version = models.TextField(db_column="appVersion", blank=True, null=True)
    cookie_enabled = models.TextField(db_column="cookieEnabled", blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    oscpu = models.TextField(blank=True, null=True)
    platform = models.TextField(blank=True, null=True)
    useragent = models.TextField(db_column="userAgent", blank=True, null=True)
    host = models.TextField(blank=True, null=True)
    hostname = models.TextField(blank=True, null=True)
    href = models.TextField(blank=True, null=True)
    protocol = models.TextField(blank=True, null=True)
    search = models.TextField(blank=True, null=True)
    pathname = models.TextField(blank=True, null=True)
    unique_id = models.TextField(db_column="hash", blank=True, null=True)
    screen_height = models.TextField(db_column="screenHeight", blank=True, null=True)
    screen_width = models.TextField(db_column="screenWidth", blank=True, null=True)
    origin = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    load_time = models.TextField(db_column="loadTime", blank=True, null=True)
    access_date = models.DateTimeField(
        db_column="accessDateTime", blank=True, null=True
    )
    referrer = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="analytics",
    )
    zoom = models.FloatField(db_column="Zoom", blank=True, null=True)
    epic = models.IntegerField(db_column="Epic", blank=True, null=True)
    page_id = models.TextField(db_column="pageId", blank=True, null=True)
    session_id = models.TextField(db_column="sessionId", blank=True, null=True)
    page_time = models.IntegerField(db_column="pageTime", blank=True, null=True)
    session_time = models.IntegerField(db_column="sessionTime", blank=True, null=True)
    update_time = models.DateTimeField(db_column="updateTime", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Analytics"


class ProjectAgreements(models.Model):
    agreement_id = models.AutoField(db_column="AgreementID", primary_key=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    _met_at = models.DateTimeField(db_column="MeetingDate", blank=True, null=True)
    _effective_from = models.DateTimeField(
        db_column="EffectiveDate", blank=True, null=True
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_agreement_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )
    project_id = models.ForeignKey(
        "Projects",
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
        related_name="agreements",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_Agreement"

    @property
    def met_at(self):
        if self._met_at:
            return datetime.strftime(self._met_at, "%d/%m/%y")
        return ""

    @property
    def effective_from(self):
        if self._effective_from:
            return datetime.strftime(self._effective_from, "%d/%m/%y")
        return ""

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%d/%m/%y")
        return ""


class ProjectAgreementUsers(models.Model):
    agreementusers_id = models.AutoField(db_column="AgreementUsersID", primary_key=True)
    agreement_id = models.ForeignKey(
        ProjectAgreements,
        models.DO_NOTHING,
        db_column="AgreementID",
        blank=True,
        null=True,
    )
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="project_agreement",
    )
    modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_agreement_users_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "DP_AgreementUsers"


class ProjectAttachments(models.Model):
    attachment_id = models.AutoField(db_column="AttachmentId", primary_key=True)
    project_id = models.ForeignKey(
        "Projects", models.DO_NOTHING, db_column="DataProjectId"
    )
    rank = models.IntegerField(db_column="Rank")
    data = models.BinaryField(db_column="AttachmentData")
    category = models.TextField(db_column="AttachmentType")
    name = models.TextField(db_column="AttachmentName", blank=True, null=True)
    size = models.IntegerField(db_column="AttachmentSize", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_Attachments"


class InitiativeContacts(models.Model):
    contact_id = models.AutoField(db_column="ContactID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    email = models.TextField(db_column="Email", blank=True, null=True)
    phone = models.CharField(db_column="Phone", max_length=55, blank=True, null=True)
    company = models.TextField(db_column="Company", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "DP_Contact"


class InitiativeContactLinks(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    initiative_id = models.ForeignKey(
        "Initiatives",
        models.DO_NOTHING,
        db_column="InitiativeId",
        blank=True,
        null=True,
    )
    contact_id = models.ForeignKey(
        InitiativeContacts,
        models.DO_NOTHING,
        db_column="ContactId",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "DP_Contact_Links"


class Initiatives(models.Model):
    initiative_id = models.AutoField(db_column="DataInitiativeID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    ops_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="OperationOwnerID",
        blank=True,
        null=True,
        related_name="initiative_ops_owner",
    )
    exec_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="ExecutiveOwnerID",
        blank=True,
        null=True,
        related_name="initiative_exec_owner",
    )

    financial_impact = models.ForeignKey(
        "Financialimpact",
        models.DO_NOTHING,
        db_column="FinancialImpact",
        blank=True,
        null=True,
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        models.DO_NOTHING,
        db_column="StrategicImportance",
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="initiative_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%d/%m/%y")
        return ""

    class Meta:
        managed = False
        db_table = "DP_DataInitiative"


class Projects(models.Model):
    project_id = models.AutoField(db_column="DataProjectID", primary_key=True)

    initiative = models.ForeignKey(
        "Initiatives",
        models.DO_NOTHING,
        db_column="DataInitiativeID",
        blank=True,
        null=True,
        related_name="projects",
    )

    name = models.TextField(db_column="Name", blank=True, null=True)
    purpose = models.TextField(db_column="Purpose", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    ops_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_ops_owner",
        db_column="OperationOwnerID",
        blank=True,
        null=True,
    )
    exec_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_exec_owner",
        db_column="ExecutiveOwnerID",
        blank=True,
        null=True,
    )
    analytics_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_analytics_owner",
        db_column="AnalyticsOwnerID",
        blank=True,
        null=True,
    )
    data_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_data_owner",
        db_column="DataManagerID",
        blank=True,
        null=True,
    )
    financial_impact = models.ForeignKey(
        "Financialimpact",
        models.DO_NOTHING,
        db_column="FinancialImpact",
        blank=True,
        null=True,
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        models.DO_NOTHING,
        db_column="StrategicImportance",
        blank=True,
        null=True,
    )
    external_documentation_url = models.TextField(
        db_column="ExternalDocumentationURL", blank=True, null=True
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="project_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )

    hidden = models.CharField(max_length=1, blank=True, null=True)

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%d/%m/%y")
        return ""

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "DP_DataProject"


class ProjectChecklist(models.Model):
    checklist_id = models.AutoField(db_column="MilestoneChecklistId", primary_key=True)
    task_id = models.ForeignKey(
        "DpMilestonetasks",
        models.DO_NOTHING,
        db_column="MilestoneTaskId",
        blank=True,
        null=True,
    )
    item = models.TextField(db_column="Item", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_MilestoneChecklist"


class ProjectChecklistCompleted(models.Model):
    checklistcompleted_id = models.AutoField(
        db_column="MilestoneChecklistCompletedId", primary_key=True
    )
    project_id = models.ForeignKey(
        Projects,
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
    )
    task_date = models.DateTimeField(db_column="TaskDate", blank=True, null=True)
    task_id = models.IntegerField(db_column="TaskId", blank=True, null=True)
    checklist_id = models.IntegerField(
        db_column="MilestoneChecklistId", blank=True, null=True
    )
    status = models.BooleanField(db_column="ChecklistStatus", blank=True, null=True)
    completion_date = models.DateTimeField(
        db_column="CompletionDate", blank=True, null=True
    )
    completion_user = models.IntegerField(
        db_column="CompletionUser", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "DP_MilestoneChecklistCompleted"


class ProjectMilestoneFrequency(models.Model):
    frequency_id = models.AutoField(db_column="MilestoneTypeId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_MilestoneFrequency"


class DpMilestonetasks(models.Model):
    milestonetaskid = models.AutoField(db_column="MilestoneTaskId", primary_key=True)
    milestonetemplateid = models.ForeignKey(
        "DpMilestonetemplates",
        models.DO_NOTHING,
        db_column="MilestoneTemplateId",
        blank=True,
        null=True,
    )
    ownerid = models.IntegerField(db_column="OwnerId", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    startdate = models.DateTimeField(db_column="StartDate", blank=True, null=True)
    enddate = models.DateTimeField(db_column="EndDate", blank=True, null=True)
    lastupdateuser = models.IntegerField(
        db_column="LastUpdateUser", blank=True, null=True
    )
    lastupdatedate = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    dataprojectid = models.ForeignKey(
        Projects,
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "DP_MilestoneTasks"


class DpMilestonetaskscompleted(models.Model):
    milestonetaskcompletedid = models.AutoField(
        db_column="MilestoneTaskCompletedId", primary_key=True
    )
    dataprojectid = models.ForeignKey(
        Projects,
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
    )
    completiondate = models.DateTimeField(
        db_column="CompletionDate", blank=True, null=True
    )
    completionuser = models.TextField(db_column="CompletionUser", blank=True, null=True)
    comments = models.TextField(db_column="Comments", blank=True, null=True)
    owner = models.TextField(db_column="Owner", blank=True, null=True)
    duedate = models.DateTimeField(db_column="DueDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_MilestoneTasksCompleted"


class DpMilestonetemplates(models.Model):
    milestonetemplateid = models.AutoField(
        db_column="MilestoneTemplateId", primary_key=True
    )
    name = models.TextField(db_column="Name", blank=True, null=True)
    milestonetypeid = models.ForeignKey(
        ProjectMilestoneFrequency,
        models.DO_NOTHING,
        db_column="MilestoneTypeId",
        blank=True,
        null=True,
    )
    lastupdateuser = models.IntegerField(
        db_column="LastUpdateUser", blank=True, null=True
    )
    lastupdatedate = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    interval = models.IntegerField(db_column="Interval", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "DP_MilestoneTemplates"


class ProjectReports(models.Model):
    annotation_id = models.AutoField(db_column="ReportAnnotationID", primary_key=True)
    annotation = models.TextField(db_column="Annotation", blank=True, null=True)
    report = models.ForeignKey(
        "Reports",
        models.DO_NOTHING,
        db_column="ReportId",
        related_name="projects",
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Projects,
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
        related_name="reports",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    def __str__(self):
        return self.report.friendly_name

    class Meta:
        managed = False
        db_table = "DP_ReportAnnotation"


class ProjectTerms(models.Model):
    termannotationid = models.AutoField(db_column="TermAnnotationID", primary_key=True)
    annotation = models.TextField(db_column="Annotation", blank=True, null=True)

    term = models.ForeignKey(
        "Terms",
        models.DO_NOTHING,
        db_column="TermId",
        related_name="projects",
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Projects,
        models.DO_NOTHING,
        db_column="DataProjectId",
        blank=True,
        null=True,
        related_name="terms",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    def __str__(self):
        return self.report

    class Meta:
        managed = False
        db_table = "DP_TermAnnotation"


class ProjectCommentStream(models.Model):
    stream_id = models.AutoField(
        db_column="DataProjectConversationId", primary_key=True
    )
    project_id = models.ForeignKey(
        Projects, models.DO_NOTHING, db_column="DataProjectId"
    )

    class Meta:
        managed = False
        db_table = "Dp_DataProjectConversation"


class ProjectComments(models.Model):
    comment_id = models.AutoField(
        db_column="DataProjectConversationMessageId", primary_key=True
    )
    stream_id = models.ForeignKey(
        ProjectCommentStream,
        models.DO_NOTHING,
        db_column="DataProjectConversationId",
        blank=True,
        null=True,
    )
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="user_project_comments",
        db_column="UserId",
        blank=True,
        null=True,
    )
    message = models.CharField(
        db_column="MessageText", max_length=4000, blank=True, null=True
    )
    posted_at = models.DateTimeField(db_column="PostDateTime", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Dp_DataProjectConversationMessage"


class RunFrequency(models.Model):
    frequency_id = models.AutoField(
        db_column="EstimatedRunFrequencyID", primary_key=True
    )
    name = models.TextField(
        db_column="EstimatedRunFrequencyName", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "EstimatedRunFrequency"

    def __str__(self):
        return self.name


class FinancialImpact(models.Model):
    impact_id = models.AutoField(db_column="FinancialImpactId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "FinancialImpact"


class Fragility(models.Model):
    fragility_id = models.AutoField(db_column="FragilityID", primary_key=True)
    name = models.TextField(db_column="FragilityName", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Fragility"

    def __str__(self):
        return self.name


class FragilityTag(models.Model):
    tag_id = models.AutoField(db_column="FragilityTagID", primary_key=True)
    name = models.TextField(db_column="FragilityTagName", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "FragilityTag"

    def __str__(self):
        return self.name


class Globalsitesettings(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    value = models.TextField(db_column="Value", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "GlobalSiteSettings"


class MailConversations(models.Model):
    conversationid = models.AutoField(db_column="ConversationId", primary_key=True)
    messageid = models.ForeignKey(
        "MailMessages", models.DO_NOTHING, db_column="MessageId"
    )

    class Meta:
        managed = False
        db_table = "Mail_Conversations"


class MailDrafts(models.Model):
    draftid = models.AutoField(db_column="DraftId", primary_key=True)
    subject = models.TextField(db_column="Subject", blank=True, null=True)
    message = models.TextField(db_column="Message", blank=True, null=True)
    editdate = models.DateTimeField(db_column="EditDate", blank=True, null=True)
    messagetypeid = models.IntegerField(
        db_column="MessageTypeId", blank=True, null=True
    )
    fromuserid = models.IntegerField(db_column="FromUserId", blank=True, null=True)
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, null=True
    )
    recipients = models.TextField(db_column="Recipients", blank=True, null=True)
    replytomessageid = models.IntegerField(
        db_column="ReplyToMessageId", blank=True, null=True
    )
    replytoconvid = models.IntegerField(
        db_column="ReplyToConvId", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "Mail_Drafts"


class MailFoldermessages(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    folderid = models.ForeignKey(
        "MailFolders", models.DO_NOTHING, db_column="FolderId", blank=True, null=True
    )
    messageid = models.ForeignKey(
        "MailMessages", models.DO_NOTHING, db_column="MessageId", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "Mail_FolderMessages"


class MailFolders(models.Model):
    folderid = models.AutoField(db_column="FolderId", primary_key=True)
    parentfolderid = models.IntegerField(
        db_column="ParentFolderId", blank=True, null=True
    )
    userid = models.IntegerField(db_column="UserId", blank=True, null=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Mail_Folders"


class MailMessagetype(models.Model):
    messagetypeid = models.AutoField(db_column="MessageTypeId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Mail_MessageType"


class MailMessages(models.Model):
    messageid = models.AutoField(db_column="MessageId", primary_key=True)
    subject = models.TextField(db_column="Subject", blank=True, null=True)
    message = models.TextField(db_column="Message", blank=True, null=True)
    senddate = models.DateTimeField(db_column="SendDate", blank=True, null=True)
    messagetypeid = models.ForeignKey(
        MailMessagetype,
        models.DO_NOTHING,
        db_column="MessageTypeId",
        blank=True,
        null=True,
    )
    fromuserid = models.IntegerField(db_column="FromUserId", blank=True, null=True)
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "Mail_Messages"


class MailRecipients(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    messageid = models.ForeignKey(
        MailMessages, models.DO_NOTHING, db_column="MessageId", blank=True, null=True
    )
    touserid = models.IntegerField(db_column="ToUserId", blank=True, null=True)
    readdate = models.DateTimeField(db_column="ReadDate", blank=True, null=True)
    alertdisplayed = models.IntegerField(
        db_column="AlertDisplayed", blank=True, null=True
    )
    togroupid = models.IntegerField(db_column="ToGroupId", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Mail_Recipients"


class MailRecipientsDeleted(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    messageid = models.IntegerField(db_column="MessageId", blank=True, null=True)
    touserid = models.IntegerField(db_column="ToUserId", blank=True, null=True)
    readdate = models.DateTimeField(db_column="ReadDate", blank=True, null=True)
    alertdisplayed = models.IntegerField(
        db_column="AlertDisplayed", blank=True, null=True
    )
    togroupid = models.IntegerField(db_column="ToGroupId", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Mail_Recipients_Deleted"


class MaintenanceLogs(models.Model):
    log_id = models.AutoField(db_column="MaintenanceLogID", primary_key=True)
    maintainer = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="MaintainerID",
        blank=True,
        null=True,
        related_name="report_maintenance_logs",
    )
    maintained_at = models.DateTimeField(
        db_column="MaintenanceDate", blank=True, null=True
    )
    comments = models.TextField(db_column="Comment", blank=True, null=True)
    status = models.ForeignKey(
        "MaintenancelogStatus",
        models.DO_NOTHING,
        db_column="MaintenanceLogStatusID",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "MaintenanceLog"
        ordering = ["maintained_at"]


class MaintenanceLogStatus(models.Model):
    status_id = models.AutoField(db_column="MaintenanceLogStatusID", primary_key=True)
    name = models.TextField(db_column="MaintenanceLogStatusName")

    class Meta:
        managed = False
        db_table = "MaintenanceLogStatus"

    def __str__(self):
        return self.name


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(db_column="MaintenanceScheduleID", primary_key=True)
    name = models.TextField(db_column="MaintenanceScheduleName")

    class Meta:
        managed = False
        db_table = "MaintenanceSchedule"

    def __str__(self):
        return self.name


class Organizationalvalue(models.Model):
    organizationalvalue_id = models.AutoField(
        db_column="OrganizationalValueID", primary_key=True
    )
    name = models.TextField(db_column="OrganizationalValueName", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "OrganizationalValue"

    def __str__(self):
        return self.name


class ReportTickets(models.Model):
    ticket_id = models.AutoField(db_column="ManageEngineTicketsId", primary_key=True)
    number = models.IntegerField(db_column="TicketNumber", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    report_id = models.OneToOneField(
        "ReportDocs",
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        null=True,
        related_name="tickets",
    )
    ticketurl = models.TextField(db_column="TicketUrl", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportManageEngineTickets"

    def __str__(self):
        return self.number


class ReportCommentStream(models.Model):
    stream_id = models.AutoField(db_column="ConversationID", primary_key=True)
    report_id = models.ForeignKey(
        "Reports", models.DO_NOTHING, db_column="ReportObjectID"
    )

    class Meta:
        managed = False
        db_table = "ReportObjectConversation_doc"


class ReportComments(models.Model):
    comment_id = models.AutoField(db_column="MessageID", primary_key=True)
    stream_id = models.ForeignKey(
        "ReportCommentStream", models.DO_NOTHING, db_column="ConversationID"
    )
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="user_report_comments",
        db_column="UserID",
        blank=True,
        null=True,
    )
    message = models.TextField(db_column="MessageText")
    posted_at = models.DateTimeField(db_column="PostDateTime")

    class Meta:
        managed = False
        db_table = "ReportObjectConversationMessage_doc"


class ReportFragilityTags(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report = models.ForeignKey(
        "ReportDocs",
        models.DO_NOTHING,
        db_column="ReportObjectID",
        related_name="fragility_tags",
    )
    fragility_tag = models.ForeignKey(
        FragilityTag,
        models.DO_NOTHING,
        db_column="FragilityTagID",
        related_name="reports",
    )

    class Meta:
        managed = False
        db_table = "ReportObjectDocFragilityTags"
        unique_together = (("report", "fragility_tag"),)


class ReportMaintenanceLogs(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report = models.ForeignKey(
        "ReportDocs", models.DO_NOTHING, db_column="ReportObjectID", related_name="logs"
    )
    log = models.ForeignKey(
        MaintenanceLogs,
        models.DO_NOTHING,
        db_column="MaintenanceLogID",
        related_name="reports",
    )

    class Meta:
        managed = False
        db_table = "ReportObjectDocMaintenanceLogs"
        unique_together = (("report", "log"),)
        ordering = ["-log__maintained_at"]


class ReportTerms(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        "ReportDocs",
        models.DO_NOTHING,
        db_column="ReportObjectID",
        related_name="terms",
    )
    term = models.ForeignKey(
        "Terms", models.DO_NOTHING, db_column="TermId", related_name="report_docs"
    )

    class Meta:
        managed = False
        db_table = "ReportObjectDocTerms"
        unique_together = (("report_doc", "term"),)


class ReportImages(models.Model):
    image_id = models.AutoField(db_column="ImageID", primary_key=True)
    report_id = models.ForeignKey(
        Reports,
        db_column="ReportObjectID",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="imgs",
    )
    image_rank = models.IntegerField(db_column="ImageOrdinal")
    image_data = models.BinaryField(db_column="ImageData")
    image_source = models.TextField(db_column="ImageSource", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectImages_doc"


class Reportobjectruntime(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    runuserid = models.IntegerField(db_column="RunUserId", blank=True, null=True)
    runs = models.IntegerField(db_column="Runs", blank=True, null=True)
    runtime = models.DecimalField(
        db_column="RunTime", max_digits=10, decimal_places=2, blank=True, null=True
    )
    runweek = models.DateTimeField(db_column="RunWeek", blank=True, null=True)
    runweekstring = models.TextField(db_column="RunWeekString", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectRunTime"


class Reportobjecttopruns(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId", blank=True, null=True
    )
    name = models.TextField(db_column="Name", blank=True, null=True)
    runuserid = models.IntegerField(db_column="RunUserId", blank=True, null=True)
    runs = models.IntegerField(db_column="Runs", blank=True, null=True)
    runtime = models.DecimalField(
        db_column="RunTime", max_digits=10, decimal_places=2, blank=True, null=True
    )
    lastrun = models.TextField(db_column="LastRun", blank=True, null=True)
    reportobjecttypeid = models.IntegerField(
        db_column="ReportObjectTypeId", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "ReportObjectTopRuns"


class Reportobjectweightedrunrank(models.Model):
    reportobjectid = models.IntegerField()
    weighted_run_rank = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "ReportObjectWeightedRunRank"


class ReportDocs(models.Model):
    # doc_id = models.IntegerField(db_column="ReportObjectID", primary_key=True)
    ops_owner = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_doc_ops_owner",
        db_column="OperationalOwnerUserID",
        blank=True,
        null=True,
    )
    requester = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_doc_requester",
        db_column="Requester",
        blank=True,
        null=True,
    )
    project_url = models.TextField(db_column="GitLabProjectURL", blank=True, null=True)
    description = models.TextField(
        db_column="DeveloperDescription", blank=True, null=True
    )
    assumptions = models.TextField(db_column="KeyAssumptions", blank=True, null=True)
    org_value = models.ForeignKey(
        Organizationalvalue,
        models.DO_NOTHING,
        db_column="OrganizationalValueID",
        blank=True,
        null=True,
    )
    frequency = models.ForeignKey(
        RunFrequency,
        models.DO_NOTHING,
        db_column="EstimatedRunFrequencyID",
        blank=True,
        null=True,
    )
    fragility = models.ForeignKey(
        Fragility, models.DO_NOTHING, db_column="FragilityID", blank=True, null=True
    )
    executive_report = models.CharField(
        db_column="ExecutiveVisibilityYN", max_length=1, blank=True, null=True
    )
    maintenance_schedule = models.ForeignKey(
        MaintenanceSchedule,
        models.DO_NOTHING,
        db_column="MaintenanceScheduleID",
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDateTime", blank=True, null=True
    )
    _created_at = models.DateTimeField(
        db_column="CreatedDateTime", blank=True, null=True
    )
    created_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_doc_creator",
        db_column="CreatedBy",
        blank=True,
        null=True,
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="report_doc_modifier",
        db_column="UpdatedBy",
        blank=True,
        null=True,
    )
    enabled_for_hyperspace = models.CharField(
        db_column="EnabledForHyperspace", max_length=1, blank=True, null=True
    )
    do_not_purge = models.CharField(
        db_column="DoNotPurge", max_length=1, blank=True, null=True
    )
    hidden = models.CharField(db_column="Hidden", max_length=1, blank=True, null=True)

    report = models.OneToOneField(
        "Reports",
        models.DO_NOTHING,
        db_column="ReportObjectID",
        related_name="docs",
        primary_key=True,
    )

    class Meta:
        managed = False
        db_table = "ReportObject_doc"

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%d/%m/%y")
        return ""

    @property
    def modified_at(self):
        if self._created_at:
            return datetime.strftime(self._created_at, "%d/%m/%y")
        return ""


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(
        db_column="RolePermissionLinksId", primary_key=True
    )
    role_id = models.ForeignKey(
        "UserRoles",
        models.DO_NOTHING,
        db_column="RoleId",
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission_id = models.ForeignKey(
        "RolePermissions",
        models.DO_NOTHING,
        db_column="RolePermissionsId",
        blank=True,
        null=True,
        related_name="role_permission_links",
    )

    class Meta:
        managed = False
        db_table = "RolePermissionLinks"


class RolePermissions(models.Model):
    permissions_id = models.AutoField(db_column="RolePermissionsId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "RolePermissions"


class Searchtable(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    itemid = models.IntegerField(db_column="ItemId", blank=True, null=True)
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)
    itemtype = models.CharField(
        db_column="ItemType", max_length=100, blank=True, null=True
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, null=True
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "SearchTable"


class SearchBasicsearchdata(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    itemid = models.IntegerField(db_column="ItemId", blank=True, null=True)
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)
    itemtype = models.CharField(
        db_column="ItemType", max_length=100, blank=True, null=True
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, null=True
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, null=True)
    hidden = models.IntegerField(db_column="Hidden", blank=True, null=True)
    visibletype = models.IntegerField(db_column="VisibleType", blank=True, null=True)
    orphaned = models.IntegerField(db_column="Orphaned", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Search_BasicSearchData"


class SearchBasicsearchdataSmall(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    itemid = models.IntegerField(db_column="ItemId", blank=True, null=True)
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)
    itemtype = models.CharField(
        db_column="ItemType", max_length=100, blank=True, null=True
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, null=True
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, null=True)
    hidden = models.IntegerField(db_column="Hidden", blank=True, null=True)
    visibletype = models.IntegerField(db_column="VisibleType", blank=True, null=True)
    orphaned = models.IntegerField(db_column="Orphaned", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Search_BasicSearchData_Small"


class SearchReportobjectsearchdata(models.Model):
    primk = models.AutoField(primary_key=True)
    id = models.IntegerField(db_column="Id")
    columnname = models.TextField(db_column="ColumnName", blank=True, null=True)
    value = models.TextField(db_column="Value", blank=True, null=True)
    lastmodifieddate = models.DateTimeField(
        db_column="LastModifiedDate", blank=True, null=True
    )
    epicmasterfile = models.CharField(
        db_column="EpicMasterFile", max_length=3, blank=True, null=True
    )
    defaultvisibilityyn = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, null=True
    )
    orphanedreportobjectyn = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, null=True
    )
    reportobjecttypeid = models.IntegerField(
        db_column="ReportObjectTypeID", blank=True, null=True
    )
    authoruserid = models.IntegerField(db_column="AuthorUserId", blank=True, null=True)
    lastmodifiedbyuserid = models.IntegerField(
        db_column="LastModifiedByUserID", blank=True, null=True
    )
    epicreporttemplateid = models.DecimalField(
        db_column="EpicReportTemplateId",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    sourceserver = models.CharField(db_column="SourceServer", max_length=255)
    sourcedb = models.CharField(db_column="SourceDB", max_length=255)
    sourcetable = models.CharField(db_column="SourceTable", max_length=255)
    documented = models.IntegerField(db_column="Documented")
    docownerid = models.IntegerField(db_column="DocOwnerId", blank=True, null=True)
    docrequesterid = models.IntegerField(
        db_column="DocRequesterId", blank=True, null=True
    )
    docorgvalueid = models.IntegerField(
        db_column="DocOrgValueId", blank=True, null=True
    )
    docrunfreqid = models.IntegerField(db_column="DocRunFreqId", blank=True, null=True)
    docfragid = models.IntegerField(db_column="DocFragId", blank=True, null=True)
    docexecvis = models.CharField(
        db_column="DocExecVis", max_length=1, blank=True, null=True
    )
    docmainschedid = models.IntegerField(
        db_column="DocMainSchedId", blank=True, null=True
    )
    doclastupdated = models.DateTimeField(
        db_column="DocLastUpdated", blank=True, null=True
    )
    doccreated = models.DateTimeField(db_column="DocCreated", blank=True, null=True)
    doccreatedby = models.IntegerField(db_column="DocCreatedBy", blank=True, null=True)
    docupdatedby = models.IntegerField(db_column="DocUpdatedBy", blank=True, null=True)
    dochypeenabled = models.CharField(
        db_column="DocHypeEnabled", max_length=1, blank=True, null=True
    )
    docdonotpurge = models.CharField(
        db_column="DocDoNotPurge", max_length=1, blank=True, null=True
    )
    dochidden = models.CharField(
        db_column="DocHidden", max_length=1, blank=True, null=True
    )
    twoyearruns = models.IntegerField(db_column="TwoYearRuns", blank=True, null=True)
    oneyearruns = models.IntegerField(db_column="OneYearRuns", blank=True, null=True)
    sixmonthsruns = models.IntegerField(
        db_column="SixMonthsRuns", blank=True, null=True
    )
    onemonthruns = models.IntegerField(db_column="OneMonthRuns", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Search_ReportObjectSearchData"


class Shareditems(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    sharedfromuserid = models.IntegerField(
        db_column="SharedFromUserId", blank=True, null=True
    )
    sharedtouserid = models.IntegerField(
        db_column="SharedToUserId", blank=True, null=True
    )
    url = models.TextField(db_column="Url", blank=True, null=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    sharedate = models.DateTimeField(db_column="ShareDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "SharedItems"


class StrategicImportance(models.Model):
    strategic_importance_id = models.AutoField(
        db_column="StrategicImportanceId", primary_key=True
    )
    name = models.TextField(db_column="Name", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "StrategicImportance"


class Terms(models.Model):
    term_id = models.AutoField(db_column="TermId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=255, blank=True, null=True)
    summary = models.CharField(
        db_column="Summary", max_length=4000, blank=True, null=True
    )
    technical_definition = models.TextField(
        db_column="TechnicalDefinition", blank=True, null=True
    )
    approved = models.CharField(
        db_column="ApprovedYN", max_length=1, blank=True, null=True
    )
    _approved_at = models.DateTimeField(
        db_column="ApprovalDateTime", blank=True, null=True
    )
    approved_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="term_approve_user",
        db_column="ApprovedByUserId",
        blank=True,
        null=True,
    )
    has_external_standard = models.CharField(
        db_column="HasExternalStandardYN", max_length=1, blank=True, null=True
    )
    external_standard_url = models.CharField(
        db_column="ExternalStandardUrl", max_length=4000, blank=True, null=True
    )
    _valid_from = models.DateTimeField(
        db_column="ValidFromDateTime", blank=True, null=True
    )
    _valid_to = models.DateTimeField(db_column="ValidToDateTime", blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="term_modifier",
        db_column="UpdatedByUserId",
        blank=True,
        null=True,
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdatedDateTime", blank=True, null=True
    )

    @property
    def approved_at(self):
        if self._approved_at:
            return datetime.strftime(self._approved_at, "%-m/%-d/%y")
        return ""

    @property
    def valid_from(self):
        if self._valid_from:
            return datetime.strftime(self._valid_from, "%-m/%-d/%y")
        return ""

    @property
    def valid_to(self):
        if self._valid_to:
            return datetime.strftime(self._valid_to, "%-m/%-d/%y")
        return ""

    @property
    def modified_at(self):
        if self._modified_at:
            return datetime.strftime(self._modified_at, "%-m/%-d/%y")
        return ""

    class Meta:
        managed = False
        db_table = "Term"

    def __str__(self):
        return self.name


class TermCommentStream(models.Model):
    stream_id = models.AutoField(db_column="TermConversationId", primary_key=True)
    term_id = models.ForeignKey(Terms, models.DO_NOTHING, db_column="TermId")

    class Meta:
        managed = False
        db_table = "TermConversation"


class TermComments(models.Model):
    comment_id = models.AutoField(
        db_column="TermConversationMessageID", primary_key=True
    )
    stream_id = models.ForeignKey(
        TermCommentStream, models.DO_NOTHING, db_column="TermConversationId"
    )
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="user_term_comments",
    )
    message = models.CharField(db_column="MessageText", max_length=4000)
    posted_at = models.DateTimeField(db_column="PostDateTime")

    class Meta:
        managed = False
        db_table = "TermConversationMessage"


class FavoriteFolders(models.Model):
    folder_id = models.AutoField(db_column="UserFavoriteFolderId", primary_key=True)
    name = models.TextField(db_column="FolderName", blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="favorite_folders",
    )
    rank = models.IntegerField(db_column="FolderRank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserFavoriteFolders"
        ordering = ["rank"]


class Favorites(models.Model):
    favorite_id = models.AutoField(db_column="UserFavoritesId", primary_key=True)
    item_type = models.TextField(db_column="ItemType", blank=True, null=True)
    rank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="favorites",
    )
    name = models.TextField(db_column="ItemName", blank=True, null=True)
    folder = models.ForeignKey(
        FavoriteFolders,
        models.DO_NOTHING,
        db_column="FolderId",
        blank=True,
        null=True,
        related_name="favorites",
    )

    class Meta:
        managed = False
        db_table = "UserFavorites"
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
            return Reports.objects.get(report_id=self.item_id).certification_tag

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
    preference_id = models.AutoField(db_column="UserPreferenceId", primary_key=True)
    key = models.TextField(db_column="ItemType", blank=True, null=True)
    value = models.IntegerField(db_column="ItemValue", blank=True, null=True)
    item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="user_preferences",
    )

    class Meta:
        managed = False
        db_table = "UserPreferences"


class UserRolelinks(models.Model):
    rolelinks_id = models.AutoField(db_column="UserRoleLinksId", primary_key=True)
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role_id = models.ForeignKey(
        "UserRoles",
        models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="role_links",
    )

    class Meta:
        managed = False
        db_table = "UserRoleLinks"


class UserRoles(models.Model):
    role_id = models.AutoField(db_column="UserRolesId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserRoles"


class UserNamedata(models.Model):
    userid = models.IntegerField(db_column="UserId", primary_key=True)
    fullname = models.TextField(db_column="Fullname", blank=True, null=True)
    firstname = models.TextField(db_column="Firstname", blank=True, null=True)
    lastname = models.TextField(db_column="Lastname", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "User_NameData"
