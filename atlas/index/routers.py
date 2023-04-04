"""Atlas database router for sql server db."""
# pylint: disable=W0613, C0103, W0212
from typing import Any, Optional, Union

from django.db import models


class IndexRouter:
    """Base router setup."""

    def db_for_read(self, model: models.Model, **hints: Any) -> Optional[str]:
        """Set read db name."""
        if model._meta.app_label == "index":
            return "dg_db"
        return None

    def db_for_write(self, model: models.Model, **hints: Any) -> Optional[str]:
        """Set write db name."""
        if model._meta.app_label == "index":
            return "dg_db"
        return None

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> None:
        """Set nothing."""
        return None

    def allow_migrate(
        self, db: str, app_label: str, model_name: Optional[str] = None, **hints: Any
    ) -> Optional[Union[str, bool]]:
        """Disable migrations on dg_db, this db is sql server.."""
        if app_label == "index":
            return db == "dg_db"
        if db == "dg_db":
            return False
        return None
