"""Atlas Sqlserver Models."""
# pylint: disable=C0115,C0116,E0307
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.functional import cached_property


class ReportGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    group = models.ForeignKey(
        "Groups",
        on_delete=models.CASCADE,
        db_column="GroupId",
        related_name="reports",
    )
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        related_name="report_creator",
        db_column="AuthorUserID",
        blank=True,
        null=True,
    )
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_modifier",
        db_column="LastModifiedByUserID",
        blank=True,
        null=True,
    )
    modified_at = models.DateTimeField(
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

    def __str__(self) -> str:
        return self.title or self.name or ""

    @cached_property
    def is_certified(self) -> bool:
        return self.tags.filter(
            tag__name__in=["Analytics Certified", "Analytics Reviewed"]
        ).exists()

    def has_docs(self) -> bool:
        return hasattr(self, "docs")

    @cached_property
    def get_group_ids(self) -> Tuple[int]:
        return self.groups.all().values_list("group__group_id", flat=True)

    @property
    def friendly_name(self) -> str:
        return self.title or self.name or ""

    def get_absolute_url(self) -> str:
        return reverse("report:item", kwargs={"pk": self.pk})

    def get_absolute_maint_status_url(self) -> str:
        return reverse("report:maint_status", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("report:edit", kwargs={"pk": self.pk})


class ReportParameters(models.Model):
    parameter_id = models.AutoField(
        db_column="ReportObjectParameterId", primary_key=True
    )
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        related_name="parameters",
    )
    name = models.TextField(db_column="ParameterName", blank=True, null=True)
    value = models.TextField(db_column="ParameterValue", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectParameters"


class ReportAttachments(models.Model):
    attachment_id = models.AutoField(
        db_column="ReportObjectAttachmentId", primary_key=True
    )
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        related_name="attachments",
    )
    name = models.TextField(db_column="Name")
    path = models.TextField(db_column="Path")
    created_at = models.DateTimeField(db_column="CreationDate", blank=True, null=True)
    source = models.TextField(db_column="Source", blank=True, null=True)
    type = models.TextField(db_column="Type", blank=True, null=True)
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectAttachments"


class ReportTags(models.Model):
    tag_id = models.AutoField(db_column="TagID", primary_key=True)
    system_id = models.DecimalField(
        db_column="EpicTagID", max_digits=18, decimal_places=0, blank=True, null=True
    )
    name = models.CharField(db_column="TagName", max_length=200, blank=True, null=True)

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

    def __str__(self) -> str:
        return self.name or ""

    def usage(self) -> int:
        return self.reports.count()


class ReportSystemTagLinks(models.Model):
    link_id = models.AutoField(db_column="TagMembershipID", primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        blank=True,
        default="",
        related_name="system_tag_links",
    )

    tag = models.ForeignKey(
        ReportTags,
        on_delete=models.CASCADE,
        db_column="TagID",
        related_name="system_report_links",
    )
    line = models.IntegerField(db_column="Line", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectTagMemberships"


class ReportTagLinks(models.Model):
    link_id = models.AutoField(db_column="ReportTagLinkId", primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        db_column="ReportId",
        blank=True,
        default="",
        related_name="tags",
    )
    tag = models.ForeignKey(
        Tags, on_delete=models.CASCADE, db_column="TagId", related_name="reports"
    )
    show_in_header = models.TextField(db_column="ShowInHeader", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportTagLinks"


class ReportHierarchies(models.Model):
    parent = models.OneToOneField(
        "Reports",
        on_delete=models.CASCADE,
        related_name="parent",
        db_column="ParentReportObjectID",
        primary_key=True,
    )
    child = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        blank=True,
        default="",
        related_name="queries",
    )
    query = models.TextField(db_column="Query", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    sourceserver = models.TextField(db_column="SourceServer", blank=True, null=True)
    language = models.TextField(db_column="Language", blank=True, null=True)
    name = models.TextField(db_column="Name", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectQuery"

    def __str__(self) -> str:
        return self.query or ""


class ReportSubscriptions(models.Model):
    subscriptions_id = models.AutoField(
        db_column="ReportObjectSubscriptionsId", primary_key=True
    )
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        blank=True,
        default="",
        related_name="user_subscriptions",
    )
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
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
    visible = models.CharField(db_column="Visible", max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportObjectType"

    def __str__(self) -> str:
        return self.name

    @property
    def short(self) -> str:
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
    is_staff = True

    class Meta:
        managed = False
        db_table = "User"

    def __str__(self) -> str:
        return self.full_name or self._full_name or ""

    @cached_property
    def is_superuser(self) -> bool:
        # either an admin, or in a group that is an admin.
        return (
            self.role_links.filter(role__name="Administrator").exists()
            or self.group_links.filter(
                group__role_links__role__name="Administrator"
            ).exists()
        )

    def get_user_permissions(self, obj: Optional[Any] = None) -> QuerySet:
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

    def get_group_permissions(self, obj: Optional[Any] = None) -> QuerySet:
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
    def get_group_ids(self) -> List[int]:
        return self.group_links.all().values_list("group__group_id", flat=True)

    @cached_property
    def get_all_permissions(self, obj: Optional[Any] = None) -> QuerySet:
        return self.get_user_permissions().union(self.get_group_permissions())

    def has_perm(self, perm: str, obj: Optional[Any] = None) -> bool:
        return perm in self.get_all_permissions

    def has_perms(self, perms: Tuple[str, ...], obj: Optional[Any] = None) -> bool:
        return set(perms) < set(self.get_all_permissions)

    def get_roles(self) -> QuerySet:
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))

    def get_absolute_url(self) -> str:
        return reverse("user:profile", kwargs={"pk": self.pk})

    @cached_property
    def get_preferences(self) -> Dict[Any, Any]:
        # return users preferences as queriable object
        return dict(self.user_preferences.values_list("key", "value"))

    @cached_property
    def get_starred_reports(self) -> List[int]:
        # return all favorites
        return list(self.starred_reports.values_list("report__report_id", flat=True))

    @cached_property
    def get_starred_initiatives(self) -> List[int]:
        # return all favorites
        return list(
            self.starred_initiatives.values_list("initiative__initiative_id", flat=True)
        )

    @cached_property
    def get_starred_collections(self) -> List[int]:
        # return all favorites
        return list(
            self.starred_collections.values_list("collection__collection_id", flat=True)
        )

    @cached_property
    def get_starred_terms(self) -> List[int]:
        # return all favorites
        return list(self.starred_terms.values_list("term__term_id", flat=True))

    @cached_property
    def get_starred_users(self) -> List[int]:
        # return all favorites
        return list(self.starred_users.values_list("user__user_id", flat=True))

    @cached_property
    def get_starred_groups(self) -> List[int]:
        # return all favorites
        return list(self.starred_groups.values_list("group__group_id", flat=True))

    @cached_property
    def get_starred_searches(self) -> List[int]:
        # return all favorites
        return list(self.starred_searches.values_list("search__search_id", flat=True))

    @property
    def password(self) -> int:
        return 123


class UserSettings(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="settings",
    )
    name = models.CharField(db_column="Name", max_length=450, blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    value = models.TextField(db_column="Value", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "UserSettings"


class Groups(models.Model):
    group_id = models.AutoField(db_column="GroupId", primary_key=True)
    account_name = models.TextField(db_column="AccountName", blank=True, default="")
    name = models.TextField(db_column="GroupName", blank=True, default="")
    email = models.TextField(db_column="GroupEmail", blank=True, default="")
    type = models.TextField(db_column="GroupType", blank=True, default="")
    source = models.TextField(db_column="GroupSource", blank=True, default="")
    etl_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    epic_id = models.TextField(db_column="EpicId", blank=True, default="")

    class Meta:
        managed = False
        db_table = "UserGroups"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("group:profile", kwargs={"pk": self.pk})

    def get_roles(self) -> List[str]:
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        default="",
        related_name="group_links",
    )
    group = models.ForeignKey(
        Groups,
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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


class AnalyticsErrors(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="analytics_errors",
    )

    status_code = models.IntegerField(db_column="StatusCode", blank=True, null=True)
    message = models.TextField(db_column="Message", blank=True, null=True)
    trace = models.TextField(db_column="Trace", blank=True, null=True)
    access_date = models.DateTimeField(db_column="LogDateTime", blank=True, null=True)
    handled = models.IntegerField(db_column="Handled", blank=True, null=True)
    update_time = models.DateTimeField(db_column="UpdateTime", blank=True, null=True)
    useragent = models.TextField(db_column="UserAgent", blank=True, null=True)
    referer = models.TextField(db_column="Referer", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "AnalyticsError"

    def get_absolute_url(self) -> str:
        return reverse("analytics:error", kwargs={"pk": self.pk})


class AnalyticsTrace(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="analytics_trace",
    )
    level = models.IntegerField(db_column="Level", blank=True, null=True)
    message = models.TextField(db_column="Message", blank=True, null=True)
    logger = models.TextField(db_column="Logger", blank=True, null=True)
    access_date = models.DateTimeField(db_column="LogDateTime", blank=True, null=True)
    handled = models.IntegerField(db_column="Handled", blank=True, null=True)
    useragent = models.TextField(db_column="UserAgent", blank=True, null=True)
    referer = models.TextField(db_column="Referer", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "AnalyticsTrace"

    def get_absolute_url(self) -> str:
        return reverse("analytics:trace", kwargs={"pk": self.pk})


class Initiatives(models.Model):
    initiative_id = models.AutoField(db_column="InitiativeID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    ops_owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="OperationOwnerID",
        blank=True,
        null=True,
        related_name="initiative_ops_owner",
    )
    exec_owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="ExecutiveOwnerID",
        blank=True,
        null=True,
        related_name="initiative_exec_owner",
    )

    financial_impact = models.ForeignKey(
        "Financialimpact",
        on_delete=models.CASCADE,
        db_column="FinancialImpact",
        blank=True,
        null=True,
        related_name="initiatives",
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        on_delete=models.CASCADE,
        db_column="StrategicImportance",
        blank=True,
        null=True,
        related_name="initiatives",
    )
    modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, auto_now=True
    )
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="initiative_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )
    hidden = models.CharField(db_column="Hidden", max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Initiative"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("initiative:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self) -> str:
        return reverse("initiative:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("initiative:edit", kwargs={"pk": self.pk})

    def stars(self) -> int:
        return self.stars.count()  # type: ignore[attr-defined]


class Collections(models.Model):
    collection_id = models.AutoField(db_column="CollectionId", primary_key=True)

    initiative = models.ForeignKey(
        "Initiatives",
        on_delete=models.CASCADE,
        db_column="InitiativeId",
        blank=True,
        null=True,
        related_name="collections",
    )

    name = models.TextField(db_column="Name", blank=True, default="")
    search_summary = models.TextField(db_column="Purpose", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, auto_now=True
    )
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
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

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("collection:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self) -> str:
        return reverse("collection:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("collection:edit", kwargs={"pk": self.pk})


class CollectionReports(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
        db_column="ReportId",
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        on_delete=models.CASCADE,
        db_column="CollectionId",
        blank=True,
        null=True,
        related_name="reports",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "CollectionReport"

    def __str__(self) -> str:
        return self.report.friendly_name

    def get_absolute_delete_url(self) -> str:
        return reverse(
            "collection:report_delete",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )

    def get_absolute_edit_url(self) -> str:
        return reverse(
            "collection:report_edit",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )


class CollectionTerms(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        db_column="TermId",
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        on_delete=models.CASCADE,
        db_column="CollectionId",
        blank=True,
        null=True,
        related_name="terms",
    )
    rank = models.IntegerField(db_column="Rank", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "CollectionTerm"

    def __str__(self) -> str:
        return self.term.name

    def get_absolute_delete_url(self) -> str:
        return reverse(
            "collection:term_delete",
            kwargs={"pk": self.pk, "collection_id": self.collection_id},
        )

    def get_absolute_edit_url(self) -> str:
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

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class FinancialImpact(models.Model):
    impact_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "FinancialImpact"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.initiatives.count()


class Fragility(models.Model):
    fragility_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Fragility"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class FragilityTag(models.Model):
    tag_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "FragilityTag"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="FolderId",
        blank=True,
        null=True,
        related_name="folder_messages",
    )
    message = models.ForeignKey(
        "MailMessages",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="MaintenanceLogStatusID",
        blank=True,
        null=True,
        related_name="logs",
    )

    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
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

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.logs.count()


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name")

    class Meta:
        managed = False
        db_table = "MaintenanceSchedule"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class OrganizationalValue(models.Model):
    value_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "OrganizationalValue"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class ReportFragilityTags(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
        db_column="ReportObjectID",
        related_name="fragility_tags",
    )
    fragility_tag = models.ForeignKey(
        FragilityTag,
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="ReportObjectID",
        related_name="terms",
    )
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        db_column="TermId",
        related_name="report_docs",
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

    def get_absolute_url(self) -> str:
        return reverse(
            "report:image", kwargs={"pk": self.pk, "report_id": self.report.report_id}
        )


class ReportRunDetails(models.Model):
    run_id = models.AutoField(db_column="RunId", primary_key=True)

    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="RunUserID",
        blank=True,
        null=True,
        related_name="report_runs",
    )

    etl_date = models.DateTimeField(db_column="LastLoadDate")
    rundurationseconds = models.IntegerField(
        db_column="RunDurationSeconds", blank=True, null=True
    )
    runstarttime = models.DateTimeField(db_column="RunStartTime")
    status = models.CharField(
        db_column="RunStatus", max_length=100, blank=True, null=True
    )

    rundataid = models.CharField(db_column="RunDataId", unique=True, max_length=450)
    runstarttime_day = models.DateTimeField(db_column="RunStartTime_Day")
    runstarttime_hour = models.DateTimeField(db_column="RunStartTime_Hour")
    runstarttime_month = models.DateTimeField(db_column="RunStartTime_Month")
    runstarttime_year = models.DateTimeField(db_column="RunStartTime_Year")

    class Meta:
        managed = False
        db_table = "ReportObjectRunData"


class ReportRunBridge(models.Model):
    bridge_id = models.AutoField(db_column="BridgeId", primary_key=True)

    report = models.OneToOneField(
        "Reports",
        on_delete=models.CASCADE,
        db_column="ReportObjectID",
        related_name="runs",
    )

    run = models.OneToOneField(
        "ReportRunDetails",
        on_delete=models.CASCADE,
        db_column="RunId",
        related_name="runs",
        to_field="rundataid",
    )

    runs = models.IntegerField(db_column="Runs")
    inherited = models.IntegerField(db_column="Inherited")

    class Meta:
        managed = False
        db_table = "ReportObjectRunDataBridge"


class ReportDocs(models.Model):
    ops_owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_ops_owner",
        db_column="OperationalOwnerUserID",
        blank=True,
        null=True,
    )
    requester = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="OrganizationalValueID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    frequency = models.ForeignKey(
        RunFrequency,
        on_delete=models.CASCADE,
        db_column="EstimatedRunFrequencyID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    fragility = models.ForeignKey(
        Fragility,
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="MaintenanceScheduleID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    modified_at = models.DateTimeField(
        db_column="LastUpdateDateTime", blank=True, auto_now=True
    )
    created_at = models.DateTimeField(
        db_column="CreatedDateTime", blank=True, auto_now_add=True
    )
    created_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="report_doc_creator",
        db_column="CreatedBy",
        blank=True,
        null=True,
    )
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="ReportObjectID",
        related_name="docs",
        primary_key=True,
    )

    class Meta:
        managed = False
        db_table = "ReportObject_doc"


class ReportTickets(models.Model):
    ticket_id = models.AutoField(db_column="ServiceRequestId", primary_key=True)
    number = models.TextField(db_column="TicketNumber", blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)
    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
        db_column="ReportObjectId",
        blank=True,
        null=True,
        related_name="tickets",
    )
    url = models.TextField(db_column="TicketUrl", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ReportServiceRequests"

    def __str__(self) -> str:
        return str(self.number)


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(
        db_column="RolePermissionLinksId", primary_key=True
    )
    role = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
        db_column="RoleId",
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission = models.ForeignKey(
        "RolePermissions",
        on_delete=models.CASCADE,
        db_column="RolePermissionsId",
        blank=True,
        null=True,
        related_name="role_permission_links",
    )

    class Meta:
        managed = False
        db_table = "RolePermissionLinks"

    def __str__(self) -> str:
        return self.permission.name


class RolePermissions(models.Model):
    permissions_id = models.AutoField(db_column="RolePermissionsId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = False
        db_table = "RolePermissions"

    def __str__(self) -> str:
        return self.name


class SharedItems(models.Model):
    id = models.AutoField(db_column="Id", primary_key=True)
    sender = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="sent_shares",
        db_column="SharedFromUserId",
        blank=True,
        null=True,
    )
    recipient = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="recieved_shares",
        db_column="SharedToUserId",
        blank=True,
        null=True,
    )
    url = models.TextField(db_column="Url", blank=True, default="")
    name = models.TextField(db_column="Name", blank=True, default="")
    share_date = models.DateTimeField(db_column="ShareDate", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "SharedItems"


class StrategicImportance(models.Model):
    importance_id = models.AutoField(db_column="Id", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = False
        db_table = "StrategicImportance"

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
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
    approved_at = models.DateTimeField(
        db_column="ApprovalDateTime", blank=True, null=True
    )
    approved_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
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
    valid_from = models.DateTimeField(
        db_column="ValidFromDateTime", blank=True, null=True
    )
    valid_to = models.DateTimeField(db_column="ValidToDateTime", blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="term_modifier",
        db_column="UpdatedByUserId",
        blank=True,
        null=True,
    )
    modified_at = models.DateTimeField(
        db_column="LastUpdatedDateTime", blank=True, auto_now=True
    )

    class Meta:
        managed = False
        db_table = "Term"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("term:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self) -> str:
        return reverse("term:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("term:edit", kwargs={"pk": self.pk})


class FavoriteFolders(models.Model):
    folder_id = models.AutoField(db_column="UserFavoriteFolderId", primary_key=True)
    name = models.TextField(db_column="FolderName", blank=True, default="")
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="favorite_folders",
    )
    rank = models.IntegerField(db_column="FolderRank", blank=True, null=True)

    @property
    def total(self) -> int:
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

    def __str__(self) -> str:
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


class UserPreferences(models.Model):
    preference_id = models.AutoField(db_column="UserPreferenceId", primary_key=True)
    key = models.TextField(db_column="ItemType", blank=True, default="")
    value = models.IntegerField(db_column="ItemValue", blank=True, null=True)
    item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="user_preferences",
    )

    class Meta:
        managed = False
        db_table = "UserPreferences"


class GroupRoleLinks(models.Model):
    rolelinks_id = models.AutoField(db_column="GroupRoleLinksId", primary_key=True)
    group = models.ForeignKey(
        "Groups",
        on_delete=models.CASCADE,
        db_column="GroupId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
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
        on_delete=models.CASCADE,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
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

    def __str__(self) -> str:
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
