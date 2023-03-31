"""Atlas Postgres Models."""
# pylint: disable=C0115,C0116,E0307

from typing import Any, Dict, List, Optional

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.functional import cached_property


class ReportGroupMemberships(models.Model):
    membership_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(
        "Groups", on_delete=models.CASCADE, related_name="reports"
    )
    report = models.ForeignKey(
        "Reports", on_delete=models.CASCADE, related_name="groups"
    )
    etl_date = models.DateTimeField(blank=True, null=True)


class Reports(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_key = models.TextField(blank=True, default="")
    type = models.ForeignKey(
        "ReportTypes",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    name = models.TextField(blank=True, default="")
    title = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    detailed_description = models.TextField(blank=True, default="")
    system_description = models.TextField(blank=True, default="")
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
    modified_at = models.DateTimeField(blank=True, auto_now=True)
    system_run_url = models.TextField(blank=True, default="")
    system_identifier = models.CharField(max_length=3, blank=True, default="")
    system_id = models.DecimalField(
        max_digits=18, decimal_places=0, blank=True, null=True
    )
    system_template_id = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    system_catalog_id = models.CharField(max_length=50, blank=True, default="")
    visible = models.CharField(max_length=1, blank=True, default="")
    orphan = models.CharField(max_length=1, blank=True, default="")
    system_path = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)
    availability = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.title or self.name

    @cached_property
    def is_certified(self) -> bool:
        return self.tags.filter(
            tag__name__in=["Analytics Certified", "Analytics Reviewed"]
        ).exists()

    def has_docs(self) -> bool:
        return hasattr(self, "docs")

    @cached_property
    def get_group_ids(self) -> QuerySet:
        return self.groups.all().values_list("group__group_id", flat=True)

    @property
    def friendly_name(self) -> str:
        return self.title or self.name

    def get_absolute_url(self) -> str:
        return reverse("report:item", kwargs={"pk": self.pk})

    def get_absolute_maint_status_url(self) -> str:
        return reverse("report:maint_status", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("report:edit", kwargs={"pk": self.pk})


class ReportParameters(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        related_name="parameters",
    )
    name = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)


class ReportAttachments(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    name = models.TextField()
    path = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportTags(models.Model):
    tag_id = models.AutoField(primary_key=True)
    system_id = models.DecimalField(
        max_digits=18, decimal_places=0, blank=True, null=True
    )
    name = models.CharField(max_length=200, blank=True, null=True)


class Tags(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=450, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    show_in_header = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.reports.count()


class ReportSystemTagLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        blank=True,
        default="",
        related_name="system_tag_links",
    )

    tag = models.ForeignKey(
        ReportTags,
        on_delete=models.CASCADE,
        related_name="system_report_links",
    )
    line = models.IntegerField(blank=True, null=True)


class ReportTagLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Reports,
        on_delete=models.CASCADE,
        blank=True,
        default="",
        related_name="tags",
    )
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, related_name="reports")
    show_in_header = models.TextField(blank=True, null=True)


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
        default="",
        on_delete=models.CASCADE,
        related_name="queries",
    )
    query = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)
    sourceserver = models.TextField(blank=True, null=True)
    language = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.query


class ReportSubscriptions(models.Model):
    subscriptions_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Reports,
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
    )
    user = models.ForeignKey(
        "Users",
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="report_subscriptions",
    )
    unique_id = models.TextField(blank=True, default="")
    inactive = models.IntegerField(blank=True, null=True)
    email_list = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    status = models.TextField(blank=True, default="")
    last_run = models.DateTimeField(blank=True, null=True)
    email = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)


class ReportTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.TextField()
    code = models.TextField(blank=True, default="")
    short_name = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)
    visible = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    @property
    def short(self) -> str:
        return self.short_name or self.name


