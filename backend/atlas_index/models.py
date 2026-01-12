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
