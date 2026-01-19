from django.db import models


class ReportObjectType(models.Model):
    type_id = models.AutoField(db_column="ReportObjectTypeID", primary_key=True)
    name = models.TextField(db_column="Name")
    short_name = models.TextField(db_column="ShortName", blank=True, default="")
    code = models.TextField(db_column="DefaultEpicMasterFile", blank=True, default="")

    class Meta:
        managed = True
        db_table = "ReportObjectType"

    def __str__(self) -> str:
        return self.name


class ReportObject(models.Model):
    report_id = models.AutoField(db_column="ReportObjectID", primary_key=True)
    report_key = models.TextField(db_column="ReportObjectBizKey", blank=True, default="")
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
    system_run_url = models.TextField(db_column="ReportObjectURL", blank=True, default="")
    author = models.ForeignKey(
        "AtlasUser",
        on_delete=models.DO_NOTHING,
        db_column="AuthorUserID",
        blank=True,
        null=True,
        related_name="authored_reports",
    )
    last_modified_by = models.ForeignKey(
        "AtlasUser",
        on_delete=models.DO_NOTHING,
        db_column="LastModifiedByUserID",
        blank=True,
        null=True,
        related_name="modified_reports",
    )
    last_modified_date = models.DateTimeField(
        db_column="LastModifiedDate", blank=True, null=True
    )
    epic_master_file = models.TextField(db_column="EpicMasterFile", blank=True, default="")
    epic_record_id = models.TextField(db_column="EpicRecordID", blank=True, default="")
    report_server_catalog_id = models.IntegerField(
        db_column="ReportServerCatalogID", blank=True, null=True
    )
    default_visibility = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, default=""
    )
    orphaned = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, default=""
    )
    report_server_path = models.TextField(db_column="ReportServerPath", blank=True, default="")

    class Meta:
        managed = True
        db_table = "ReportObject"

    def __str__(self) -> str:
        return self.title or self.name or ""