class Users(AbstractUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.TextField()
    employee_id = models.TextField(blank=True, default="")
    account_name = models.TextField(blank=True, default="")
    display_name = models.TextField(blank=True, default="")
    _full_name = models.TextField(blank=True, default="")
    _first_name = models.TextField(blank=True, default="")
    full_name = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, default="")
    department = models.TextField(blank=True, default="")
    title = models.TextField(blank=True, default="")
    phone = models.TextField(blank=True, default="")
    email = models.TextField(blank=True, default="")
    base = models.TextField(blank=True, default="")
    system_id = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = True
    date_joined = None

    is_staff = True

    def __str__(self) -> str:
        return self.full_name or self._full_name

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
    def get_group_ids(self) -> QuerySet:
        return self.group_links.all().values_list("group__group_id", flat=True)

    @cached_property
    def get_all_permissions(self, obj: Optional[Any] = None) -> QuerySet:
        return self.get_user_permissions().union(self.get_group_permissions())

    def has_perm(self, perm: str, obj: Optional[Any] = None) -> bool:
        return perm in self.get_all_permissions

    def has_perms(self, perms: List[str], obj: Optional[Any] = None) -> bool:
        return set(perms) < set(self.get_all_permissions)

    def get_roles(self) -> List[str]:
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))

    def get_absolute_url(self) -> str:
        return reverse("user:profile", kwargs={"pk": self.pk})

    @cached_property
    def get_preferences(self) -> Dict[str, str]:
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
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="settings",
    )
    name = models.CharField(max_length=450, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)


class Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    account_name = models.TextField(blank=True, default="")
    name = models.TextField(blank=True, default="")
    email = models.TextField(blank=True, default="")
    type = models.TextField(blank=True, default="")
    source = models.TextField(blank=True, default="")
    etl_date = models.DateTimeField(blank=True, null=True)
    epic_id = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("group:profile", kwargs={"pk": self.pk})

    def get_roles(self) -> List[str]:
        """Get users roles."""
        return list(self.role_links.values_list("role__name"))


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        Users,
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="group_links",
    )
    group = models.ForeignKey(
        Groups,
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="user_memberships",
    )
    etl_date = models.DateTimeField(blank=True, null=True)


class Analytics(models.Model):
    analytics_id = models.AutoField(primary_key=True)
    language = models.TextField(blank=True, default="")
    useragent = models.TextField(blank=True, default="")
    hostname = models.TextField(blank=True, default="")
    href = models.TextField(blank=True, default="")
    protocol = models.TextField(blank=True, default="")
    search = models.TextField(blank=True, default="")
    pathname = models.TextField(blank=True, default="")
    unique_id = models.TextField(blank=True, default="")
    screen_height = models.TextField(blank=True, default="")
    screen_width = models.TextField(blank=True, default="")
    origin = models.TextField(blank=True, default="")
    load_time = models.TextField(blank=True, default="")
    access_date = models.DateTimeField(blank=True, null=True)
    referrer = models.TextField(blank=True, default="")
    user = models.ForeignKey(
        "Users",
        blank=True,
        null=True,
        related_name="analytics",
        on_delete=models.CASCADE,
    )
    zoom = models.FloatField(blank=True, default="")
    epic = models.IntegerField(blank=True, null=True)
    page_id = models.TextField(blank=True, default="")
    session_id = models.TextField(blank=True, default="")
    page_time = models.IntegerField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)


class AnalyticsErrors(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="analytics_errors",
    )

    status_code = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    trace = models.TextField(blank=True, null=True)
    access_date = models.DateTimeField(blank=True, null=True)
    handled = models.IntegerField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    useragent = models.TextField(blank=True, null=True)
    referer = models.TextField(blank=True, null=True)


class AnalyticsTrace(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="analytics_trace",
    )
    level = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    logger = models.TextField(blank=True, null=True)
    access_date = models.DateTimeField(blank=True, null=True)
    handled = models.IntegerField(blank=True, null=True)
    useragent = models.TextField(blank=True, null=True)
    referer = models.TextField(blank=True, null=True)


