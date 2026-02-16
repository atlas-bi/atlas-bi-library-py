import os
import re
from pathlib import Path

import pyodbc
from django.conf import settings
from django.core.management.base import BaseCommand

# Mapping from old schema-qualified names to new flat names.
# Order matters: longer / more specific patterns first.
_TABLE_RENAMES: list[tuple[str, str]] = [
    # [atlas].schema.Table -> flat name
    ("[atlas].app.UserRoleLinks", "userRoleLinks"),
    ("[atlas].dbo.UserGroupsMembership", "userGroupsMembership"),
    ("[atlas].dbo.UserGroups", "userGroups"),
    # app.Table -> flat name
    ("app.ReportObjectDocMaintenanceLogs", "reportObjectDocMaintenanceLogs"),
    ("app.reportobjectdocfragilitytags", "reportObjectDocFragilityTags"),
    ("app.ReportObjectDocTerms", "reportObjectDocTerms"),
    ("app.ReportObject_doc", "reportObject_doc"),
    ("app.reportobjectimages_doc", "reportObjectImages_doc"),
    ("app.MaintenanceLogStatus", "maintenanceLogStatus"),
    ("app.MaintenanceLog", "maintenanceLog"),
    ("app.MaintenanceSchedule", "maintenanceSchedule"),
    ("app.UserFavoriteFolders", "userFavoriteFolders"),
    ("app.Term", "term"),
    # dbo.Table -> flat name
    ("dbo.ReportObjectRunDataBridge", "reportObjectRunDataBridge"),
    ("dbo.ReportObjectRunData", "reportObjectRunData"),
    ("dbo.ReportObjectHierarchy", "reportObjectHierarchy"),
    ("dbo.ReportObjectQuery", "reportObjectQuery"),
    ("dbo.ReportObjectType", "reportObjectType"),
    ("dbo.ReportObject", "reportObject"),
    ("dbo.[User]", "dbo.[user]"),
    ("dbo.UserGroups", "userGroups"),
    ("dbo.UserGroupsMembership", "userGroupsMembership"),
]

# Stored-procedure / function references that don't exist in our DB.
# We'll skip batches that try to EXECUTE them.
_SKIP_PROCS = [
    "app.Search_MasterDataUpdate",
    "app.CalculateReportRunTimeData",
    "app.CalculateReportRunData",
]