class Tag(models.Model):
    tag_id = models.AutoField(db_column="TagId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=450, blank=True, null=True)
    description = models.TextField(db_column="Description", blank=True, null=True)

    class Meta:
        managed = True
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
        managed = True
        db_table = "ReportTagLinks"


class AtlasUser(models.Model):
    user_id = models.AutoField(db_column="UserID", primary_key=True)
    username = models.TextField(db_column="Username")
    full_name = models.TextField(db_column="FullName", blank=True, default="")
    first_name = models.TextField(db_column="FirstName", blank=True, default="")
    last_name = models.TextField(db_column="LastName", blank=True, default="")
    department = models.TextField(db_column="Department", blank=True, default="")
    title = models.TextField(db_column="Title", blank=True, default="")
    email = models.TextField(db_column="Email", blank=True, default="")
    display_name = models.TextField(db_column="DisplayName", blank=True, default="")
    full_name_calc = models.TextField(db_column="Fullname_calc", blank=True, null=True)

    class Meta:
        managed = True
        db_table = "User"

    def __str__(self) -> str:
        return self.full_name or self.display_name or self.username or ""


class Initiative(models.Model):
    initiative_id = models.AutoField(db_column="InitiativeID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = True
        db_table = "Initiative"

    def __str__(self) -> str:
        return self.name


class Term(models.Model):
    term_id = models.AutoField(db_column="TermId", primary_key=True)
    name = models.CharField(db_column="Name", max_length=255, blank=True, default="")
    summary = models.TextField(db_column="Summary", blank=True, default="")
    technical_definition = models.TextField(
        db_column="TechnicalDefinition", blank=True, default=""
    )
    approved = models.CharField(db_column="ApprovedYN", max_length=1, blank=True, default="")
    approval_datetime = models.DateTimeField(
        db_column="ApprovalDateTime", blank=True, null=True
    )
    approved_by = models.ForeignKey(
        "AtlasUser",
        on_delete=models.DO_NOTHING,
        db_column="ApprovedByUserId",
        blank=True,
        null=True,
        related_name="approved_terms",
    )
    has_external_standard = models.CharField(
        db_column="HasExternalStandardYN", max_length=1, blank=True, default=""
    )
    external_standard_url = models.TextField(
        db_column="ExternalStandardUrl", blank=True, default=""
    )
    valid_from_datetime = models.DateTimeField(
        db_column="ValidFromDateTime", blank=True, null=True
    )
    valid_to_datetime = models.DateTimeField(db_column="ValidToDateTime", blank=True, null=True)
    updated_by = models.ForeignKey(
        "AtlasUser",
        on_delete=models.DO_NOTHING,
        db_column="UpdatedByUserId",
        blank=True,
        null=True,
        related_name="updated_terms",
    )
    last_updated_datetime = models.DateTimeField(
        db_column="LastUpdatedDateTime", blank=True, null=True
    )

    class Meta:
        managed = True
        db_table = "app.Term"

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
    modified_at = models.DateTimeField(db_column="LastUpdateDate", blank=True, null=True)
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
        db_table = "UserPreferences"


class Groups(models.Model):
    group_id = models.AutoField(db_column="GroupId", primary_key=True)
    account_name = models.TextField(db_column="AccountName", blank=True, default="")
    name = models.TextField(db_column="GroupName", blank=True, default="")
    email = models.TextField(db_column="GroupEmail", blank=True, default="")
    group_type = models.TextField(db_column="GroupType", blank=True, default="")

    class Meta:
        managed = True
        db_table = "UserGroups"

    def __str__(self) -> str:
        return self.name


class UserRoles(models.Model):
    role_id = models.AutoField(db_column="UserRolesId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = True
        db_table = "UserRoles"

    def __str__(self) -> str:
        return self.name


class RolePermissions(models.Model):
    permissions_id = models.AutoField(db_column="RolePermissionsId", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")
    description = models.TextField(db_column="Description", blank=True, default="")

    class Meta:
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
        db_table = "app.UserRoleLinks"


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
        managed = True
        db_table = "UserGroupsMembership"


class OrganizationalValue(models.Model):
    organizational_value_id = models.AutoField(
        db_column="OrganizationalValueID", primary_key=True
    )
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.OrganizationalValue"


class EstimatedRunFrequency(models.Model):
    estimated_run_frequency_id = models.AutoField(
        db_column="EstimatedRunFrequencyID", primary_key=True
    )
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.EstimatedRunFrequency"


class Fragility(models.Model):
    fragility_id = models.AutoField(db_column="FragilityID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.Fragility"


class MaintenanceSchedule(models.Model):
    schedule_id = models.AutoField(db_column="MaintenanceScheduleID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.MaintenanceSchedule"


class MaintenanceLogStatus(models.Model):
    status_id = models.AutoField(db_column="MaintenanceLogStatusID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.MaintenanceLogStatus"


class FragilityTag(models.Model):
    fragility_tag_id = models.AutoField(db_column="FragilityTagID", primary_key=True)
    name = models.TextField(db_column="Name", blank=True, default="")

    class Meta:
        managed = True
        db_table = "app.FragilityTag"


class ReportObjectDoc(models.Model):
    report = models.OneToOneField(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        primary_key=True,
        related_name="doc",
    )
    operational_owner_user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="OperationalOwnerUserID",
        blank=True,
        null=True,
        related_name="owned_report_docs",
    )
    requester = models.TextField(db_column="Requester", blank=True, default="")
    developer_description = models.TextField(
        db_column="DeveloperDescription", blank=True, default=""
    )
    key_assumptions = models.TextField(db_column="KeyAssumptions", blank=True, default="")
    organizational_value = models.ForeignKey(
        OrganizationalValue,
        on_delete=models.DO_NOTHING,
        db_column="OrganizationalValueID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    estimated_run_frequency = models.ForeignKey(
        EstimatedRunFrequency,
        on_delete=models.DO_NOTHING,
        db_column="EstimatedRunFrequencyID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    fragility = models.ForeignKey(
        Fragility,
        on_delete=models.DO_NOTHING,
        db_column="FragilityID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    executive_visibility = models.CharField(
        db_column="ExecutiveVisibilityYN", max_length=1, blank=True, default=""
    )
    maintenance_schedule = models.ForeignKey(
        MaintenanceSchedule,
        on_delete=models.DO_NOTHING,
        db_column="MaintenanceScheduleID",
        blank=True,
        null=True,
        related_name="report_docs",
    )
    last_update_datetime = models.DateTimeField(
        db_column="LastUpdateDateTime", blank=True, null=True
    )
    created_datetime = models.DateTimeField(db_column="CreatedDateTime", blank=True, null=True)
    created_by = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="CreatedBy",
        blank=True,
        null=True,
        related_name="created_report_docs",
    )
    updated_by = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="UpdatedBy",
        blank=True,
        null=True,
        related_name="updated_report_docs",
    )

    class Meta:
        managed = True
        db_table = "app.ReportObject_doc"


class ReportObjectDocTerms(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        ReportObjectDoc,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="term_links",
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.DO_NOTHING,
        db_column="TermId",
        related_name="report_doc_links",
    )

    class Meta:
        managed = True
        db_table = "app.ReportObjectDocTerms"


class ReportObjectDocFragilityTags(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        ReportObjectDoc,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="fragility_tag_links",
    )
    fragility_tag = models.ForeignKey(
        FragilityTag,
        on_delete=models.DO_NOTHING,
        db_column="FragilityTagID",
        related_name="report_doc_links",
    )

    class Meta:
        managed = True
        db_table = "app.reportobjectdocfragilitytags"


class MaintenanceLog(models.Model):
    maintenance_log_id = models.AutoField(db_column="MaintenanceLogId", primary_key=True)
    report_doc = models.ForeignKey(
        ReportObjectDoc,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        null=True,
        related_name="maintenance_logs",
    )
    maintainer = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="MaintainerID",
        blank=True,
        null=True,
        related_name="maintenance_logs",
    )
    maintenance_date = models.DateTimeField(db_column="MaintenanceDate", blank=True, null=True)
    comment = models.TextField(db_column="Comment", blank=True, default="")
    status = models.ForeignKey(
        MaintenanceLogStatus,
        on_delete=models.DO_NOTHING,
        db_column="MaintenanceLogStatusID",
        blank=True,
        null=True,
        related_name="maintenance_logs",
    )

    class Meta:
        managed = True
        db_table = "app.MaintenanceLog"


class ReportObjectDocMaintenanceLogs(models.Model):
    link_id = models.AutoField(db_column="LinkId", primary_key=True)
    report_doc = models.ForeignKey(
        ReportObjectDoc,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="maintenance_log_links",
    )
    maintenance_log = models.ForeignKey(
        MaintenanceLog,
        on_delete=models.DO_NOTHING,
        db_column="MaintenanceLogId",
        related_name="report_doc_links",
    )

    class Meta:
        managed = True
        db_table = "app.ReportObjectDocMaintenanceLogs"


class ReportObjectHierarchy(models.Model):
    hierarchy_id = models.AutoField(db_column="HierarchyId", primary_key=True)
    parent_report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ParentReportObjectID",
        related_name="children_links",
    )
    child_report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ChildReportObjectID",
        related_name="parent_links",
    )

    class Meta:
        managed = True
        db_table = "ReportObjectHierarchy"


class ReportObjectQuery(models.Model):
    query_id = models.AutoField(db_column="QueryId", primary_key=True)
    report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectID",
        related_name="queries",
    )
    query = models.TextField(db_column="Query")

    class Meta:
        managed = True
        db_table = "ReportObjectQuery"