class Initiatives(models.Model):
    initiative_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
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
        "Financialimpact",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="initiatives",
    )
    strategic_importance = models.ForeignKey(
        "Strategicimportance",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="initiatives",
    )
    modified_at = models.DateTimeField(blank=True, auto_now=True)
    modified_by = models.ForeignKey(
        "Users",
        related_name="initiative_modifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    hidden = models.CharField(max_length=1, blank=True, null=True)

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
    collection_id = models.AutoField(primary_key=True)

    initiative = models.ForeignKey(
        "Initiatives",
        blank=True,
        null=True,
        related_name="collections",
        on_delete=models.CASCADE,
    )

    name = models.TextField(blank=True, default="")
    search_summary = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    modified_at = models.DateTimeField(blank=True, auto_now=True)
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="collection_modifier",
        blank=True,
        null=True,
    )

    hidden = models.CharField(max_length=1, blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("collection:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self) -> str:
        return reverse("collection:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("collection:edit", kwargs={"pk": self.pk})


class CollectionReports(models.Model):
    link_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reports",
    )
    rank = models.IntegerField(blank=True, null=True)

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
    link_id = models.AutoField(primary_key=True)
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        related_name="collections",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collections,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="terms",
    )
    rank = models.IntegerField(blank=True, null=True)

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
    frequency_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class FinancialImpact(models.Model):
    impact_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.initiatives.count()


class Fragility(models.Model):
    fragility_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class FragilityTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class GlobalSettings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    value = models.TextField(blank=True, default="")


class MailConversations(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(
        "MailMessages", on_delete=models.CASCADE, related_name="conversations"
    )


class MailDrafts(models.Model):
    draft_id = models.AutoField(primary_key=True)
    subject = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    editdate = models.DateTimeField(blank=True, null=True)
    messagetypeid = models.IntegerField(blank=True, null=True)
    fromuserid = models.IntegerField(blank=True, null=True)
    messageplaintext = models.TextField(blank=True, default="")
    recipients = models.TextField(blank=True, default="")
    replytomessageid = models.IntegerField(blank=True, null=True)
    replytoconvid = models.IntegerField(blank=True, null=True)


class MailFoldermessages(models.Model):
    folder_message_id = models.AutoField(primary_key=True)
    folder = models.ForeignKey(
        "MailFolders",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="folder_messages",
    )

    message = models.ForeignKey(
        "MailMessages",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="message_folders",
    )


class MailFolders(models.Model):
    folder_id = models.AutoField(primary_key=True)
    parentfolderid = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, default="")
    rank = models.IntegerField(blank=True, null=True)


class MailMessagetype(models.Model):
    messagetypeid = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")


class MailMessages(models.Model):
    message_id = models.AutoField(primary_key=True)
    subject = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    senddate = models.DateTimeField(blank=True, null=True)
    message_type = models.ForeignKey(
        MailMessagetype,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    fromuserid = models.IntegerField(blank=True, null=True)
    messageplaintext = models.TextField(blank=True, default="")


class MailRecipients(models.Model):
    recipient_id = models.AutoField(primary_key=True)
    message = models.ForeignKey(
        MailMessages,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="messages",
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
    comments = models.TextField(blank=True, default="")
    status = models.ForeignKey(
        "MaintenancelogStatus",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="logs",
    )
    report_doc = models.ForeignKey(
        "ReportDocs",
        on_delete=models.CASCADE,
        related_name="maintenance_logs",
    )

    class Meta:
        ordering = ["maintained_at"]


class MaintenanceLogStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.logs.count()


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class OrganizationalValue(models.Model):
    value_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.report_docs.count()


class ReportFragilityTags(models.Model):
    link_id = models.AutoField(primary_key=True)
    report_doc = models.ForeignKey(
        "ReportDocs", on_delete=models.CASCADE, related_name="fragility_tags"
    )
    fragility_tag = models.ForeignKey(
        FragilityTag, on_delete=models.CASCADE, related_name="report_docs"
    )

    class Meta:
        unique_together = (("report_doc", "fragility_tag"),)


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
    report = models.ForeignKey(
        Reports,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="imgs",
    )
    rank = models.IntegerField()
    data = models.BinaryField()
    source = models.TextField(blank=True, default="")

    def get_absolute_url(self) -> str:
        return reverse(
            "report:image", kwargs={"pk": self.pk, "report_id": self.report.report_id}
        )


class ReportRunDetails(models.Model):
    run_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_runs",
    )

    etl_date = models.DateTimeField()
    rundurationseconds = models.IntegerField(blank=True, null=True)
    runstarttime = models.DateTimeField()
    status = models.CharField(max_length=100, blank=True, null=True)

    rundataid = models.CharField(unique=True, max_length=450)
    runstarttime_day = models.DateTimeField()
    runstarttime_hour = models.DateTimeField()
    runstarttime_month = models.DateTimeField()
    runstarttime_year = models.DateTimeField()


class ReportRunBridge(models.Model):
    bridge_id = models.AutoField(primary_key=True)

    report = models.OneToOneField(
        "Reports",
        on_delete=models.CASCADE,
        related_name="runs",
    )

    run = models.OneToOneField(
        "ReportRunDetails",
        on_delete=models.CASCADE,
        related_name="runs",
        to_field="rundataid",
    )

    runs = models.IntegerField()
    inherited = models.IntegerField()


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
    external_url = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    assumptions = models.TextField(blank=True, default="")
    org_value = models.ForeignKey(
        OrganizationalValue,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_docs",
    )
    frequency = models.ForeignKey(
        RunFrequency,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_docs",
    )
    fragility = models.ForeignKey(
        Fragility,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="report_docs",
    )
    executive_report = models.CharField(max_length=1, blank=True, default="")
    maintenance_schedule = models.ForeignKey(
        MaintenanceSchedule,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="report_docs",
    )
    modified_at = models.DateTimeField(blank=True, auto_now=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
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
    enabled_for_hyperspace = models.CharField(max_length=1, blank=True, default="")
    do_not_purge = models.CharField(max_length=1, blank=True, default="")
    hidden = models.CharField(max_length=1, blank=True, default="")

    report = models.OneToOneField(
        "Reports",
        related_name="docs",
        primary_key=True,
        on_delete=models.CASCADE,
    )


class ReportTickets(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    number = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, default="")
    report_doc = models.OneToOneField(
        "ReportDocs",
        blank=True,
        default="",
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    url = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return str(self.number)


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(primary_key=True)
    role = models.ForeignKey(
        "UserRoles",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission = models.ForeignKey(
        "RolePermissions",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="role_permission_links",
    )

    def __str__(self) -> str:
        return self.permission.name


class RolePermissions(models.Model):
    permissions_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name


class SharedItems(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="sent_shares",
        blank=True,
        null=True,
    )
    recipient = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="recieved_shares",
        blank=True,
        null=True,
    )
    url = models.TextField(blank=True, default="")
    name = models.TextField(blank=True, default="")
    share_date = models.DateTimeField(blank=True, null=True)


class StrategicImportance(models.Model):
    importance_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name

    def usage(self) -> int:
        return self.initiatives.count()


class Terms(models.Model):
    term_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, default="")
    summary = models.TextField(blank=True, default="")
    technical_definition = models.TextField(blank=True, default="")
    approved = models.CharField(max_length=1, blank=True, default="")
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="term_approve_user",
        blank=True,
        null=True,
    )
    has_external_standard = models.CharField(max_length=1, blank=True, default="")
    external_standard_url = models.TextField(blank=True, default="")
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    modified_by = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        related_name="term_modifier",
        blank=True,
        null=True,
    )
    modified_at = models.DateTimeField(blank=True, auto_now=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("term:item", kwargs={"pk": self.pk})

    def get_absolute_delete_url(self) -> str:
        return reverse("term:delete", kwargs={"pk": self.pk})

    def get_absolute_edit_url(self) -> str:
        return reverse("term:edit", kwargs={"pk": self.pk})


class FavoriteFolders(models.Model):
    folder_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, default="")
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="favorite_folders",
    )
    rank = models.IntegerField(blank=True, null=True)

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
        ordering = ["rank"]


