# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Analytics(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    language = models.TextField(
        db_column="Language", blank=True, null=True
    )  # Field name made lowercase.
    useragent = models.TextField(
        db_column="UserAgent", blank=True, null=True
    )  # Field name made lowercase.
    hostname = models.TextField(
        db_column="Hostname", blank=True, null=True
    )  # Field name made lowercase.
    href = models.TextField(
        db_column="Href", blank=True, null=True
    )  # Field name made lowercase.
    protocol = models.TextField(
        db_column="Protocol", blank=True, null=True
    )  # Field name made lowercase.
    search = models.TextField(
        db_column="Search", blank=True, null=True
    )  # Field name made lowercase.
    pathname = models.TextField(
        db_column="Pathname", blank=True, null=True
    )  # Field name made lowercase.
    hash = models.TextField(
        db_column="Hash", blank=True, null=True
    )  # Field name made lowercase.
    screenheight = models.TextField(
        db_column="ScreenHeight", blank=True, null=True
    )  # Field name made lowercase.
    screenwidth = models.TextField(
        db_column="ScreenWidth", blank=True, null=True
    )  # Field name made lowercase.
    origin = models.TextField(
        db_column="Origin", blank=True, null=True
    )  # Field name made lowercase.
    loadtime = models.TextField(
        db_column="LoadTime", blank=True, null=True
    )  # Field name made lowercase.
    accessdatetime = models.DateTimeField(
        db_column="AccessDateTime", blank=True, null=True
    )  # Field name made lowercase.
    referrer = models.TextField(
        db_column="Referrer", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    zoom = models.FloatField(
        db_column="Zoom", blank=True, null=True
    )  # Field name made lowercase.
    epic = models.IntegerField(
        db_column="Epic", blank=True, null=True
    )  # Field name made lowercase.
    active = models.IntegerField(
        db_column="Active", blank=True, null=True
    )  # Field name made lowercase.
    pageid = models.TextField(
        db_column="PageId", blank=True, null=True
    )  # Field name made lowercase.
    sessionid = models.TextField(
        db_column="SessionId", blank=True, null=True
    )  # Field name made lowercase.
    pagetime = models.IntegerField(
        db_column="PageTime", blank=True, null=True
    )  # Field name made lowercase.
    updatetime = models.DateTimeField(
        db_column="UpdateTime", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Analytics"


class Analyticserror(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    statuscode = models.IntegerField(
        db_column="StatusCode", blank=True, null=True
    )  # Field name made lowercase.
    message = models.TextField(
        db_column="Message", blank=True, null=True
    )  # Field name made lowercase.
    trace = models.TextField(
        db_column="Trace", blank=True, null=True
    )  # Field name made lowercase.
    logdatetime = models.DateTimeField(
        db_column="LogDateTime", blank=True, null=True
    )  # Field name made lowercase.
    handled = models.IntegerField(
        db_column="Handled", blank=True, null=True
    )  # Field name made lowercase.
    updatetime = models.DateTimeField(
        db_column="UpdateTime", blank=True, null=True
    )  # Field name made lowercase.
    useragent = models.TextField(
        db_column="UserAgent", blank=True, null=True
    )  # Field name made lowercase.
    referer = models.TextField(
        db_column="Referer", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "AnalyticsError"


class Analyticstrace(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    level = models.IntegerField(
        db_column="Level", blank=True, null=True
    )  # Field name made lowercase.
    message = models.TextField(
        db_column="Message", blank=True, null=True
    )  # Field name made lowercase.
    logger = models.TextField(
        db_column="Logger", blank=True, null=True
    )  # Field name made lowercase.
    logdatetime = models.DateTimeField(
        db_column="LogDateTime", blank=True, null=True
    )  # Field name made lowercase.
    logid = models.TextField(
        db_column="LogId", blank=True, null=True
    )  # Field name made lowercase.
    handled = models.IntegerField(
        db_column="Handled", blank=True, null=True
    )  # Field name made lowercase.
    updatetime = models.DateTimeField(
        db_column="UpdateTime", blank=True, null=True
    )  # Field name made lowercase.
    useragent = models.TextField(
        db_column="UserAgent", blank=True, null=True
    )  # Field name made lowercase.
    referer = models.TextField(
        db_column="Referer", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "AnalyticsTrace"


class Collection(models.Model):
    collectionid = models.AutoField(
        db_column="CollectionId", primary_key=True
    )  # Field name made lowercase.
    initiativeid = models.ForeignKey(
        "Initiative", models.DO_NOTHING, db_column="InitiativeId", blank=True, null=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    purpose = models.TextField(
        db_column="Purpose", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    operationownerid = models.IntegerField(
        db_column="OperationOwnerId", blank=True, null=True
    )  # Field name made lowercase.
    executiveownerid = models.IntegerField(
        db_column="ExecutiveOwnerId", blank=True, null=True
    )  # Field name made lowercase.
    analyticsownerid = models.IntegerField(
        db_column="AnalyticsOwnerId", blank=True, null=True
    )  # Field name made lowercase.
    datamanagerid = models.IntegerField(
        db_column="DataManagerId", blank=True, null=True
    )  # Field name made lowercase.
    financialimpact = models.ForeignKey(
        "Financialimpact",
        models.DO_NOTHING,
        db_column="FinancialImpact",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    strategicimportance = models.ForeignKey(
        "Strategicimportance",
        models.DO_NOTHING,
        db_column="StrategicImportance",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    externaldocumentationurl = models.TextField(
        db_column="ExternalDocumentationUrl", blank=True, null=True
    )  # Field name made lowercase.
    lastupdatedate = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )  # Field name made lowercase.
    lastupdateuser = models.IntegerField(
        db_column="LastUpdateUser", blank=True, null=True
    )  # Field name made lowercase.
    hidden = models.CharField(
        db_column="Hidden", max_length=1, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Collection"


class Collectionreport(models.Model):
    linkid = models.AutoField(
        db_column="LinkId", primary_key=True
    )  # Field name made lowercase.
    reportid = models.IntegerField(db_column="ReportId")  # Field name made lowercase.
    collectionid = models.ForeignKey(
        Collection, models.DO_NOTHING, db_column="CollectionId"
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "CollectionReport"


class Collectionterm(models.Model):
    linkid = models.AutoField(
        db_column="LinkId", primary_key=True
    )  # Field name made lowercase.
    termid = models.IntegerField(db_column="TermId")  # Field name made lowercase.
    collectionid = models.ForeignKey(
        Collection, models.DO_NOTHING, db_column="CollectionId"
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "CollectionTerm"


class Estimatedrunfrequency(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "EstimatedRunFrequency"


class Financialimpact(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "FinancialImpact"


class Fragility(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Fragility"


class Fragilitytag(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "FragilityTag"


class Globalsitesettings(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    value = models.TextField(
        db_column="Value", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "GlobalSiteSettings"


class Grouprolelinks(models.Model):
    grouprolelinksid = models.AutoField(
        db_column="GroupRoleLinksId", primary_key=True
    )  # Field name made lowercase.
    groupid = models.IntegerField(db_column="GroupId")  # Field name made lowercase.
    userrolesid = models.ForeignKey(
        "Userroles", models.DO_NOTHING, db_column="UserRolesId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "GroupRoleLinks"


class Initiative(models.Model):
    initiativeid = models.AutoField(
        db_column="InitiativeId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    operationownerid = models.IntegerField(
        db_column="OperationOwnerId", blank=True, null=True
    )  # Field name made lowercase.
    executiveownerid = models.IntegerField(
        db_column="ExecutiveOwnerId", blank=True, null=True
    )  # Field name made lowercase.
    financialimpact = models.ForeignKey(
        Financialimpact,
        models.DO_NOTHING,
        db_column="FinancialImpact",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    strategicimportance = models.ForeignKey(
        "Strategicimportance",
        models.DO_NOTHING,
        db_column="StrategicImportance",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    lastupdatedate = models.DateTimeField(
        db_column="LastUpdateDate", blank=True, null=True
    )  # Field name made lowercase.
    lastupdateuser = models.IntegerField(
        db_column="LastUpdateUser", blank=True, null=True
    )  # Field name made lowercase.
    hidden = models.CharField(
        db_column="Hidden", max_length=1, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Initiative"


class MailConversations(models.Model):
    conversationid = models.AutoField(
        db_column="ConversationId", primary_key=True
    )  # Field name made lowercase.
    messageid = models.ForeignKey(
        "MailMessages", models.DO_NOTHING, db_column="MessageId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Conversations"


class MailDrafts(models.Model):
    draftid = models.AutoField(
        db_column="DraftId", primary_key=True
    )  # Field name made lowercase.
    subject = models.TextField(
        db_column="Subject", blank=True, null=True
    )  # Field name made lowercase.
    message = models.TextField(
        db_column="Message", blank=True, null=True
    )  # Field name made lowercase.
    editdate = models.DateTimeField(
        db_column="EditDate", blank=True, null=True
    )  # Field name made lowercase.
    messagetypeid = models.IntegerField(
        db_column="MessageTypeId", blank=True, null=True
    )  # Field name made lowercase.
    fromuserid = models.IntegerField(
        db_column="FromUserId", blank=True, null=True
    )  # Field name made lowercase.
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, null=True
    )  # Field name made lowercase.
    recipients = models.TextField(
        db_column="Recipients", blank=True, null=True
    )  # Field name made lowercase.
    replytomessageid = models.IntegerField(
        db_column="ReplyToMessageId", blank=True, null=True
    )  # Field name made lowercase.
    replytoconvid = models.IntegerField(
        db_column="ReplyToConvId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Drafts"


class MailFoldermessages(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    folderid = models.ForeignKey(
        "MailFolders", models.DO_NOTHING, db_column="FolderId", blank=True, null=True
    )  # Field name made lowercase.
    messageid = models.ForeignKey(
        "MailMessages", models.DO_NOTHING, db_column="MessageId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_FolderMessages"


class MailFolders(models.Model):
    folderid = models.AutoField(
        db_column="FolderId", primary_key=True
    )  # Field name made lowercase.
    parentfolderid = models.IntegerField(
        db_column="ParentFolderId", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(
        db_column="UserId", blank=True, null=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Folders"


class MailMessagetype(models.Model):
    messagetypeid = models.AutoField(
        db_column="MessageTypeId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_MessageType"


class MailMessages(models.Model):
    messageid = models.AutoField(
        db_column="MessageId", primary_key=True
    )  # Field name made lowercase.
    subject = models.TextField(
        db_column="Subject", blank=True, null=True
    )  # Field name made lowercase.
    message = models.TextField(
        db_column="Message", blank=True, null=True
    )  # Field name made lowercase.
    senddate = models.DateTimeField(
        db_column="SendDate", blank=True, null=True
    )  # Field name made lowercase.
    messagetypeid = models.ForeignKey(
        MailMessagetype,
        models.DO_NOTHING,
        db_column="MessageTypeId",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    fromuserid = models.IntegerField(
        db_column="FromUserId", blank=True, null=True
    )  # Field name made lowercase.
    messageplaintext = models.TextField(
        db_column="MessagePlainText", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Messages"


class MailRecipients(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    messageid = models.ForeignKey(
        MailMessages, models.DO_NOTHING, db_column="MessageId", blank=True, null=True
    )  # Field name made lowercase.
    touserid = models.IntegerField(
        db_column="ToUserId", blank=True, null=True
    )  # Field name made lowercase.
    readdate = models.DateTimeField(
        db_column="ReadDate", blank=True, null=True
    )  # Field name made lowercase.
    alertdisplayed = models.IntegerField(
        db_column="AlertDisplayed", blank=True, null=True
    )  # Field name made lowercase.
    togroupid = models.IntegerField(
        db_column="ToGroupId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Recipients"


class MailRecipientsDeleted(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    messageid = models.IntegerField(
        db_column="MessageId", blank=True, null=True
    )  # Field name made lowercase.
    touserid = models.IntegerField(
        db_column="ToUserId", blank=True, null=True
    )  # Field name made lowercase.
    readdate = models.DateTimeField(
        db_column="ReadDate", blank=True, null=True
    )  # Field name made lowercase.
    alertdisplayed = models.IntegerField(
        db_column="AlertDisplayed", blank=True, null=True
    )  # Field name made lowercase.
    togroupid = models.IntegerField(
        db_column="ToGroupId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Mail_Recipients_Deleted"


class MaingenancelogBackup(models.Model):
    maintenancelogid = models.AutoField(
        db_column="MaintenanceLogID"
    )  # Field name made lowercase.
    maintainerid = models.IntegerField(
        db_column="MaintainerID", blank=True, null=True
    )  # Field name made lowercase.
    maintenancedate = models.DateTimeField(
        db_column="MaintenanceDate", blank=True, null=True
    )  # Field name made lowercase.
    comment = models.TextField(
        db_column="Comment", blank=True, null=True
    )  # Field name made lowercase.
    maintenancelogstatusid = models.IntegerField(
        db_column="MaintenanceLogStatusID", blank=True, null=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "MaingenanceLog_Backup"


class Maintenancelog(models.Model):
    maintenancelogid = models.AutoField(
        db_column="MaintenanceLogId", primary_key=True
    )  # Field name made lowercase.
    maintainerid = models.IntegerField(
        db_column="MaintainerId"
    )  # Field name made lowercase.
    maintenancedate = models.DateTimeField(
        db_column="MaintenanceDate", blank=True, null=True
    )  # Field name made lowercase.
    comment = models.TextField(
        db_column="Comment", blank=True, null=True
    )  # Field name made lowercase.
    maintenancelogstatusid = models.ForeignKey(
        "Maintenancelogstatus",
        models.DO_NOTHING,
        db_column="MaintenanceLogStatusId",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    reportid = models.IntegerField(db_column="ReportId")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "MaintenanceLog"


class Maintenancelogstatus(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(db_column="Name")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "MaintenanceLogStatus"


class Maintenanceschedule(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(db_column="Name")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "MaintenanceSchedule"


class Organizationalvalue(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "OrganizationalValue"


class Reportobjectdocfragilitytags(models.Model):
    linkid = models.AutoField(
        db_column="LinkId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.ForeignKey(
        "ReportobjectDoc", models.DO_NOTHING, db_column="ReportObjectId"
    )  # Field name made lowercase.
    fragilitytagid = models.ForeignKey(
        Fragilitytag, models.DO_NOTHING, db_column="FragilityTagId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectDocFragilityTags"


class ReportobjectdocmaintenancelogsBackup(models.Model):
    linkid = models.AutoField(db_column="LinkId")  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectID"
    )  # Field name made lowercase.
    maintenancelogid = models.IntegerField(
        db_column="MaintenanceLogID"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectDocMaintenanceLogs_backup"


class Reportobjectdocterms(models.Model):
    linkid = models.AutoField(
        db_column="LinkId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.ForeignKey(
        "ReportobjectDoc", models.DO_NOTHING, db_column="ReportObjectId"
    )  # Field name made lowercase.
    termid = models.ForeignKey(
        "Term", models.DO_NOTHING, db_column="TermId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectDocTerms"


class ReportobjectimagesDoc(models.Model):
    imageid = models.AutoField(
        db_column="ImageId", primary_key=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId"
    )  # Field name made lowercase.
    imageordinal = models.IntegerField(
        db_column="ImageOrdinal"
    )  # Field name made lowercase.
    imagedata = models.BinaryField(db_column="ImageData")  # Field name made lowercase.
    imagesource = models.TextField(
        db_column="ImageSource", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObjectImages_doc"


class ReportobjectDoc(models.Model):
    reportobjectid = models.IntegerField(
        db_column="ReportObjectID", primary_key=True
    )  # Field name made lowercase.
    operationalowneruserid = models.IntegerField(
        db_column="OperationalOwnerUserID", blank=True, null=True
    )  # Field name made lowercase.
    requester = models.IntegerField(
        db_column="Requester", blank=True, null=True
    )  # Field name made lowercase.
    gitlabprojecturl = models.TextField(
        db_column="GitLabProjectURL", blank=True, null=True
    )  # Field name made lowercase.
    developerdescription = models.TextField(
        db_column="DeveloperDescription", blank=True, null=True
    )  # Field name made lowercase.
    keyassumptions = models.TextField(
        db_column="KeyAssumptions", blank=True, null=True
    )  # Field name made lowercase.
    organizationalvalueid = models.ForeignKey(
        Organizationalvalue,
        models.DO_NOTHING,
        db_column="OrganizationalValueID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    estimatedrunfrequencyid = models.ForeignKey(
        Estimatedrunfrequency,
        models.DO_NOTHING,
        db_column="EstimatedRunFrequencyID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    fragilityid = models.ForeignKey(
        Fragility, models.DO_NOTHING, db_column="FragilityID", blank=True, null=True
    )  # Field name made lowercase.
    executivevisibilityyn = models.CharField(
        db_column="ExecutiveVisibilityYN", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    maintenancescheduleid = models.ForeignKey(
        Maintenanceschedule,
        models.DO_NOTHING,
        db_column="MaintenanceScheduleID",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    lastupdatedatetime = models.DateTimeField(
        db_column="LastUpdateDateTime", blank=True, null=True
    )  # Field name made lowercase.
    createddatetime = models.DateTimeField(
        db_column="CreatedDateTime", blank=True, null=True
    )  # Field name made lowercase.
    createdby = models.IntegerField(
        db_column="CreatedBy", blank=True, null=True
    )  # Field name made lowercase.
    updatedby = models.IntegerField(
        db_column="UpdatedBy", blank=True, null=True
    )  # Field name made lowercase.
    enabledforhyperspace = models.CharField(
        db_column="EnabledForHyperspace", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    donotpurge = models.CharField(
        db_column="DoNotPurge", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    hidden = models.CharField(
        db_column="Hidden", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    developernotes = models.TextField(
        db_column="DeveloperNotes", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportObject_doc"


class Reportservicerequests(models.Model):
    servicerequestid = models.AutoField(
        db_column="ServiceRequestId", primary_key=True
    )  # Field name made lowercase.
    ticketnumber = models.TextField(
        db_column="TicketNumber", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    reportobjectid = models.IntegerField(
        db_column="ReportObjectId"
    )  # Field name made lowercase.
    ticketurl = models.TextField(
        db_column="TicketUrl", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ReportServiceRequests"


class Rolepermissionlinks(models.Model):
    rolepermissionlinksid = models.AutoField(
        db_column="RolePermissionLinksId", primary_key=True
    )  # Field name made lowercase.
    roleid = models.ForeignKey(
        "Userroles", models.DO_NOTHING, db_column="RoleId"
    )  # Field name made lowercase.
    rolepermissionsid = models.ForeignKey(
        "Rolepermissions", models.DO_NOTHING, db_column="RolePermissionsId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "RolePermissionLinks"


class Rolepermissions(models.Model):
    rolepermissionsid = models.AutoField(
        db_column="RolePermissionsId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "RolePermissions"


class Shareditems(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    sharedfromuserid = models.IntegerField(
        db_column="SharedFromUserId", blank=True, null=True
    )  # Field name made lowercase.
    sharedtouserid = models.IntegerField(
        db_column="SharedToUserId", blank=True, null=True
    )  # Field name made lowercase.
    url = models.TextField(
        db_column="Url", blank=True, null=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    sharedate = models.DateTimeField(
        db_column="ShareDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "SharedItems"


class Starredcollections(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    collectionid = models.ForeignKey(
        Collection, models.DO_NOTHING, db_column="Collectionid"
    )  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredCollections"


class Starredgroups(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    groupid = models.IntegerField(db_column="Groupid")  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredGroups"


class Starredinitiatives(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    initiativeid = models.ForeignKey(
        Initiative, models.DO_NOTHING, db_column="Initiativeid"
    )  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredInitiatives"


class Starredreports(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    reportid = models.IntegerField(db_column="Reportid")  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredReports"


class Starredsearches(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    search = models.TextField(
        db_column="Search", blank=True, null=True
    )  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredSearches"


class Starredterms(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    termid = models.IntegerField(db_column="Termid")  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredTerms"


class Starredusers(models.Model):
    starid = models.AutoField(
        db_column="StarId", primary_key=True
    )  # Field name made lowercase.
    rank = models.IntegerField(
        db_column="Rank", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="Userid")  # Field name made lowercase.
    ownerid = models.IntegerField(db_column="Ownerid")  # Field name made lowercase.
    folderid = models.ForeignKey(
        "Userfavoritefolders",
        models.DO_NOTHING,
        db_column="Folderid",
        blank=True,
        null=True,
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StarredUsers"


class Strategicimportance(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StrategicImportance"


class Term(models.Model):
    termid = models.AutoField(
        db_column="TermId", primary_key=True
    )  # Field name made lowercase.
    name = models.CharField(
        db_column="Name", max_length=255, blank=True, null=True
    )  # Field name made lowercase.
    summary = models.CharField(
        db_column="Summary", max_length=4000, blank=True, null=True
    )  # Field name made lowercase.
    technicaldefinition = models.TextField(
        db_column="TechnicalDefinition", blank=True, null=True
    )  # Field name made lowercase.
    approvedyn = models.CharField(
        db_column="ApprovedYN", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    approvaldatetime = models.DateTimeField(
        db_column="ApprovalDateTime", blank=True, null=True
    )  # Field name made lowercase.
    approvedbyuserid = models.IntegerField(
        db_column="ApprovedByUserId", blank=True, null=True
    )  # Field name made lowercase.
    hasexternalstandardyn = models.CharField(
        db_column="HasExternalStandardYN", max_length=1, blank=True, null=True
    )  # Field name made lowercase.
    externalstandardurl = models.CharField(
        db_column="ExternalStandardUrl", max_length=4000, blank=True, null=True
    )  # Field name made lowercase.
    validfromdatetime = models.DateTimeField(
        db_column="ValidFromDateTime", blank=True, null=True
    )  # Field name made lowercase.
    validtodatetime = models.DateTimeField(
        db_column="ValidToDateTime", blank=True, null=True
    )  # Field name made lowercase.
    updatedbyuserid = models.IntegerField(
        db_column="UpdatedByUserId", blank=True, null=True
    )  # Field name made lowercase.
    lastupdateddatetime = models.DateTimeField(
        db_column="LastUpdatedDateTime", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Term"


class Userfavoritefolders(models.Model):
    userfavoritefolderid = models.AutoField(
        db_column="UserFavoriteFolderId", primary_key=True
    )  # Field name made lowercase.
    foldername = models.TextField(
        db_column="FolderName", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    folderrank = models.IntegerField(
        db_column="FolderRank", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserFavoriteFolders"


class Userpreferences(models.Model):
    userpreferenceid = models.AutoField(
        db_column="UserPreferenceId", primary_key=True
    )  # Field name made lowercase.
    itemtype = models.TextField(
        db_column="ItemType", blank=True, null=True
    )  # Field name made lowercase.
    itemvalue = models.IntegerField(
        db_column="ItemValue", blank=True, null=True
    )  # Field name made lowercase.
    itemid = models.IntegerField(
        db_column="ItemId", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserPreferences"


class Userrolelinks(models.Model):
    userrolelinksid = models.AutoField(
        db_column="UserRoleLinksId", primary_key=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    userrolesid = models.ForeignKey(
        "Userroles", models.DO_NOTHING, db_column="UserRolesId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserRoleLinks"


class Userroles(models.Model):
    userrolesid = models.AutoField(
        db_column="UserRolesId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(
        db_column="Name", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserRoles"


class Usersettings(models.Model):
    id = models.AutoField(
        db_column="Id", primary_key=True
    )  # Field name made lowercase.
    userid = models.IntegerField(db_column="UserId")  # Field name made lowercase.
    name = models.CharField(
        db_column="Name", max_length=450, blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description", blank=True, null=True
    )  # Field name made lowercase.
    value = models.TextField(
        db_column="Value", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "UserSettings"