class ReportObjectRunData(models.Model):
    run_data_id = models.CharField(db_column="RunDataId", primary_key=True, max_length=450)
    run_user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="RunUserID",
        blank=True,
        null=True,
        related_name="report_runs",
    )
    run_start_time = models.DateTimeField(db_column="RunStartTime", blank=True, null=True)
    run_duration_seconds = models.DecimalField(
        db_column="RunDurationSeconds", max_digits=18, decimal_places=2, blank=True, null=True
    )
    run_status = models.CharField(db_column="RunStatus", max_length=50, blank=True, null=True)
    last_load_date = models.DateTimeField(db_column="LastLoadDate", blank=True, null=True)
    run_start_time_hour = models.IntegerField(db_column="RunStartTime_Hour", blank=True, null=True)
    run_start_time_day = models.IntegerField(db_column="RunStartTime_Day", blank=True, null=True)
    run_start_time_month = models.IntegerField(db_column="RunStartTime_Month", blank=True, null=True)
    run_start_time_year = models.IntegerField(db_column="RunStartTime_Year", blank=True, null=True)

    class Meta:
        managed = True
        db_table = "ReportObjectRunData"


class ReportObjectRunDataBridge(models.Model):
    bridge_id = models.AutoField(db_column="BridgeId", primary_key=True)
    report = models.ForeignKey(
        ReportObject,
        on_delete=models.DO_NOTHING,
        db_column="ReportObjectId",
        related_name="run_bridges",
    )
    run_id = models.IntegerField(db_column="RunId")
    runs = models.IntegerField(db_column="Runs", blank=True, null=True)
    inherited = models.CharField(db_column="Inherited", max_length=1, blank=True, default="")

    class Meta:
        managed = True
        db_table = "ReportObjectRunDataBridge"


class UserFavoriteFolders(models.Model):
    folder_id = models.AutoField(db_column="FolderId", primary_key=True)
    folder_name = models.TextField(db_column="FolderName", blank=True, default="")
    user = models.ForeignKey(
        AtlasUser,
        on_delete=models.DO_NOTHING,
        db_column="UserId",
        blank=True,
        null=True,
        related_name="favorite_folders",
    )

    class Meta:
        managed = True
        db_table = "app.UserFavoriteFolders"