class StarredUsers(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_users",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_users",
    )

    class Meta:
        ordering = ["rank"]


class StarredReports(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    report = models.ForeignKey(
        "Reports",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_reports",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_reports",
    )

    class Meta:
        ordering = ["rank"]

    def __str__(self) -> str:
        return str(self.report)


class StarredCollections(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    collection = models.ForeignKey(
        "Collections",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_collections",
    )

    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_collections",
    )

    class Meta:
        ordering = ["rank"]


class StarredGroups(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    group = models.ForeignKey(
        "Groups",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_groups",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_groups",
    )

    class Meta:
        ordering = ["rank"]


class StarredTerms(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    term = models.ForeignKey(
        "Terms",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_terms",
    )
    folder = models.ForeignKey(
        FavoriteFolders,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_terms",
    )

    class Meta:
        ordering = ["rank"]


class StarredSearches(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    search = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_searches",
    )

    class Meta:
        ordering = ["rank"]


class StarredInitiatives(models.Model):
    star_id = models.AutoField(primary_key=True)
    rank = models.IntegerField(blank=True, null=True)
    initiative = models.ForeignKey(
        "Initiatives",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred",
    )
    folder = models.ForeignKey(
        "FavoriteFolders",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_initiatives",
    )
    owner = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="starred_initiatives",
    )

    class Meta:
        ordering = ["rank"]


class UserPreferences(models.Model):
    preference_id = models.AutoField(primary_key=True)
    key = models.TextField(blank=True, default="")
    value = models.IntegerField(blank=True, null=True)
    item_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(
        "Users",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_preferences",
    )


class GroupRoleLinks(models.Model):
    rolelinks_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(
        "Groups",
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
        related_name="role_groups",
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
    name = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.name


class UserNamedata(models.Model):
    userid = models.IntegerField(primary_key=True)
    fullname = models.TextField(blank=True, default="")
    firstname = models.TextField(blank=True, default="")
    lastname = models.TextField(blank=True, default="")
