from django.db import models


class ReportObjectType(models.Model):
    type_id = models.AutoField(db_column="ReportObjectTypeID", primary_key=True)
    name = models.TextField(db_column="Name")
    short_name = models.TextField(db_column="ShortName", blank=True, default="")
    code = models.TextField(db_column="DefaultEpicMasterFile", blank=True, default="")

    class Meta:
        managed = False
        db_table = "ReportObjectType"

    def __str__(self) -> str:
        return self.name


class ReportObject(models.Model):
    report_id = models.AutoField(db_column="ReportObjectID", primary_key=True)
    report_key = models.TextField(
        db_column="ReportObjectBizKey", blank=True, default=""
    )
    type = models.ForeignKey(
        ReportObjectType,
        on_delete=models.DO_NOTHING,
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
    system_server = models.CharField(db_column="SourceServer", max_length=255)
    system_db = models.CharField(db_column="SourceDB", max_length=255)
    system_table = models.CharField(db_column="SourceTable", max_length=255)
    system_run_url = models.TextField(
        db_column="ReportObjectURL", blank=True, default=""
    )

    class Meta:
        managed = False
        db_table = "ReportObject"

    def __str__(self) -> str:
        return self.title or self.name or ""


class Tag(models.Model):
    tag_id = models.AutoField(db_column="TagId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=450, blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "Tags"

    def __str__(self) -> str:
        return self.name or ""


class ReportTagLink(models.Model):
    link_id = models.AutoField(db_column="ReportTagLinkId", primary_key=True)
    report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ReportId",
        blank=True,
        null=True,
        related_name="tag_links",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.DO_NOTHING,
        db_column="TagId",
        blank=True,
        null=True,
        related_name="report_links",
    )

    class Meta:
        managed = False
        db_table = "ReportTagLinks"


class AtlasUser(models.Model):
    user_id = models.AutoField(db_column="UserID", primary_key=True)
    username = models.TextField(db_column="Username")
    email = models.TextField(db_column="Email", blank=True, default="")
    display_name = models.TextField(db_column="DisplayName", blank=True, default="")
    full_name = models.TextField(db_column="Fullname_calc", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "User"

    def __str__(self) -> str:
        return self.full_name or self.display_name or self.username or ""


class Initiative(models.Model):
    initiative_id = models.AutoField(db_column="InitiativeID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Initiative"

    def __str__(self) -> str:
        return self.name


class Term(models.Model):
    term_id = models.AutoField(db_column="TermId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=255, blank=True, default="")
    summary = models.TextField(db_column="Summary", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Term"

    def __str__(self) -> str:
        return self.name


class Collection(models.Model):
    collection_id = models.AutoField(db_column="CollectionId", primary_key=True)
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.DO_NOTHING,
        db_column="InitiativeId",
        blank=True,
        null=True,
        related_name="collections",
    )
    name = models.TextField(db_column="Name", blank=True, default="")
    search_summary = models.TextField(db_column="Purpose", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")
    modified_at = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )
    modified_by = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        related_name="collection_modifier",
        db_column="LastUpdateUser",
        blank=True,
        null=True,
    )
    hidden = models.CharField(db_column="Hidden", max_length=1, blank=True, default="")

    class Meta:
        managed = False
        db_table = "Collection"

    def __str__(self) -> str:
        return self.name


class CollectionReport(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ReportId",
        related_name="collection_links",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.DO_NOTHING,
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
        return self.report.title if self.report else ""


class CollectionTerm(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    term = models.ForeignKey(
        Term,
        on_delete=models.DO_NOTHING,
        db_column="TermId",
        related_name="collection_links",
        blank=True,
        null=True,
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.DO_NOTHING,
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
        return self.term.name if self.term else ""


class UserPreferences(models.Model):
    preference_id = models.AutoField(db_column="UserPreferenceId", primary_key=True)
    key = models.TextField(db_column="ItemType", blank=True, default="")
    value = models.IntegerField(db_column="ItemValue", blank=True, null=True)
    item_id = models.IntegerField(db_column="ItemId", blank=True, null=True)
    user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="user_preferences",
    )

    class Meta:
        managed = False
        db_table = "UserPreferences"


class Groups(models.Model):
    group_id = models.AutoField(db_column="GroupId", primary_key=True)
    account_name = models.TextField(db_column="AccountName", blank=True, default="")
    name = models.TextField(db_column="GroupName", blank=True, default="")

    class Meta:
        managed = False
        db_table = "Groups"

    def __str__(self) -> str:
        return self.name


class UserRoles(models.Model):
    role_id = models.AutoField(db_column="UserRolesId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = False
        db_table = "UserRoles"

    def __str__(self) -> str:
        return self.name


class RolePermissions(models.Model):
    permissions_id = models.AutoField(db_column="RolePermissionsId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = False
        db_table = "RolePermissions"

    def __str__(self) -> str:
        return self.name


class RolePermissionLinks(models.Model):
    permissionlinks_id = models.AutoField(
        db_column="RolePermissionLinksId", primary_key=True
    )
    role = models.ForeignKey(
        UserRoles,
        on_delete=models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="permission_links",
    )
    permission = models.ForeignKey(
        RolePermissions,
        on_delete=models.DO_NOTHING,
        db_column="RolePermissionsId",
        blank=True,
        null=True,
        related_name="role_permission_links",
    )

    class Meta:
        managed = False
        db_table = "RolePermissionLinks"


class GroupRoleLinks(models.Model):
    rolelinks_id = models.AutoField(db_column="GroupRoleLinksId", primary_key=True)
    group = models.ForeignKey(
        Groups,
        on_delete=models.DO_NOTHING,
        db_column="GroupId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        UserRoles,
        on_delete=models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="role_groups",
    )

    class Meta:
        managed = False
        db_table = "GroupRoleLinks"


class UserRoleLinks(models.Model):
    rolelinks_id = models.AutoField(db_column="UserRoleLinksId", primary_key=True)
    user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="role_links",
    )
    role = models.ForeignKey(
        UserRoles,
        on_delete=models.DO_NOTHING,
        db_column="UserRolesId",
        blank=True,
        null=True,
        related_name="role_users",
    )

    class Meta:
        managed = False
        db_table = "UserRoleLinks"


class UserGroupMemberships(models.Model):
    membership_id = models.AutoField(db_column="MembershipId", primary_key=True)
    user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="group_links",
    )
    group = models.ForeignKey(
        Groups,
        on_delete=models.DO_NOTHING,
        db_column="GroupId",
        blank=True,
        null=True,
        related_name="user_links",
    )

    class Meta:
        managed = False
        db_table = "UserGroupMemberships"
