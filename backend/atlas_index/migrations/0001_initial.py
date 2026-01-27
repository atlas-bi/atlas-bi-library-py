from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="AtlasUser",
            fields=[
                (
                    "user_id",
                    models.AutoField(
                        db_column="UserID", primary_key=True, serialize=False
                    ),
                ),
                ("username", models.TextField(db_column="Username")),
                (
                    "full_name",
                    models.TextField(db_column="FullName", blank=True, default=""),
                ),
                (
                    "first_name",
                    models.TextField(db_column="FirstName", blank=True, default=""),
                ),
                (
                    "last_name",
                    models.TextField(db_column="LastName", blank=True, default=""),
                ),
                (
                    "department",
                    models.TextField(db_column="Department", blank=True, default=""),
                ),
                (
                    "title",
                    models.TextField(db_column="Title", blank=True, default=""),
                ),
                (
                    "email",
                    models.TextField(db_column="Email", blank=True, default=""),
                ),
                (
                    "display_name",
                    models.TextField(db_column="DisplayName", blank=True, default=""),
                ),
                (
                    "full_name_calc",
                    models.TextField(db_column="Fullname_calc", blank=True, null=True),
                ),
            ],
            options={"db_table": "User"},
        ),
        migrations.CreateModel(
            name="Groups",
            fields=[
                (
                    "group_id",
                    models.AutoField(
                        db_column="GroupId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "account_name",
                    models.TextField(db_column="AccountName", blank=True, default=""),
                ),
                (
                    "name",
                    models.TextField(db_column="GroupName", blank=True, default=""),
                ),
                (
                    "email",
                    models.TextField(db_column="GroupEmail", blank=True, default=""),
                ),
                (
                    "group_type",
                    models.TextField(db_column="GroupType", blank=True, default=""),
                ),
            ],
            options={"db_table": "UserGroups"},
        ),
        migrations.CreateModel(
            name="Initiative",
            fields=[
                (
                    "initiative_id",
                    models.AutoField(
                        db_column="InitiativeID", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, default=""),
                ),
            ],
            options={"db_table": "Initiative"},
        ),
        migrations.CreateModel(
            name="ReportObjectType",
            fields=[
                (
                    "type_id",
                    models.AutoField(
                        db_column="ReportObjectTypeID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(db_column="Name")),
                (
                    "short_name",
                    models.TextField(db_column="ShortName", blank=True, default=""),
                ),
                (
                    "code",
                    models.TextField(
                        db_column="DefaultEpicMasterFile", blank=True, default=""
                    ),
                ),
            ],
            options={"db_table": "ReportObjectType"},
        ),
        migrations.CreateModel(
            name="RolePermissions",
            fields=[
                (
                    "permissions_id",
                    models.AutoField(
                        db_column="RolePermissionsId", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, default=""),
                ),
            ],
            options={"db_table": "RolePermissions"},
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "tag_id",
                    models.AutoField(
                        db_column="TagId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="Name", max_length=450, blank=True, null=True
                    ),
                ),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, null=True),
                ),
            ],
            options={"db_table": "Tags"},
        ),
        migrations.CreateModel(
            name="Term",
            fields=[
                (
                    "term_id",
                    models.AutoField(
                        db_column="TermId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_column="Name", max_length=255, blank=True, default=""
                    ),
                ),
                (
                    "summary",
                    models.TextField(db_column="Summary", blank=True, default=""),
                ),
            ],
            options={"db_table": "Term"},
        ),
        migrations.CreateModel(
            name="UserRoles",
            fields=[
                (
                    "role_id",
                    models.AutoField(
                        db_column="UserRolesId", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, default=""),
                ),
            ],
            options={"db_table": "UserRoles"},
        ),
        migrations.CreateModel(
            name="ReportObject",
            fields=[
                (
                    "report_id",
                    models.AutoField(
                        db_column="ReportObjectID", primary_key=True, serialize=False
                    ),
                ),
                (
                    "report_key",
                    models.TextField(
                        db_column="ReportObjectBizKey", blank=True, default=""
                    ),
                ),
                (
                    "name",
                    models.TextField(db_column="Name", blank=True, default=""),
                ),
                (
                    "title",
                    models.TextField(db_column="DisplayTitle", blank=True, default=""),
                ),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, default=""),
                ),
                (
                    "detailed_description",
                    models.TextField(
                        db_column="DetailedDescription", blank=True, default=""
                    ),
                ),
                (
                    "system_server",
                    models.CharField(db_column="SourceServer", max_length=255),
                ),
                (
                    "system_db",
                    models.CharField(db_column="SourceDB", max_length=255),
                ),
                (
                    "system_table",
                    models.CharField(db_column="SourceTable", max_length=255),
                ),
                (
                    "system_run_url",
                    models.TextField(
                        db_column="ReportObjectURL", blank=True, default=""
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        to="atlas_index.reportobjecttype",
                        on_delete=models.DO_NOTHING,
                        db_column="ReportObjectTypeID",
                        blank=True,
                        null=True,
                        related_name="reports",
                    ),
                ),
            ],
            options={"db_table": "ReportObject"},
        ),
        migrations.CreateModel(
            name="Collection",
            fields=[
                (
                    "collection_id",
                    models.AutoField(
                        db_column="CollectionId", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
                (
                    "search_summary",
                    models.TextField(db_column="Purpose", blank=True, default=""),
                ),
                (
                    "description",
                    models.TextField(db_column="Description", blank=True, default=""),
                ),
                (
                    "modified_at",
                    models.DateTimeField(
                        db_column="LastUpdateDate", blank=True, null=True
                    ),
                ),
                (
                    "hidden",
                    models.CharField(
                        db_column="Hidden", max_length=1, blank=True, default=""
                    ),
                ),
                (
                    "initiative",
                    models.ForeignKey(
                        to="atlas_index.initiative",
                        on_delete=models.DO_NOTHING,
                        db_column="InitiativeId",
                        blank=True,
                        null=True,
                        related_name="collections",
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=models.DO_NOTHING,
                        db_column="LastUpdateUser",
                        blank=True,
                        null=True,
                        related_name="collection_modifier",
                    ),
                ),
            ],
            options={"db_table": "Collection"},
        ),
        migrations.CreateModel(
            name="CollectionReport",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="LinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "rank",
                    models.IntegerField(db_column="Rank", blank=True, null=True),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        to="atlas_index.collection",
                        on_delete=models.DO_NOTHING,
                        db_column="CollectionId",
                        blank=True,
                        null=True,
                        related_name="reports",
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=models.DO_NOTHING,
                        db_column="ReportId",
                        blank=True,
                        null=True,
                        related_name="collection_links",
                    ),
                ),
            ],
            options={"db_table": "CollectionReport"},
        ),
        migrations.CreateModel(
            name="CollectionTerm",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="LinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "rank",
                    models.IntegerField(db_column="Rank", blank=True, null=True),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        to="atlas_index.collection",
                        on_delete=models.DO_NOTHING,
                        db_column="CollectionId",
                        blank=True,
                        null=True,
                        related_name="terms",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        to="atlas_index.term",
                        on_delete=models.DO_NOTHING,
                        db_column="TermId",
                        blank=True,
                        null=True,
                        related_name="collection_links",
                    ),
                ),
            ],
            options={"db_table": "CollectionTerm"},
        ),
        migrations.CreateModel(
            name="GroupRoleLinks",
            fields=[
                (
                    "rolelinks_id",
                    models.AutoField(
                        db_column="GroupRoleLinksId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        to="atlas_index.groups",
                        on_delete=models.DO_NOTHING,
                        db_column="GroupId",
                        blank=True,
                        null=True,
                        related_name="role_links",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        to="atlas_index.userroles",
                        on_delete=models.DO_NOTHING,
                        db_column="UserRolesId",
                        blank=True,
                        null=True,
                        related_name="role_groups",
                    ),
                ),
            ],
            options={"db_table": "GroupRoleLinks"},
        ),
        migrations.CreateModel(
            name="ReportTagLink",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="ReportTagLinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=models.DO_NOTHING,
                        db_column="ReportId",
                        blank=True,
                        null=True,
                        related_name="tag_links",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        to="atlas_index.tag",
                        on_delete=models.DO_NOTHING,
                        db_column="TagId",
                        blank=True,
                        null=True,
                        related_name="report_links",
                    ),
                ),
            ],
            options={"db_table": "ReportTagLinks"},
        ),
        migrations.CreateModel(
            name="RolePermissionLinks",
            fields=[
                (
                    "permissionlinks_id",
                    models.AutoField(
                        db_column="RolePermissionLinksId",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        to="atlas_index.rolepermissions",
                        on_delete=models.DO_NOTHING,
                        db_column="RolePermissionsId",
                        blank=True,
                        null=True,
                        related_name="role_permission_links",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        to="atlas_index.userroles",
                        on_delete=models.DO_NOTHING,
                        db_column="UserRolesId",
                        blank=True,
                        null=True,
                        related_name="permission_links",
                    ),
                ),
            ],
            options={"db_table": "RolePermissionLinks"},
        ),
        migrations.CreateModel(
            name="UserGroupMemberships",
            fields=[
                (
                    "membership_id",
                    models.AutoField(
                        db_column="MembershipId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        to="atlas_index.groups",
                        on_delete=models.DO_NOTHING,
                        db_column="GroupId",
                        blank=True,
                        null=True,
                        related_name="user_links",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=models.DO_NOTHING,
                        db_column="UserId",
                        blank=True,
                        null=True,
                        related_name="group_links",
                    ),
                ),
            ],
            options={"db_table": "UserGroupsMembership"},
        ),
        migrations.CreateModel(
            name="UserPreferences",
            fields=[
                (
                    "preference_id",
                    models.AutoField(
                        db_column="UserPreferenceId", primary_key=True, serialize=False
                    ),
                ),
                ("key", models.TextField(db_column="ItemType", blank=True, default="")),
                (
                    "value",
                    models.IntegerField(db_column="ItemValue", blank=True, null=True),
                ),
                (
                    "item_id",
                    models.IntegerField(db_column="ItemId", blank=True, null=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=models.DO_NOTHING,
                        db_column="UserId",
                        blank=True,
                        null=True,
                        related_name="user_preferences",
                    ),
                ),
            ],
            options={"db_table": "UserPreferences"},
        ),
        migrations.CreateModel(
            name="UserRoleLinks",
            fields=[
                (
                    "rolelinks_id",
                    models.AutoField(
                        db_column="UserRoleLinksId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        to="atlas_index.userroles",
                        on_delete=models.DO_NOTHING,
                        db_column="UserRolesId",
                        blank=True,
                        null=True,
                        related_name="role_users",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=models.DO_NOTHING,
                        db_column="UserId",
                        blank=True,
                        null=True,
                        related_name="role_links",
                    ),
                ),
            ],
            options={"db_table": "app.UserRoleLinks"},
        ),
    ]
