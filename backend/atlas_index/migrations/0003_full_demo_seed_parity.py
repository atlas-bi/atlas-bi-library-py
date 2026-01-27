import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("atlas_index", "0002_demo_seed_script_alignment"),
    ]

    operations = [
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
            BEGIN
                EXEC('CREATE SCHEMA app');
            END
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    IF OBJECT_ID('dbo.Term','U') IS NOT NULL AND OBJECT_ID('app.Term','U') IS NULL
                    BEGIN
                        ALTER SCHEMA app TRANSFER dbo.Term;
                    END
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.AlterModelTable(name="term", table="app.Term"),
            ],
        ),
        migrations.AddField(
            model_name="term",
            name="technical_definition",
            field=models.TextField(
                db_column="TechnicalDefinition", blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="approved",
            field=models.CharField(
                db_column="ApprovedYN", max_length=1, blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="approval_datetime",
            field=models.DateTimeField(
                db_column="ApprovalDateTime", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="approved_by",
            field=models.ForeignKey(
                to="atlas_index.atlasuser",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_column="ApprovedByUserId",
                blank=True,
                null=True,
                related_name="approved_terms",
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="has_external_standard",
            field=models.CharField(
                db_column="HasExternalStandardYN", max_length=1, blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="external_standard_url",
            field=models.TextField(
                db_column="ExternalStandardUrl", blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="valid_from_datetime",
            field=models.DateTimeField(
                db_column="ValidFromDateTime", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="valid_to_datetime",
            field=models.DateTimeField(
                db_column="ValidToDateTime", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="updated_by",
            field=models.ForeignKey(
                to="atlas_index.atlasuser",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_column="UpdatedByUserId",
                blank=True,
                null=True,
                related_name="updated_terms",
            ),
        ),
        migrations.AddField(
            model_name="term",
            name="last_updated_datetime",
            field=models.DateTimeField(
                db_column="LastUpdatedDateTime", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="author",
            field=models.ForeignKey(
                to="atlas_index.atlasuser",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_column="AuthorUserID",
                blank=True,
                null=True,
                related_name="authored_reports",
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="last_modified_by",
            field=models.ForeignKey(
                to="atlas_index.atlasuser",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_column="LastModifiedByUserID",
                blank=True,
                null=True,
                related_name="modified_reports",
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="last_modified_date",
            field=models.DateTimeField(
                db_column="LastModifiedDate", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="epic_master_file",
            field=models.TextField(db_column="EpicMasterFile", blank=True, default=""),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="epic_record_id",
            field=models.TextField(db_column="EpicRecordID", blank=True, default=""),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="report_server_catalog_id",
            field=models.IntegerField(
                db_column="ReportServerCatalogID", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="default_visibility",
            field=models.CharField(
                db_column="DefaultVisibilityYN", max_length=1, blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="orphaned",
            field=models.CharField(
                db_column="OrphanedReportObjectYN", max_length=1, blank=True, default=""
            ),
        ),
        migrations.AddField(
            model_name="reportobject",
            name="report_server_path",
            field=models.TextField(
                db_column="ReportServerPath", blank=True, default=""
            ),
        ),
        migrations.CreateModel(
            name="OrganizationalValue",
            fields=[
                (
                    "organizational_value_id",
                    models.AutoField(
                        db_column="OrganizationalValueID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.OrganizationalValue"},
        ),
        migrations.CreateModel(
            name="EstimatedRunFrequency",
            fields=[
                (
                    "estimated_run_frequency_id",
                    models.AutoField(
                        db_column="EstimatedRunFrequencyID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.EstimatedRunFrequency"},
        ),
        migrations.CreateModel(
            name="Fragility",
            fields=[
                (
                    "fragility_id",
                    models.AutoField(
                        db_column="FragilityID", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.Fragility"},
        ),
        migrations.CreateModel(
            name="MaintenanceSchedule",
            fields=[
                (
                    "schedule_id",
                    models.AutoField(
                        db_column="MaintenanceScheduleID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.MaintenanceSchedule"},
        ),
        migrations.CreateModel(
            name="MaintenanceLogStatus",
            fields=[
                (
                    "status_id",
                    models.AutoField(
                        db_column="MaintenanceLogStatusID",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.MaintenanceLogStatus"},
        ),
        migrations.CreateModel(
            name="FragilityTag",
            fields=[
                (
                    "fragility_tag_id",
                    models.AutoField(
                        db_column="FragilityTagID", primary_key=True, serialize=False
                    ),
                ),
                ("name", models.TextField(db_column="Name", blank=True, default="")),
            ],
            options={"db_table": "app.FragilityTag"},
        ),
        migrations.CreateModel(
            name="ReportObjectDoc",
            fields=[
                (
                    "report",
                    models.OneToOneField(
                        to="atlas_index.reportobject",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        primary_key=True,
                        serialize=False,
                        related_name="doc",
                    ),
                ),
                (
                    "requester",
                    models.TextField(db_column="Requester", blank=True, default=""),
                ),
                (
                    "developer_description",
                    models.TextField(
                        db_column="DeveloperDescription", blank=True, default=""
                    ),
                ),
                (
                    "key_assumptions",
                    models.TextField(
                        db_column="KeyAssumptions", blank=True, default=""
                    ),
                ),
                (
                    "executive_visibility",
                    models.CharField(
                        db_column="ExecutiveVisibilityYN",
                        max_length=1,
                        blank=True,
                        default="",
                    ),
                ),
                (
                    "last_update_datetime",
                    models.DateTimeField(
                        db_column="LastUpdateDateTime", blank=True, null=True
                    ),
                ),
                (
                    "created_datetime",
                    models.DateTimeField(
                        db_column="CreatedDateTime", blank=True, null=True
                    ),
                ),
                (
                    "operational_owner_user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="OperationalOwnerUserID",
                        blank=True,
                        null=True,
                        related_name="owned_report_docs",
                    ),
                ),
                (
                    "organizational_value",
                    models.ForeignKey(
                        to="atlas_index.organizationalvalue",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="OrganizationalValueID",
                        blank=True,
                        null=True,
                        related_name="report_docs",
                    ),
                ),
                (
                    "estimated_run_frequency",
                    models.ForeignKey(
                        to="atlas_index.estimatedrunfrequency",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="EstimatedRunFrequencyID",
                        blank=True,
                        null=True,
                        related_name="report_docs",
                    ),
                ),
                (
                    "fragility",
                    models.ForeignKey(
                        to="atlas_index.fragility",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="FragilityID",
                        blank=True,
                        null=True,
                        related_name="report_docs",
                    ),
                ),
                (
                    "maintenance_schedule",
                    models.ForeignKey(
                        to="atlas_index.maintenanceschedule",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="MaintenanceScheduleID",
                        blank=True,
                        null=True,
                        related_name="report_docs",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="CreatedBy",
                        blank=True,
                        null=True,
                        related_name="created_report_docs",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="UpdatedBy",
                        blank=True,
                        null=True,
                        related_name="updated_report_docs",
                    ),
                ),
            ],
            options={"db_table": "app.ReportObject_doc"},
        ),
        migrations.CreateModel(
            name="ReportObjectDocTerms",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="LinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "report_doc",
                    models.ForeignKey(
                        to="atlas_index.reportobjectdoc",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        related_name="term_links",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        to="atlas_index.term",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="TermId",
                        related_name="report_doc_links",
                    ),
                ),
            ],
            options={"db_table": "app.ReportObjectDocTerms"},
        ),
        migrations.CreateModel(
            name="ReportObjectDocFragilityTags",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="LinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "report_doc",
                    models.ForeignKey(
                        to="atlas_index.reportobjectdoc",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        related_name="fragility_tag_links",
                    ),
                ),
                (
                    "fragility_tag",
                    models.ForeignKey(
                        to="atlas_index.fragilitytag",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="FragilityTagID",
                        related_name="report_doc_links",
                    ),
                ),
            ],
            options={"db_table": "app.reportobjectdocfragilitytags"},
        ),
        migrations.CreateModel(
            name="MaintenanceLog",
            fields=[
                (
                    "maintenance_log_id",
                    models.AutoField(
                        db_column="MaintenanceLogId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "maintenance_date",
                    models.DateTimeField(
                        db_column="MaintenanceDate", blank=True, null=True
                    ),
                ),
                (
                    "comment",
                    models.TextField(db_column="Comment", blank=True, default=""),
                ),
                (
                    "report_doc",
                    models.ForeignKey(
                        to="atlas_index.reportobjectdoc",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        blank=True,
                        null=True,
                        related_name="maintenance_logs",
                    ),
                ),
                (
                    "maintainer",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="MaintainerID",
                        blank=True,
                        null=True,
                        related_name="maintenance_logs",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        to="atlas_index.maintenancelogstatus",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="MaintenanceLogStatusID",
                        blank=True,
                        null=True,
                        related_name="maintenance_logs",
                    ),
                ),
            ],
            options={"db_table": "app.MaintenanceLog"},
        ),
        migrations.CreateModel(
            name="ReportObjectDocMaintenanceLogs",
            fields=[
                (
                    "link_id",
                    models.AutoField(
                        db_column="LinkId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "report_doc",
                    models.ForeignKey(
                        to="atlas_index.reportobjectdoc",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        related_name="maintenance_log_links",
                    ),
                ),
                (
                    "maintenance_log",
                    models.ForeignKey(
                        to="atlas_index.maintenancelog",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="MaintenanceLogId",
                        related_name="report_doc_links",
                    ),
                ),
            ],
            options={"db_table": "app.ReportObjectDocMaintenanceLogs"},
        ),
        migrations.CreateModel(
            name="ReportObjectHierarchy",
            fields=[
                (
                    "hierarchy_id",
                    models.AutoField(
                        db_column="HierarchyId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "parent_report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ParentReportObjectID",
                        related_name="children_links",
                    ),
                ),
                (
                    "child_report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ChildReportObjectID",
                        related_name="parent_links",
                    ),
                ),
            ],
            options={"db_table": "ReportObjectHierarchy"},
        ),
        migrations.CreateModel(
            name="ReportObjectQuery",
            fields=[
                (
                    "query_id",
                    models.AutoField(
                        db_column="QueryId", primary_key=True, serialize=False
                    ),
                ),
                ("query", models.TextField(db_column="Query")),
                (
                    "report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectID",
                        related_name="queries",
                    ),
                ),
            ],
            options={"db_table": "ReportObjectQuery"},
        ),
        migrations.CreateModel(
            name="ReportObjectRunData",
            fields=[
                (
                    "run_data_id",
                    models.CharField(
                        db_column="RunDataId",
                        primary_key=True,
                        serialize=False,
                        max_length=450,
                    ),
                ),
                (
                    "run_start_time",
                    models.DateTimeField(
                        db_column="RunStartTime", blank=True, null=True
                    ),
                ),
                (
                    "run_duration_seconds",
                    models.DecimalField(
                        db_column="RunDurationSeconds",
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "run_status",
                    models.CharField(
                        db_column="RunStatus", max_length=50, blank=True, null=True
                    ),
                ),
                (
                    "last_load_date",
                    models.DateTimeField(
                        db_column="LastLoadDate", blank=True, null=True
                    ),
                ),
                (
                    "run_start_time_hour",
                    models.IntegerField(
                        db_column="RunStartTime_Hour", blank=True, null=True
                    ),
                ),
                (
                    "run_start_time_day",
                    models.IntegerField(
                        db_column="RunStartTime_Day", blank=True, null=True
                    ),
                ),
                (
                    "run_start_time_month",
                    models.IntegerField(
                        db_column="RunStartTime_Month", blank=True, null=True
                    ),
                ),
                (
                    "run_start_time_year",
                    models.IntegerField(
                        db_column="RunStartTime_Year", blank=True, null=True
                    ),
                ),
                (
                    "run_user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="RunUserID",
                        blank=True,
                        null=True,
                        related_name="report_runs",
                    ),
                ),
            ],
            options={"db_table": "ReportObjectRunData"},
        ),
        migrations.CreateModel(
            name="ReportObjectRunDataBridge",
            fields=[
                (
                    "bridge_id",
                    models.AutoField(
                        db_column="BridgeId", primary_key=True, serialize=False
                    ),
                ),
                ("run_id", models.IntegerField(db_column="RunId")),
                ("runs", models.IntegerField(db_column="Runs", blank=True, null=True)),
                (
                    "inherited",
                    models.CharField(
                        db_column="Inherited", max_length=1, blank=True, default=""
                    ),
                ),
                (
                    "report",
                    models.ForeignKey(
                        to="atlas_index.reportobject",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="ReportObjectId",
                        related_name="run_bridges",
                    ),
                ),
            ],
            options={"db_table": "ReportObjectRunDataBridge"},
        ),
        migrations.CreateModel(
            name="UserFavoriteFolders",
            fields=[
                (
                    "folder_id",
                    models.AutoField(
                        db_column="FolderId", primary_key=True, serialize=False
                    ),
                ),
                (
                    "folder_name",
                    models.TextField(db_column="FolderName", blank=True, default=""),
                ),
                (
                    "user",
                    models.ForeignKey(
                        to="atlas_index.atlasuser",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        db_column="UserId",
                        blank=True,
                        null=True,
                        related_name="favorite_folders",
                    ),
                ),
            ],
            options={"db_table": "app.UserFavoriteFolders"},
        ),
    ]
