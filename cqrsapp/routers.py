# cqrsapp/routers.py
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        # Users + Django auth tables → auth_db
        if model._meta.app_label == "cqrsex" and model.__name__ == "User":
            return "auth_db"
        if model._meta.app_label in {"auth", "contenttypes"}:
            return "auth_db"
        # باقي الجداول → default
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "cqrsex" and model.__name__ == "User":
            return "auth_db"
        if model._meta.app_label in {"auth", "contenttypes"}:
            return "auth_db"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Users + Permissions → auth_db
        if app_label in {"auth", "contenttypes"}:
            return db == "auth_db"
        if app_label == "cqrsex" and model_name == "user":
            return db == "auth_db"

        # باقي الجداول → default
        return db == "default"
