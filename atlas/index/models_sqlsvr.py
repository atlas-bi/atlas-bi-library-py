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

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property


class ReportGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    group = models.ForeignKey(
        "Groups",
        models.DO_NOTHING,
        db_column="GroupId",
        related_name="reports",
    )
    report = models.ForeignKey(
        "Reports",
        models.DO_NOTHING,
        db_column="ReportId",
        related_name="groups",
    )
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportGroupsMemberships"


class Reports(models.Model):
    report_id = models.AutoField(db_column="ReportObjectID", primary_key=True)
    report_key = models.TextField(
        db_column="ReportObjectBizKey", blank=True, default=""
    )
    type = models.ForeignKey(
        "ReportTypes",
        models.DO_NOTHING,
        db_column="ReportObjectTypeID",
        blank=True,
        null=True,
        related_name="reports",
    )
    name = models.TextField(db_column="Name", blank=True, default="")
    title = models.TextField(db_column="DisplayTitle", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    detailed_description = models.TextField(
        db_column="DetailedDescription", blank=True, default=""
    )
    system_description = models.TextField(
        db_column="RepositoryDescription", blank=True, default=""
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
        db_column="LastModifiedDate", blank=True, auto_now=True
    )
    system_run_url = models.TextField(
        db_column="ReportObjectURL", blank=True, default=""
    )
    system_identifier = models.CharField(
        db_column="EpicMasterFile", max_length=3, blank=True, default=""
    )
    system_id = models.DecimalField(
        db_column="EpicRecordID",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    system_template_id = models.DecimalField(
        db_column="EpicReportTemplateId",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    system_catalog_id = models.CharField(
        db_column="ReportServerCatalogID", max_length=50, blank=True, default=""
    )
    visible = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, default=""
    )
    orphan = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, default=""
    )
    system_path = models.TextField(db_column="ReportServerPath", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    availability = models.TextField(db_column="Availability", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObject"

    def __str__(self):
        return self.title or self.name

    @cached_property
    def is_certified(self):
        return self.tags.filter(
            tag__name__in=["Analytics Certified", "Analytics Reviewed"]
        ).exists()

    def has_docs(self):
        return hasattr(self, "docs")

    @cached_property
    def get_group_ids(self):
        return self.groups.all().values_list("group__group_id", flat=True)

    @property
    def friendly_name(self):
        return self.title or self.name

    def get_absolute_url(self):
        return reverse("report:item", kwargs={"pk": self.pk})

    def get_absolute__maint_status_url(self):
        return reverse("report:maint_status", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self):
        return reverse("report:edit", kwargs={"pk": self.pk})

    # def system_run_url(self, in_system):
    #     return "123.123"

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

    @property
    def modified_at(self):
        if self._modified_at:
            return self._modified_at  # datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""


class ReportParameters(models.Model):
    parameter_id = models.AutoField(
        db_column="ReportObjectParameterId", primary_key=True
    )  # Field name made lowercase.
    report = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="parameters",
    )
    name = models.TextField(
        db_column="ParameterName", blank=True, null=True
    )  # Field name made lowercase.
    value = models.TextField(
        db_column="ParameterValue", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectParameters"


class ReportAttachments(models.Model):
    attachment_id = models.AutoField(
        db_column="ReportObjectAttachmentId", primary_key=True
    )  # Field name made lowercase.
    report = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="attachments",
    )
    name = models.TextField(db_column="Name")  # Field name made lowercase.
    path = models.TextField(db_column="Path")  # Field name made lowercase.
    _created_at = models.DateTimeField(db_column="CreationDate", blank=True, null=True)
    source = models.TextField(db_column="Source", blank=True, null=True)
    type = models.TextField(db_column="Type", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectAttachments"


class ReportTags(models.Model):
    tag_id = models.AutoField(
        db_column="TagID", primary_key=True
    )  # Field name made lowercase.
    system_id = models.DecimalField(
        db_column="EpicTagID", max_digits=18, decimal_places=0, blank=True, null=True
    )  # Field name made lowercase.
    name = models.CharField(
        db_column="TagName", max_length=200, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectTags"


class Tags(models.Model):
    tag_id = models.AutoField(db_column="TagId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=450, blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    priority = models.IntegerField(db_column="Priority", blank=True, null=True)
    show_in_header = models.TextField(db_column="ShowInHeader", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Tags"

    def __str__(self):
        return self.name

    def usage(self):
        return self.reports.count()


class ReportSystemTagLinks(models.Model):
    link_id = models.AutoField(
        db_column="TagMembershipID", primary_key=True
    )  # Field name made lowercase.
    report = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        default="",
        related_name="system_tag_links",
    )

    tag = models.ForeignKey(
        ReportTags,
        models.DO_NOTHING,
        db_column="TagID",
        related_name="system_report_links",
    )
    line = models.IntegerField(
        db_column="Line", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectTagMemberships"


class ReportTagLinks(models.Model):
    link_id = models.AutoField(
        db_column="ReportTagLinkId", primary_key=True
    )  # Field name made lowercase.
    report = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportId",
        blank=True,
        default="",
        related_name="tags",
    )
    tag = models.ForeignKey(
        Tags, models.DO_NOTHING, db_column="TagId", related_name="reports"
    )
    show_in_header = models.TextField(db_column="ShowInHeader", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportTagLinks"


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
        default="",
        related_name="queries",
    )
    query = models.TextField(db_column="Query", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    sourceserver = models.TextField(
        db_column="SourceServer", blank=True, null=True
    )  # Field name made lowercase.
    language = models.TextField(
        db_column="Language", blank=True, null=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

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
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="RunUserID",
        blank=True,
        default="",
        related_name="report_runs",
    )
    start_time = models.DateTimeField(db_column="RunStartTime", blank=True, null=True)
    duration_seconds = models.IntegerField(
        db_column="RunDurationSeconds", blank=True, null=True
    )
    status = models.CharField(
        db_column="RunStatus", max_length=100, blank=True, default=""
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
    report = models.ForeignKey(
        Reports,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        default="",
        related_name="user_subscriptions",
    )
    user_id = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        default="",
        related_name="report_subscriptions",
    )
    unique_id = models.TextField(db_column="SubscriptionId", blank=True, default="")
    inactive = models.IntegerField(db_column="InactiveFlags", blank=True, null=True)
    email_list = models.TextField(db_column="EmailList", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    status = models.TextField(db_column="LastStatus", blank=True, default="")
    last_run = models.DateTimeField(db_column="LastRunTime", blank=True, null=True)
    email = models.TextField(db_column="SubscriptionTo", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectSubscriptions"


class ReportTypes(models.Model):
    type_id = models.AutoField(db_column="ReportObjectTypeID", primary_key=True)
    name = models.TextField(db_column="Name")
    short_name = models.TextField(db_column="ShortName", blank=True, default="")
    code = models.TextField(db_column="DefaultEpicMasterFile", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    visible = models.CharField(
        db_column="Visible", max_length=1, blank=True, null=True
    )  # F

    class Meta:
        managed = False
        db_table = "ReportObjectType"

    def __str__(self):
        return self.name

    @property
    def short(self):
        return self.short_name or self.name


class Users(AbstractUser, PermissionsMixin):
    user_id = models.AutoField(db_column="UserID", primary_key=True)
    username = models.TextField(db_column="Username")
    employee_id = models.TextField(db_column="EmployeeID", blank=True, default="")
    account_name = models.TextField(db_column="AccountName", blank=True, default="")
    display_name = models.TextField(db_column="DisplayName", blank=True, default="")
    _full_name = models.TextField(db_column="FullName", blank=True, default="")
    _first_name = models.TextField(db_column="FirstName", blank=True, default="")
    full_name = models.TextField(db_column="Fullname_calc", blank=True, null=True)
    first_name = models.TextField(db_column="Firstname_calc", blank=True, null=True)
    last_name = models.TextField(db_column="LastName", blank=True, default="")
    department = models.TextField(db_column="Department", blank=True, default="")
    title = models.TextField(db_column="Title", blank=True, default="")
    phone = models.TextField(db_column="Phone", blank=True, default="")
    email = models.TextField(db_column="Email", blank=True, default="")
    base = models.TextField(db_column="Base", blank=True, default="")
    system_id = models.TextField(db_column="EpicId", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    last_login = models.DateTimeField(db_column="LastLogin", blank=True, null=True)
    is_active = True
    date_joined = None
    # is_superuser = True  # check permissions for admin
    is_staff = True

    class Meta:
        managed = False
        db_table = "User"

    def __str__(self):
        return self.full_name

    @cached_property
    def is_superuser(self):
        # either an admin, or in a group that is an admin.
        return (
            self.role_links.filter(role__name="Administrator").exists()
            or self.group_links.filter(
                group__role_links__role__name="Administrator"
            ).exists()
        )

    def get_user_permissions(self, obj=None):
        # if an active admin, return all permissions
        if (
            not self.user_preferences.filter(key="AdminDisabled").exists()
            and self.is_superuser
        ):
            return RolePermissions.objects.all().values_list("name", flat=True)

        # otherwise get the users group permissions, and add in the default user permissions.
        return (
            self.role_links.exclude(role__name__in=["Administrator", "User"])
            .values_list("role__permission_links__permission__name", flat=True)
            .union(
                RolePermissions.objects.filter(
                    role_permission_links__role__name="User"
                ).values_list("name", flat=True)
            )
        )

    def get_group_permissions(self, obj=None):
        # don't need to get admin or user permissions here, they are passed from the user permissions check.
        return (
            UserRoles.objects.filter(
                name__in=self.group_links.values_list(
                    "group__role_links__role__name", flat=True
                )
            )
            .exclude(name__in=["Administrator", "User"])
            .values_list("permission_links__permission__name", flat=True)
        )

    @cached_property
    def get_group_ids(self):
        return self.group_links.all().values_list("group__group_id", flat=True)

    @cached_property
    def get_all_permissions(self, obj=None):
        return self.get_user_permissions().union(self.get_group_permissions())

    def has_perm(self, perm, obj=None):
        return perm in self.get_all_permissions

    def has_perms(self, perms, obj=None):
        return set(perms) < set(self.get_all_permissions)
        pass

    def get_roles(self):
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))

    def get_absolute_url(self):
        return reverse("user:profile", kwargs={"pk": self.pk})

    @cached_property
    def get_preferences(self):
        # return users preferences as queriable object
        return dict(self.user_preferences.values_list("key", "value"))

    @cached_property
    def get_starred_reports(self):
        # return all favorites
        return list(self.starred_reports.values_list("report__report_id", flat=True))

    @cached_property
    def get_starred_initiatives(self):
        # return all favorites
        return list(
            self.starred_initiatives.values_list("initiative__initiative_id", flat=True)
        )

    @cached_property
    def get_starred_collections(self):
        # return all favorites
        return list(
            self.starred_collections.values_list("collection__collection_id", flat=True)
        )

    @cached_property
    def get_starred_terms(self):
        # return all favorites
        return list(self.starred_terms.values_list("term__term_id", flat=True))

    @cached_property
    def get_starred_users(self):
        # return all favorites
        return list(self.starred_users.values_list("user__user_id", flat=True))

    @cached_property
    def get_starred_groups(self):
        # return all favorites
        return list(self.starred_groups.values_list("group__group_id", flat=True))

    @cached_property
    def get_starred_searches(self):
        # return all favorites
        return list(self.starred_searches.values_list("search__search_id", flat=True))

    @property
    def password(self):
        return 123

    @property
    def first_initial(self):
        return self.full_name[0]


class Groups(models.Model):
    group_id = models.AutoField(db_column="GroupId", primary_key=True)
    account_name = models.TextField(db_column="AccountName", blank=True, default="")
    name = models.TextField(db_column="GroupName", blank=True, default="")
    email = models.TextField(db_column="GroupEmail", blank=True, default="")
    group_type = models.TextField(db_column="GroupType", blank=True, default="")
    source = models.TextField(db_column="GroupSource", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    epic_id = models.TextField(db_column="EpicId", blank=True, default="")

    class Meta:
        managed = False
        db_table = "UserGroups"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("group:details", kwargs={"pk": self.pk})

    def get_roles(self):
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    user = models.ForeignKey(
        Users,
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        default="",
        related_name="group_links",
    )
    group = models.ForeignKey(
        Groups,
        models.DO_NOTHING,
        db_column="GroupId",
        blank=True,
        default="",
        related_name="user_memberships",
    )
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserGroupsMembership"


class Analytics(models.Model):
    analytics_id = models.AutoField(db_column="Id", primary_key=True)
    language = models.TextField(blank=True, default="")
    useragent = models.TextField(db_column="userAgent", blank=True, default="")
    hostname = models.TextField(blank=True, default="")
    href = models.TextField(blank=True, default="")
    protocol = models.TextField(blank=True, default="")
    search = models.TextField(blank=True, default="")
    pathname = models.TextField(blank=True, default="")
    unique_id = models.TextField(db_column="hash", blank=True, default="")
    screen_height = models.TextField(db_column="screenHeight", blank=True, default="")
    screen_width = models.TextField(db_column="screenWidth", blank=True, default="")
    origin = models.TextField(blank=True, default="")
    load_time = models.TextField(db_column="loadTime", blank=True, default="")
    access_date = models.DateTimeField(
        db_column="accessDateTime", blank=True, null=True
    )
    referrer = models.TextField(blank=True, default="")
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="analytics",
    )
    zoom = models.FloatField(db_column="Zoom", blank=True, default="")
    epic = models.IntegerField(db_column="Epic", blank=True, null=True)
    page_id = models.TextField(db_column="pageId", blank=True, default="")
    session_id = models.TextField(db_column="sessionId", blank=True, default="")
    page_time = models.IntegerField(db_column="pageTime", blank=True, null=True)
    update_time = models.DateTimeField(db_column="updateTime", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Analytics"


class Initiatives(models.Model):
    initiative_id = models.AutoField(db_column="InitiativeID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
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
        related_name="initiatives",
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        models.DO_NOTHING,
        db_column="StrategicImportance",
        blank=True,
        null=True,
        related_name="initiatives",
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, auto_now=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="initiative_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )
    hidden = models.CharField(db_column="Hidden", max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Initiative"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("initiative:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse("initiative:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self):
        return reverse("initiative:edit", kwargs={"pk": self.pk})

    def stars(self):
        return self.stars.count()

    @property
    def modified_at(self):
        if self._modified_at:
            return self._modified_at  # datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""


class Collections(models.Model):
    collection_id = models.AutoField(db_column="CollectionId", primary_key=True)

    initiative = models.ForeignKey(
        "Initiatives",
        models.DO_NOTHING,
        db_column="InitiativeId",
        blank=True,
        null=True,
        related_name="collections",
    )

    name = models.TextField(db_column="Name", blank=True, default="")
    search_summary = models.TextField(db_column="Purpose", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, auto_now=True
    )
    modified_by = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        related_name="collection_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )

    hidden = models.CharField(
        max_length=1,
        blank=True,
        default="",
        db_column="Hidden",
    )

    class Meta:
        managed = False
        db_table = "Collection"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("collection:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse("collection:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self):
        return reverse("collection:edit", kwargs={"pk": self.pk})

    @property
    def modified_at(self):
        if self._modified_at:
            return self._modified_at  # datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""


class CollectionReports(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report = models.ForeignKey(
        "Reports",
        models.DO_NOTHING,
        db_column="ReportId",
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        models.DO_NOTHING,
        db_column="CollectionId",
        blank=True,
        null=True,
        related_name="reports",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "CollectionReport"

    def __str__(self):
        return self.report.friendly_name

    def get_absolute_delete_url(self):
        return reverse(
            "collection:report_delete",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )

    def get_absolute_edit_url(self):
        return reverse(
            "collection:report_edit",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )


class CollectionTerms(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    term = models.ForeignKey(
        "Terms",
        models.DO_NOTHING,
        db_column="TermId",
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        models.DO_NOTHING,
        db_column="CollectionId",
        blank=True,
        null=True,
        related_name="terms",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "CollectionTerm"

    def __str__(self):
        return self.term.name

    def get_absolute_delete_url(self):
        return reverse(
            "collection:term_delete",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )

    def get_absolute_edit_url(self):
        return reverse(
            "collection:term_edit",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )


class RunFrequency(models.Model):
    frequency_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "EstimatedRunFrequency"

    def __str__(self):
        return self.name

    def usage(self):
        return self.report_docs.count()


class FinancialImpact(models.Model):
    impact_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "FinancialImpact"

    def __str__(self):
        return self.name

    def usage(self):
        return self.initiatives.count()


class Fragility(models.Model):
    fragility_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Fragility"

    def __str__(self):
        return self.name

    def usage(self):
        return self.report_docs.count()


class FragilityTag(models.Model):
    tag_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "FragilityTag"

    def __str__(self):
        return self.name

    def usage(self):
        return self.report_docs.count()


class GlobalSettings(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    value = models.TextField(db_column="Value", blank=True, default="")

    class Meta:
        managed = False
        db_table = "GlobalSiteSettings"


class MailConversations(models.Model):
    conversation_id = models.AutoField(db_column="ConversationId", primary_key=True)
    message = models.ForeignKey(
        "MailMessages",
        models.DO_NOTHING,
        db_column="MessageId",
        related_name="conversations",
    )

    class Meta:
        managed = False
        db_table = "Mail_Conversations"


class MailDrafts(models.Model):
    draft_id = models.AutoField(db_column="DraftId", primary_key=True)
    subject = models.TextField(db_column="Subject", blank=True, default="")
    message = models.TextField(db_column="Message", blank=True, default="")
    editdate = models.DateTimeField(db_column="EditDate", blank=True, null=True)
    messagetypeid = models.IntegerField(
        db_column="MessageTypeId", blank=True, null=True
    )
    fromuserid = models.IntegerField(db_column="FromUserId", blank=True, null=True)
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, default=""
    )
    recipients = models.TextField(db_column="Recipients", blank=True, default="")
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
    folder_message_id = models.AutoField(db_column="Id", primary_key=True)
    folder = models.ForeignKey(
        "MailFolders",
        models.DO_NOTHING,
        db_column="FolderId",
        blank=True,
        null=True,
        related_name="folder_messages",
    )
    message = models.ForeignKey(
        "MailMessages",
        models.DO_NOTHING,
        db_column="MessageId",
        blank=True,
        null=True,
        related_name="message_folders",
    )

    class Meta:
        managed = False
        db_table = "Mail_FolderMessages"


class MailFolders(models.Model):
    folder_id = models.AutoField(db_column="FolderId", primary_key=True)
    parentfolderid = models.IntegerField(
        db_column="ParentFolderId", blank=True, null=True
    )
    userid = models.IntegerField(db_column="UserId", blank=True, null=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Mail_Folders"


class MailMessagetype(models.Model):
    messagetypeid = models.AutoField(db_column="MessageTypeId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Mail_MessageType"


class MailMessages(models.Model):
    message_id = models.AutoField(db_column="MessageId", primary_key=True)
    subject = models.TextField(db_column="Subject", blank=True, default="")
    message = models.TextField(db_column="Message", blank=True, default="")
    senddate = models.DateTimeField(db_column="SendDate", blank=True, null=True)
    message_type = models.ForeignKey(
        MailMessagetype,
        models.DO_NOTHING,
        db_column="MessageTypeId",
        blank=True,
        null=True,
        related_name="messages",
    )
    fromuserid = models.IntegerField(db_column="FromUserId", blank=True, null=True)
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, default=""
    )

    class Meta:
        managed = False
        db_table = "Mail_Messages"


class MailRecipients(models.Model):
    recipient_id = models.AutoField(db_column="Id", primary_key=True)
    message = models.ForeignKey(
        MailMessages,
        models.DO_NOTHING,
        db_column="MessageId",
        blank=True,
        null=True,
        related_name="messages",
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
        db_column="MaintenanceDate", blank=True, auto_now=True
    )
    comments = models.TextField(db_column="Comment", blank=True, default="")
    status = models.ForeignKey(
        "MaintenancelogStatus",
        models.DO_NOTHING,
        db_column="MaintenanceLogStatusID",
        blank=True,
        null=True,
        related_name="logs",
    )

    report = models.ForeignKey(
        "ReportDocs",
        models.DO_NOTHING,
        db_column="ReportId",
        related_name="maintenance_logs",
    )

    class Meta:
        managed = False
        db_table = "MaintenanceLog"
        ordering = ["maintained_at"]


class MaintenanceLogStatus(models.Model):
    status_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name")

    class Meta:
        managed = False
        db_table = "MaintenanceLogStatus"

    def __str__(self):
        return self.name

    def usage(self):
        return self.logs.count()


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name")

    class Meta:
        managed = False
        db_table = "MaintenanceSchedule"

    def __str__(self):
        return self.name

    def usage(self):
        return self.report_docs.count()


class OrganizationalValue(models.Model):
    value_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "OrganizationalValue"

    def __str__(self):
        return self.name

    def usage(self):
        return self.report_docs.count()


class ReportFragilityTags(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        "ReportDocs",
        models.DO_NOTHING,
        db_column="ReportObjectID",
        related_name="fragility_tags",
    )
    fragility_tag = models.ForeignKey(
        FragilityTag,
        models.DO_NOTHING,
        db_column="FragilityTagID",
        related_name="report_docs",
    )

    class Meta:
        managed = False
        db_table = "ReportObjectDocFragilityTags"
        unique_together = (("report_doc", "fragility_tag"),)


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
    report = models.ForeignKey(
        Reports,
        db_column="ReportObjectID",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="imgs",
    )
    rank = models.IntegerField(db_column="ImageOrdinal")
    data = models.BinaryField(db_column="ImageData")
    source = models.TextField(db_column="ImageSource", blank=True, default="")

    class Meta:
        managed = False
        db_table = "ReportObjectImages_doc"

    def get_absolute_url(self):
        return reverse(
            "report:image", kwargs={"pk": self.pk, "report_id": self.report.report_id}
        )


class Reportobjectruntime(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    runuserid = models.IntegerField(db_column="RunUserId", blank=True, null=True)
    runs = models.IntegerField(db_column="Runs", blank=True, null=True)
    runtime = models.DecimalField(
        db_column="RunTime", max_digits=10, decimal_places=2, blank=True, null=True
    )
    runweek = models.DateTimeField(db_column="RunWeek", blank=True, null=True)
    runweekstring = models.TextField(db_column="RunWeekString", blank=True, default="")

    class Meta:
        managed = False
        db_table = "ReportObjectRunTime"


class Reportobjecttopruns(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId", blank=True, null=True
    )
    name = models.TextField(db_column="Name", blank=True, default="")
    runuserid = models.IntegerField(db_column="RunUserId", blank=True, null=True)
    runs = models.IntegerField(db_column="Runs", blank=True, null=True)
    runtime = models.DecimalField(
        db_column="RunTime", max_digits=10, decimal_places=2, blank=True, null=True
    )
    lastrun = models.TextField(db_column="LastRun", blank=True, default="")
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
    external_url = models.TextField(
        db_column="GitLabProjectURL", blank=True, default=""
    )
    description = models.TextField(
        db_column="DeveloperDescription", blank=True, default=""
    )
    assumptions = models.TextField(db_column="KeyAssumptions", blank=True, default="")
    org_value = models.ForeignKey(
        OrganizationalValue,
        models.DO_NOTHING,
        db_column="OrganizationalValueID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    frequency = models.ForeignKey(
        RunFrequency,
        models.DO_NOTHING,
        db_column="EstimatedRunFrequencyID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    fragility = models.ForeignKey(
        Fragility,
        models.DO_NOTHING,
        db_column="FragilityID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    executive_report = models.CharField(
        db_column="ExecutiveVisibilityYN", max_length=1, blank=True, default=""
    )
    maintenance_schedule = models.ForeignKey(
        MaintenanceSchedule,
        models.DO_NOTHING,
        db_column="MaintenanceScheduleID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    _modified_at = models.DateTimeField(
        db_column="LastUpdateDateTime", blank=True, auto_now=True
    )
    _created_at = models.DateTimeField(
        db_column="CreatedDateTime", blank=True, auto_now_add=True
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
        db_column="EnabledForHyperspace", max_length=1, blank=True, default=""
    )
    do_not_purge = models.CharField(
        db_column="DoNotPurge", max_length=1, blank=True, default=""
    )
    hidden = models.CharField(db_column="Hidden", max_length=1, blank=True, default="")

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
            return self._modified_at  # datetime.strftime(self._modified_at, "%m/%d/%y")
        return ""

    @property
    def created_at(self):
        if self._created_at:
            return self._created_at  # datetime.strftime(self._created_at, "%m/%d/%y")
        return ""


class ReportTickets(models.Model):
    ticket_id = models.AutoField(
        db_column="ServiceRequestId", primary_key=True
    )  # Field name made lowercase.
    number = models.TextField(
        db_column="TicketNumber", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        blank=True,
        null=True,
        related_name="tickets",
    )
    url = models.TextField(
        db_column="TicketUrl", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportServiceRequests"

    def __str__(self):
        return self.number


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(
        db_column="RolePermissionLinksId", primary_key=True
    )
    role = models.ForeignKey(
        "UserRoles",
        models.DO_NOTHING,
        db_column="RoleId",
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission = models.ForeignKey(
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

    def __str__(self):
        return self.permission.name


class RolePermissions(models.Model):
    permissions_id = models.AutoField(db_column="RolePermissionsId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = False
        db_table = "RolePermissions"

    def __str__(self):
        return self.name


class Searchtable(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    itemid = models.IntegerField(db_column="ItemId", blank=True, null=True)
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)
    itemtype = models.CharField(
        db_column="ItemType", max_length=100, blank=True, default=""
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, default=""
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, default="")

    class Meta:
        managed = False
        db_table = "SearchTable"


class SearchBasicsearchdata(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    itemid = models.IntegerField(db_column="ItemId", blank=True, null=True)
    typeid = models.IntegerField(db_column="TypeId", blank=True, null=True)
    itemtype = models.CharField(
        db_column="ItemType", max_length=100, blank=True, default=""
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, default=""
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, default="")
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
        db_column="ItemType", max_length=100, blank=True, default=""
    )
    itemrank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
    searchfielddescription = models.CharField(
        db_column="SearchFieldDescription", max_length=100, blank=True, default=""
    )
    searchfield = models.TextField(db_column="SearchField", blank=True, default="")
    hidden = models.IntegerField(db_column="Hidden", blank=True, null=True)
    visibletype = models.IntegerField(db_column="VisibleType", blank=True, null=True)
    orphaned = models.IntegerField(db_column="Orphaned", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Search_BasicSearchData_Small"


class SearchReportobjectsearchdata(models.Model):
    primk = models.AutoField(primary_key=True)
    id = models.IntegerField(db_column="Id")
    columnname = models.TextField(db_column="ColumnName", blank=True, default="")
    value = models.TextField(db_column="Value", blank=True, default="")
    lastmodifieddate = models.DateTimeField(
        db_column="LastModifiedDate", blank=True, null=True
    )
    epicmasterfile = models.CharField(
        db_column="EpicMasterFile", max_length=3, blank=True, default=""
    )
    defaultvisibilityyn = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, default=""
    )
    orphanedreportobjectyn = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, default=""
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
        db_column="DocExecVis", max_length=1, blank=True, default=""
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
        db_column="DocHypeEnabled", max_length=1, blank=True, default=""
    )
    docdonotpurge = models.CharField(
        db_column="DocDoNotPurge", max_length=1, blank=True, default=""
    )
    dochidden = models.CharField(
        db_column="DocHidden", max_length=1, blank=True, default=""
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
    url = models.TextField(db_column="Url", blank=True, default="")
    name = models.TextField(db_column="Name", blank=True, default="")
    sharedate = models.DateTimeField(db_column="ShareDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "SharedItems"


class StrategicImportance(models.Model):
    importance_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "StrategicImportance"

    def __str__(self):
        return self.name

    def usage(self):
        return self.initiatives.count()


class Terms(models.Model):
    term_id = models.AutoField(db_column="TermId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=255, blank=True, default="")
    summary = models.TextField(db_column="Summary", blank=True, default="")
    technical_definition = models.TextField(
        db_column="TechnicalDefinition", blank=True, default=""
    )
    approved = models.CharField(
        db_column="ApprovedYN", max_length=1, blank=True, default=""
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
        db_column="HasExternalStandardYN", max_length=1, blank=True, default=""
    )
    external_standard_url = models.TextField(
        db_column="ExternalStandardUrl", blank=True, default=""
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
        db_column="LastUpdatedDateTime", blank=True, auto_now=True
    )

    class Meta:
        managed = False
        db_table = "Term"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("term:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self):
        return reverse("term:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self):
        return reverse("term:edit", kwargs={"pk": self.pk})

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


class FavoriteFolders(models.Model):
    folder_id = models.AutoField(db_column="UserFavoriteFolderId", primary_key=True)
    name = models.TextField(db_column="FolderName", blank=True, default="")
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="favorite_folders",
    )
    rank = models.IntegerField(db_column="FolderRank", blank=True, null=True)

    @property
    def total(self):
        return (
            self.starred_reports.count()
            + self.starred_collections.count()
            + self.starred_initiatives.count()
            + self.starred_terms.count()
            + self.starred_users.count()
            + self.starred_groups.count()
        )

    class Meta:
        managed = False
        db_table = "UserFavoriteFolders"
        ordering = ["rank"]


class StarredUsers(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="Userid",
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_users",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        db_column="folderid",
        blank=True,
        null=True,
        related_name="starred_users",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredUsers"


class StarredReports(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
        db_column="reportid",
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_reports",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        db_column="folderid",
        blank=True,
        null=True,
        related_name="starred_reports",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredReports"

    def __str__(self):
        return str(self.report)


class StarredCollections(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    collection = models.ForeignKey(
        "Collections",
        on_delete=models.CASCADE,
        db_column="collectionid",
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_collections",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        db_column="folderid",
        blank=True,
        null=True,
        related_name="starred_collections",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredCollections"


class StarredGroups(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    group = models.ForeignKey(
        "Groups",
        on_delete=models.CASCADE,
        db_column="groupid",
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_groups",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        db_column="folderid",
        blank=True,
        null=True,
        related_name="starred_groups",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredGroups"


class StarredTerms(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        db_column="termid",
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_terms",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        db_column="folderid",
        blank=True,
        null=True,
        related_name="starred_terms",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredTerms"


class StarredSearches(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    search = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_searches",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredSearches"


class StarredInitiatives(models.Model):
    star_id = models.AutoField(db_column="StarId", primary_key=True)
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)
    initiative = models.ForeignKey(
        "Initiatives",
        on_delete=models.CASCADE,
        db_column="Initiativeid",
        blank=True,
        null=True,
        related_name="starred",
    )
    folder = models.ForeignKey(
        "FavoriteFolders",
        on_delete=models.CASCADE,
        db_column="Folderid",
        blank=True,
        null=True,
        related_name="starred_initiatives",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ownerid",
        blank=True,
        null=True,
        related_name="starred_initiatives",
    )

    class Meta:
        ordering = ["rank"]
        managed = False
        db_table = "StarredInitiatives"


# class Favorites(models.Model):
#     favorite_id = models.AutoField(db_column="UserFavoritesId", primary_key=True)
#     item_type = models.TextField(db_column="ItemType", blank=True, default="")
#     rank = models.IntegerField(db_column="ItemRank", blank=True, null=True)
#     item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
#     user = models.ForeignKey(
#         "Users",
#         models.DO_NOTHING,
#         db_column="UserId",
#         blank=True,
#         null=True,
#         related_name="favorites",
#     )
#     name = models.TextField(db_column="ItemName", blank=True, default="")
#     folder = models.ForeignKey(
#         FavoriteFolders,
#         models.DO_NOTHING,
#         db_column="FolderId",
#         blank=True,
#         null=True,
#         related_name="favorites",
#     )

#     class Meta:
#         managed = False
#         db_table = "UserFavorites"
#         ordering = ["rank"]

#     def __str__(self):
#         if self.item_type.lower() == "report":
#             return str(Reports.objects.get(report_id=self.item_id))
#         elif self.item_type.lower() == "term":
#             return str(Terms.objects.get(term_id=self.item_id).name)
#         elif self.item_type.lower() in ["collection", "project"]:
#             return str(Collections.objects.get(collection_id=self.item_id))
#         elif self.item_type.lower() == "initiative":
#             return str(Initiatives.objects.get(initiative_id=self.item_id))
#         else:
#             return ""

#     @property
#     def atlas_url(self):
#         return "{}s/{}".format(
#             self.item_type,
#             self.item_id,
#         )

#     @property
#     def system_run_url(self):
#         if self.item_type.lower() == "report":
#             return Reports.objects.get(report_id=self.item_id).system_run_url()

#     @property
#     def system_manage_url(self):
#         if self.item_type.lower() == "report":
#             return Reports.objects.get(report_id=self.item_id).system_manage_url()

#     @property
#     def system_editor_url(self):
#         if self.item_type.lower() == "report":
#             return Reports.objects.get(report_id=self.item_id).system_editor_url()

#     @property
#     def system_id(self):
#         if self.item_type.lower() == "report":
#             return Reports.objects.filter(report_id=self.item_id).first().system_id

#         return None

#     @property
#     def system_identifier(self):
#         if self.item_type.lower() == "report":
#             return (
#                 Reports.objects.filter(report_id=self.item_id).first().system_identifier
#             )

#         return None

#     @property
#     def certification_tag(self):
#         if self.item_type.lower() == "report":
#             return Reports.objects.get(report_id=self.item_id).certification_tag

#         return None

#     @property
#     def description(self):
#         if self.item_type.lower() == "report":
#             report = Reports.objects.get(report_id=self.item_id)
#             return (
#                 report.docs.description
#                 or report.description
#                 or report.detailed_descripion
#                 or report.docs.assumptions
#             )
#         elif self.item_type.lower() == "term":
#             term = Terms.objects.get(term_id=self.item_id)
#             return term.summary or term.technical_definition
#         elif self.item_type.lower() == "collection":
#             collection = Collections.objects.get(collection_id=self.item_id)
#             return collection.purpose or collection.description
#         elif self.item_type.lower() == "initiative":
#             return Initiatives.objects.get(initiative_id=self.item_id).description


class UserPreferences(models.Model):
    preference_id = models.AutoField(db_column="UserPreferenceId", primary_key=True)
    key = models.TextField(db_column="ItemType", blank=True, default="")
    value = models.IntegerField(db_column="ItemValue", blank=True, null=True)
    item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
    user = models.ForeignKey(
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


class GroupRoleLinks(models.Model):
    rolelinks_id = models.AutoField(
        db_column="GroupRoleLinksId", primary_key=True
    )  # Field name made lowercase.
    group = models.ForeignKey(
        "Groups",
        models.DO_NOTHING,
        db_column="GroupId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        "UserRoles",
        models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="role_groups",
    )

    class Meta:
        managed = False
        db_table = "GroupRoleLinks"


class UserRolelinks(models.Model):
    rolelinks_id = models.AutoField(db_column="UserRoleLinksId", primary_key=True)
    user = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        "UserRoles",
        models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="role_users",
    )

    class Meta:
        managed = False
        db_table = "UserRoleLinks"


class UserRoles(models.Model):
    role_id = models.AutoField(db_column="UserRolesId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "UserRoles"


class UserNamedata(models.Model):
    userid = models.IntegerField(db_column="UserId", primary_key=True)
    fullname = models.TextField(db_column="Fullname", blank=True, default="")
    firstname = models.TextField(db_column="Firstname", blank=True, default="")
    lastname = models.TextField(db_column="Lastname", blank=True, default="")

    class Meta:
        managed = False
        db_table = "User_NameData"
