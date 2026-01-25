class ActivosRouter:
    """
    A router to control all database operations on models in the
    activos application.
    """
    route_app_labels = {'activos'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read ativos models go to legacy_activos.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'legacy_activos'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write ativos models go to legacy_activos.
        """
        if model._meta.app_label in self.route_app_labels:
            return None # Prevent writes for now, or return 'legacy_activos' if needed
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the actives app is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the activos app only appears in the 'legacy_activos'
        database.
        """
        if app_label in self.route_app_labels:
            return False # DO NOT MIGRATE LEGACY DB
        return None
