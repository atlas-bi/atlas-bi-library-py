"""Atlas database router for sql server db."""


class IndexRouter:
    """Base router setup."""

    def db_for_read(self, model, **hints):
        """Set read db name."""
        if model._meta.app_label == "index":
            return "dg_db"
        return None

    def db_for_write(self, model, **hints):
        """Set write db name."""
        if model._meta.app_label == "index":
            return "dg_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Set nothing."""
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Disable migrations on dg_db, this db is sql server.."""
        if app_label == "index":
            return db == "dg_db"
        if db == "dg_db":
            return False
        return None