class Command(BaseCommand):
    help = "Seed SQL Server (dg_db) with demo data from the legacy seed script."

    @staticmethod
    def _strip_leading_comments(sql: str) -> str:
        s = sql.lstrip()

        # Strip leading /* ... */ comment blocks.
        while s.startswith("/*"):
            end = s.find("*/")
            if end == -1:
                return ""
            s = s[end + 2 :].lstrip()

        # Strip leading -- comment lines and blank lines.
        lines = s.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].lstrip()
            if not line or line.startswith("--"):
                i += 1
                continue
            break
        return "\n".join(lines[i:]).strip()

    def _get_raw_connection(self) -> pyodbc.Connection:
        """Build a raw pyodbc connection to the dg_db database."""
        db_settings = settings.DATABASES["dg_db"]
        host = db_settings.get("HOST", "dg_db")
        port = db_settings.get("PORT", "1433")
        user = db_settings.get("USER", "sa")
        pw = db_settings.get("PASSWORD", "")
        db_name = db_settings.get("NAME", "atlas")
        opts = db_settings.get("OPTIONS", {})
        driver = opts.get("driver", "ODBC Driver 18 for SQL Server")
        extra = opts.get("extra_params", "Encrypt=no;TrustServerCertificate=yes")

        dsn = (
            f"DRIVER={{{driver}}};SERVER={host},{port};"
            f"UID={user};PWD={pw};DATABASE={db_name};{extra}"
        )
        cn = pyodbc.connect(dsn, timeout=30)
        cn.autocommit = True
        return cn

    @staticmethod
    def _adapt_sql(sql_text: str) -> str:
        """Replace old schema-qualified table names with new flat names."""
        result = sql_text

        # Remove USE [atlas] statements
        result = re.sub(r"(?i)^USE\s+\[atlas\]\s*$", "-- USE [atlas] (removed)", result, flags=re.MULTILINE)

        # Replace table names (case-insensitive)
        for old, new in _TABLE_RENAMES:
            # Use word-boundary-aware replacement
            pattern = re.escape(old)
            result = re.sub(pattern, new, result, flags=re.IGNORECASE)

        # Replace object_id('app.X' ...) references
        for old, new in _TABLE_RENAMES:
            if old.startswith("app.") or old.startswith("dbo."):
                old_quoted = f"'{old}'"
                new_quoted = f"'{new}'"
                result = result.replace(old_quoted, new_quoted)

        # Replace [app].ProcName references for stored procs
        result = re.sub(r"\[app\]\.\[(\w+)\]", r"\1", result)

        return result

    def handle(self, *args, **options):
        seed_sql_path = os.environ.get("ATLAS_DEMO_SEED_SQL_PATH", "").strip()
        if not seed_sql_path:
            here = Path(__file__).resolve()
            for parent in [here, *here.parents]:
                for name in ("atlas-demo-seed_script.sql", "seed.sql"):
                    candidate = parent / name
                    if candidate.is_file():
                        seed_sql_path = str(candidate)
                        break
                if seed_sql_path:
                    break

        if not seed_sql_path:
            self.stderr.write(
                "Skipping seed: ATLAS_DEMO_SEED_SQL_PATH not set and "
                "atlas-demo-seed_script.sql not found."
            )
            return

        seed_file = Path(seed_sql_path)
        if not seed_file.is_file():
            self.stderr.write(f"Skipping seed: file not found at {seed_sql_path}")
            return

        self.stdout.write(f"Reading seed SQL from {seed_sql_path} ...")
        raw_sql = seed_file.read_text(encoding="utf-8", errors="ignore")

        # Adapt table names
        adapted_sql = self._adapt_sql(raw_sql)

        # Split on GO batch separators
        batches = re.split(r"^\s*GO\s*$", adapted_sql, flags=re.MULTILINE | re.IGNORECASE)

        cn = self._get_raw_connection()
        cur = cn.cursor()

        # Preflight: relax columns that the legacy seed script doesn't populate.
        # The seed SQL inserts into reportObject_doc without GitLabProjectURL.
        # If our schema made it NOT NULL, the seed will fail.
        try:
            cur.execute(
                """
                BEGIN TRY
                    IF COL_LENGTH('dbo.reportObject_doc', 'GitLabProjectURL') IS NOT NULL
                    BEGIN
                        ALTER TABLE dbo.reportObject_doc ALTER COLUMN GitLabProjectURL nvarchar(max) NULL;
                    END

                    IF COL_LENGTH('dbo.reportObject_doc', 'EnabledForHyperspace') IS NOT NULL
                    BEGIN
                        ALTER TABLE dbo.reportObject_doc ALTER COLUMN EnabledForHyperspace nvarchar(1) NULL;
                    END

                    IF COL_LENGTH('dbo.reportObject_doc', 'DoNotPurge') IS NOT NULL
                    BEGIN
                        ALTER TABLE dbo.reportObject_doc ALTER COLUMN DoNotPurge nvarchar(1) NULL;
                    END

                    IF COL_LENGTH('dbo.reportObject_doc', 'Hidden') IS NOT NULL
                    BEGIN
                        ALTER TABLE dbo.reportObject_doc ALTER COLUMN Hidden nvarchar(1) NULL;
                    END

                    IF COL_LENGTH('dbo.reportObject_doc', 'DeveloperNotes') IS NOT NULL
                    BEGIN
                        ALTER TABLE dbo.reportObject_doc ALTER COLUMN DeveloperNotes nvarchar(max) NULL;
                    END
                END TRY
                BEGIN CATCH
                    -- Non-fatal: continue even if ALTER isn't possible (e.g. type mismatch)
                END CATCH
                """
            )
        except pyodbc.Error:
            # Non-fatal
            pass

        # Preflight: the legacy seed references many UserId FKs. In this migrated schema
        # some rows may reference users that aren't present yet, which would block seeding.
        # For demo data we temporarily disable FK checks on the affected tables.
        try:
            cur.execute(
                """
                BEGIN TRY
                    IF OBJECT_ID('dbo.userGroupsMembership', 'U') IS NOT NULL
                        ALTER TABLE dbo.userGroupsMembership NOCHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObject_doc', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObject_doc NOCHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.term', 'U') IS NOT NULL
                        ALTER TABLE dbo.term NOCHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.userFavoriteFolders', 'U') IS NOT NULL
                        ALTER TABLE dbo.userFavoriteFolders NOCHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObjectHierarchy', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObjectHierarchy NOCHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObjectDocFragilityTags', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObjectDocFragilityTags NOCHECK CONSTRAINT ALL;
                END TRY
                BEGIN CATCH
                END CATCH
                """
            )
        except pyodbc.Error:
            pass

        executed = 0
        skipped = 0
        errors = 0

        for i, batch in enumerate(batches):
            batch = self._strip_leading_comments(batch)
            if not batch:
                continue

            # Skip batches that reference stored procs we don't have
            batch_lower = batch.lower()
            skip = False
            for proc in _SKIP_PROCS:
                if proc.lower() in batch_lower:
                    skip = True
                    break
            if skip:
                skipped += 1
                continue

            # Skip image data inserts (commented out in seed but just in case)
            if "reportobjectimages_doc" in batch_lower and "0x89504E47" in batch:
                skipped += 1
                continue

            try:
                cur.execute(batch)
                executed += 1
            except pyodbc.Error as e:
                err_msg = str(e)
                # Tolerable SQL Server error codes for demo seeding:
                #   2627/2601 - duplicate key
                #   1779 - table already has PK
                #   23000 - FK constraint (e.g. reserved-keyword table timing)
                #   3701/4902 - object not found
                #   102 - syntax error in dynamic SQL (optional procs)
                tolerable = ["2627", "2601", "1779", "3701", "4902"]
                if any(code in err_msg for code in tolerable):
                    skipped += 1
                    continue
                # Log but don't fail on FK and syntax errors
                if "23000" in err_msg or "42000" in err_msg:
                    self.stderr.write(
                        f"  Batch {i} warning (non-fatal): {err_msg[:200]}"
                    )
                    skipped += 1
                    continue
                self.stderr.write(f"  Batch {i} error: {err_msg[:200]}")
                errors += 1

        # Postflight: re-enable constraints (without validating existing rows).
        try:
            cur.execute(
                """
                BEGIN TRY
                    IF OBJECT_ID('dbo.userGroupsMembership', 'U') IS NOT NULL
                        ALTER TABLE dbo.userGroupsMembership WITH NOCHECK CHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObject_doc', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObject_doc WITH NOCHECK CHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.term', 'U') IS NOT NULL
                        ALTER TABLE dbo.term WITH NOCHECK CHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.userFavoriteFolders', 'U') IS NOT NULL
                        ALTER TABLE dbo.userFavoriteFolders WITH NOCHECK CHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObjectHierarchy', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObjectHierarchy WITH NOCHECK CHECK CONSTRAINT ALL;
                    IF OBJECT_ID('dbo.reportObjectDocFragilityTags', 'U') IS NOT NULL
                        ALTER TABLE dbo.reportObjectDocFragilityTags WITH NOCHECK CHECK CONSTRAINT ALL;
                END TRY
                BEGIN CATCH
                END CATCH
                """
            )
        except pyodbc.Error:
            pass

        cur.close()
        cn.close()

        self.stdout.write(
            f"  Executed {executed} batches, skipped {skipped}, errors {errors}."
        )
        if errors == 0:
            self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        else:
            self.stderr.write(
                self.style.WARNING(f"Seeding completed with {errors} errors.")
            )
