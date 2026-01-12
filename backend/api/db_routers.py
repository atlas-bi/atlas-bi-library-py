from os import environ


def _labels_from_env(name: str, default: str = "") -> set[str]:
    raw = environ.get(name, default)
    return {x.strip() for x in raw.split(",") if x.strip()}


class DgDbRouter:
    def __init__(self) -> None:
        self._app_labels = _labels_from_env("DG_DB_APP_LABELS", "")

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self._app_labels:
            return "dg_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self._app_labels:
            return "dg_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self._app_labels:
            return db == "dg_db"
        if db == "dg_db":
            return False
        return None
