from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("atlas_index", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql=r"""
            IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'app')
            BEGIN
                EXEC('CREATE SCHEMA app');
            END;

            IF OBJECT_ID(N'dbo.Groups', N'U') IS NOT NULL AND OBJECT_ID(N'dbo.UserGroups', N'U') IS NULL
            BEGIN
                EXEC sp_rename 'dbo.Groups', 'UserGroups';
            END;

            IF OBJECT_ID(N'dbo.UserGroupMemberships', N'U') IS NOT NULL AND OBJECT_ID(N'dbo.UserGroupsMembership', N'U') IS NULL
            BEGIN
                EXEC sp_rename 'dbo.UserGroupMemberships', 'UserGroupsMembership';
            END;

            IF OBJECT_ID(N'dbo.UserRoleLinks', N'U') IS NOT NULL AND OBJECT_ID(N'app.UserRoleLinks', N'U') IS NULL
            BEGIN
                EXEC('ALTER SCHEMA app TRANSFER dbo.UserRoleLinks');
            END;

            IF COL_LENGTH('dbo.[User]', 'FullName') IS NULL
                ALTER TABLE dbo.[User] ADD FullName nvarchar(max) NOT NULL CONSTRAINT DF_User_FullName DEFAULT('');
            IF COL_LENGTH('dbo.[User]', 'FirstName') IS NULL
                ALTER TABLE dbo.[User] ADD FirstName nvarchar(max) NOT NULL CONSTRAINT DF_User_FirstName DEFAULT('');
            IF COL_LENGTH('dbo.[User]', 'LastName') IS NULL
                ALTER TABLE dbo.[User] ADD LastName nvarchar(max) NOT NULL CONSTRAINT DF_User_LastName DEFAULT('');
            IF COL_LENGTH('dbo.[User]', 'Department') IS NULL
                ALTER TABLE dbo.[User] ADD Department nvarchar(max) NOT NULL CONSTRAINT DF_User_Department DEFAULT('');
            IF COL_LENGTH('dbo.[User]', 'Title') IS NULL
                ALTER TABLE dbo.[User] ADD Title nvarchar(max) NOT NULL CONSTRAINT DF_User_Title DEFAULT('');

            IF COL_LENGTH('dbo.[UserGroups]', 'GroupEmail') IS NULL
                ALTER TABLE dbo.[UserGroups] ADD GroupEmail nvarchar(max) NOT NULL CONSTRAINT DF_UserGroups_GroupEmail DEFAULT('');
            IF COL_LENGTH('dbo.[UserGroups]', 'GroupType') IS NULL
                ALTER TABLE dbo.[UserGroups] ADD GroupType nvarchar(max) NOT NULL CONSTRAINT DF_UserGroups_GroupType DEFAULT('');
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
