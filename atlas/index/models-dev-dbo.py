# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Reportgroupsmemberships(models.Model):
    membershipid = models.AutoField(
        db_column="MembershipId", primary_key=True
    )  # Field name made lowercase.
    groupid = models.ForeignKey(
        "Usergroups", models.DO_NOTHING, db_column="GroupId"
    )  # Field name made lowercase.
    reportid = models.ForeignKey(
        "Reportobject", models.DO_NOTHING, db_column="ReportId"
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportGroupsMemberships"


class Reportobject(models.Model):
    reportobjectid = models.AutoField(
        db_column="ReportObjectID", primary_key=True
    )  # Field name made lowercase.
    reportobjectbizkey = models.TextField(
        db_column="ReportObjectBizKey", blank=True, null=True
    )  # Field name made lowercase.
    sourceserver = models.CharField(
        db_column="SourceServer", max_length=255
    )  # Field name made lowercase.
    sourcedb = models.CharField(
        db_column="SourceDB", max_length=255
    )  # Field name made lowercase.
    sourcetable = models.CharField(
        db_column="SourceTable", max_length=255
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    detaileddescription = models.TextField(
        db_column="DetailedDescription", blank=True, null=True
    )  # Field name made lowercase.
    reportobjecttypeid = models.ForeignKey(
        "Reportobjecttype",
        models.DO_NOTHING,
        db_column="ReportObjectTypeID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    authoruserid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="AuthorUserID", blank=True, null=True
    )  # Field name made lowercase.
    lastmodifiedbyuserid = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="LastModifiedByUserID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    lastmodifieddate = models.DateTimeField(
        db_column="LastModifiedDate", blank=True, null=True
    )  # Field name made lowercase.
    reportobjecturl = models.TextField(
        db_column="ReportObjectURL", blank=True, null=True
    )  # Field name made lowercase.
    epicmasterfile = models.CharField(
        db_column="EpicMasterFile", max_length=3, blank=True, null=True
    )  # Field name made lowercase.
    epicrecordid = models.DecimalField(
        db_column="EpicRecordID", max_digits=18, decimal_places=0, blank=True, null=True
    )  # Field name made lowercase.
    reportservercatalogid = models.CharField(
        db_column="ReportServerCatalogID", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    defaultvisibilityyn = models.CharField(
        db_column="DefaultVisibilityYN", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    orphanedreportobjectyn = models.CharField(
        db_column="OrphanedReportObjectYN", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    epicreporttemplateid = models.DecimalField(
        db_column="EpicReportTemplateId",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )  # Field name made lowercase.
    reportserverpath = models.TextField(
        db_column="ReportServerPath", blank=True, null=True
    )  # Field name made lowercase.
    displaytitle = models.TextField(
        db_column="DisplayTitle", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.
    repositorydescription = models.TextField(
        db_column="RepositoryDescription", blank=True, null=True
    )  # Field name made lowercase.
    epicreleased = models.CharField(
        db_column="EpicReleased", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    availability = models.TextField(
        db_column="Availability", blank=True, null=True
    )  # Field name made lowercase.
    runs = models.IntegerField(
        db_column="Runs", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObject"


class Reportobjectattachments(models.Model):
    reportobjectattachmentid = models.AutoField(
        db_column="ReportObjectAttachmentId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.ForeignKey(
        Reportobject, models.DO_NOTHING, db_column="ReportObjectId"
    )  # Field name made lowercase.
    name = models.TextField(db_column="Name")  # Field name made lowercase.
    path = models.TextField(db_column="Path")  # Field name made lowercase.
    creationdate = models.DateTimeField(
        db_column="CreationDate", blank=True, null=True
    )  # Field name made lowercase.
    source = models.TextField(
        db_column="Source", blank=True, null=True
    )  # Field name made lowercase.
    type = models.TextField(
        db_column="Type", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectAttachments"


class Reportobjecthierarchy(models.Model):
    parentreportobjectid = models.OneToOneField(
        Reportobject,
        models.DO_NOTHING,
        db_column="ParentReportObjectID",
        primary_key=True,
    )  # Field name made lowercase.
    childreportobjectid = models.ForeignKey(
        Reportobject, models.DO_NOTHING, db_column="ChildReportObjectID"
    )  # Field name made lowercase.
    line = models.IntegerField(
        db_column="Line", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectHierarchy"
        unique_together = (("parentreportobjectid", "childreportobjectid"),)


class Reportobjectparameters(models.Model):
    reportobjectparameterid = models.AutoField(
        db_column="ReportObjectParameterId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId"
    )  # Field name made lowercase.
    parametername = models.TextField(
        db_column="ParameterName", blank=True, null=True
    )  # Field name made lowercase.
    parametervalue = models.TextField(
        db_column="ParameterValue", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectParameters"


class Reportobjectquery(models.Model):
    reportobjectqueryid = models.AutoField(
        db_column="ReportObjectQueryId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId"
    )  # Field name made lowercase.
    query = models.TextField(
        db_column="Query", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.
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


class Reportobjectrundata(models.Model):
    runuserid = models.IntegerField(
        db_column="RunUserID", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate"
    )  # Field name made lowercase.
    rundurationseconds = models.IntegerField(
        db_column="RunDurationSeconds", blank=True, null=True
    )  # Field name made lowercase.
    runstarttime = models.DateTimeField(
        db_column="RunStartTime"
    )  # Field name made lowercase.
    runstatus = models.CharField(
        db_column="RunStatus", max_length=100, blank=True, null=True
    )  # Field name made lowercase.
    runid = models.AutoField(
        db_column="RunId", primary_key=True
    )  # Field name made lowercase.
    rundataid = models.CharField(
        db_column="RunDataId", unique=True, max_length=450
    )  # Field name made lowercase.
    runstarttime_day = models.DateTimeField(
        db_column="RunStartTime_Day"
    )  # Field name made lowercase.
    runstarttime_hour = models.DateTimeField(
        db_column="RunStartTime_Hour"
    )  # Field name made lowercase.
    runstarttime_month = models.DateTimeField(
        db_column="RunStartTime_Month"
    )  # Field name made lowercase.
    runstarttime_year = models.DateTimeField(
        db_column="RunStartTime_Year"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectRunData"


class Reportobjectrundatabridge(models.Model):
    bridgeid = models.AutoField(
        db_column="BridgeId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId"
    )  # Field name made lowercase.
    runid = models.ForeignKey(
        Reportobjectrundata, models.DO_NOTHING, db_column="RunId", blank=True, null=True
    )  # Field name made lowercase.
    runs = models.IntegerField(db_column="Runs")  # Field name made lowercase.
    inherited = models.IntegerField(db_column="Inherited")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectRunDataBridge"


class Reportobjectsubscriptions(models.Model):
    reportobjectsubscriptionsid = models.AutoField(
        db_column="ReportObjectSubscriptionsId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.ForeignKey(
        Reportobject,
        models.DO_NOTHING,
        db_column="ReportObjectId",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    userid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="UserId", blank=True, null=True
    )  # Field name made lowercase.
    subscriptionid = models.TextField(
        db_column="SubscriptionId", blank=True, null=True
    )  # Field name made lowercase.
    inactiveflags = models.IntegerField(
        db_column="InactiveFlags", blank=True, null=True
    )  # Field name made lowercase.
    emaillist = models.TextField(
        db_column="EmailList", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    laststatus = models.TextField(
        db_column="LastStatus", blank=True, null=True
    )  # Field name made lowercase.
    lastruntime = models.DateTimeField(
        db_column="LastRunTime", blank=True, null=True
    )  # Field name made lowercase.
    subscriptionto = models.TextField(
        db_column="SubscriptionTo", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectSubscriptions"


class Reportobjecttagmemberships(models.Model):
    tagmembershipid = models.AutoField(
        db_column="TagMembershipID", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.ForeignKey(
        Reportobject, models.DO_NOTHING, db_column="ReportObjectID"
    )  # Field name made lowercase.
    tagid = models.ForeignKey(
        "Reportobjecttags", models.DO_NOTHING, db_column="TagID"
    )  # Field name made lowercase.
    line = models.IntegerField(
        db_column="Line", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectTagMemberships"


class Reportobjecttags(models.Model):
    tagid = models.AutoField(
        db_column="TagID", primary_key=True
    )  # Field name made lowercase.
    epictagid = models.DecimalField(
        db_column="EpicTagID", max_digits=18, decimal_places=0, blank=True, null=True
    )  # Field name made lowercase.
    tagname = models.CharField(
        db_column="TagName", max_length=200, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectTags"


class Reportobjecttype(models.Model):
    reportobjecttypeid = models.AutoField(
        db_column="ReportObjectTypeID", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(db_column="Name")  # Field name made lowercase.
    defaultepicmasterfile = models.CharField(
        db_column="DefaultEpicMasterFile", max_length=3, blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.
    shortname = models.TextField(
        db_column="ShortName", blank=True, null=True
    )  # Field name made lowercase.
    visible = models.CharField(
        db_column="Visible", max_length=1, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectType"


class Reporttaglinks(models.Model):
    reporttaglinkid = models.AutoField(
        db_column="ReportTagLinkId", primary_key=True
    )  # Field name made lowercase.
    reportid = models.IntegerField(db_column="ReportId")  # Field name made lowercase.
    tagid = models.ForeignKey(
        "Tags", models.DO_NOTHING, db_column="TagId"
    )  # Field name made lowercase.
    showinheader = models.TextField(
        db_column="ShowInHeader", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportTagLinks"


class Tags(models.Model):
    tagid = models.AutoField(
        db_column="TagId", primary_key=True
    )  # Field name made lowercase.
    name = models.CharField(
        db_column="Name", max_length=450, blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    priority = models.IntegerField(
        db_column="Priority", blank=True, null=True
    )  # Field name made lowercase.
    showinheader = models.TextField(
        db_column="ShowInHeader", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Tags"


class User(models.Model):
    userid = models.AutoField(
        db_column="UserID", primary_key=True
    )  # Field name made lowercase.
    username = models.TextField(db_column="Username")  # Field name made lowercase.
    employeeid = models.TextField(
        db_column="EmployeeID", blank=True, null=True
    )  # Field name made lowercase.
    accountname = models.TextField(
        db_column="AccountName", blank=True, null=True
    )  # Field name made lowercase.
    displayname = models.TextField(
        db_column="DisplayName", blank=True, null=True
    )  # Field name made lowercase.
    fullname = models.TextField(
        db_column="FullName", blank=True, null=True
    )  # Field name made lowercase.
    firstname = models.TextField(
        db_column="FirstName", blank=True, null=True
    )  # Field name made lowercase.
    lastname = models.TextField(
        db_column="LastName", blank=True, null=True
    )  # Field name made lowercase.
    department = models.TextField(
        db_column="Department", blank=True, null=True
    )  # Field name made lowercase.
    title = models.TextField(
        db_column="Title", blank=True, null=True
    )  # Field name made lowercase.
    phone = models.TextField(
        db_column="Phone", blank=True, null=True
    )  # Field name made lowercase.
    email = models.TextField(
        db_column="Email", blank=True, null=True
    )  # Field name made lowercase.
    base = models.TextField(
        db_column="Base", blank=True, null=True
    )  # Field name made lowercase.
    epicid = models.TextField(
        db_column="EpicId", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.
    lastlogin = models.DateTimeField(
        db_column="LastLogin", blank=True, null=True
    )  # Field name made lowercase.
    fullname_calc = models.TextField(
        db_column="Fullname_calc", blank=True, null=True
    )  # Field name made lowercase.
    firstname_calc = models.TextField(
        db_column="Firstname_calc", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "User"


class Usergroups(models.Model):
    groupid = models.AutoField(
        db_column="GroupId", primary_key=True
    )  # Field name made lowercase.
    accountname = models.TextField(
        db_column="AccountName", blank=True, null=True
    )  # Field name made lowercase.
    groupname = models.TextField(
        db_column="GroupName", blank=True, null=True
    )  # Field name made lowercase.
    groupemail = models.TextField(
        db_column="GroupEmail", blank=True, null=True
    )  # Field name made lowercase.
    grouptype = models.TextField(
        db_column="GroupType", blank=True, null=True
    )  # Field name made lowercase.
    groupsource = models.TextField(
        db_column="GroupSource", blank=True, null=True
    )  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.
    epicid = models.TextField(
        db_column="EpicId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserGroups"


class Usergroupsmembership(models.Model):
    membershipid = models.AutoField(
        db_column="MembershipId", primary_key=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    groupid = models.IntegerField(db_column="GroupId")  # Field name made lowercase.
    lastloaddate = models.DateTimeField(
        db_column="LastLoadDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserGroupsMembership"


class Efmigrationshistory(models.Model):
    migrationid = models.CharField(
        db_column="MigrationId", primary_key=True, max_length=150
    )  # Field name made lowercase.
    productversion = models.CharField(
        db_column="ProductVersion", max_length=32
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "__EFMigrationsHistory"
