from django.db.backends.mysql.base import DatabaseWrapper as MysqlDatabaseWrapper

class DatabaseWrapper(MysqlDatabaseWrapper):
    def check_database_version_supported(self):
        """
        Bypass Django's version check to allow legacy MySQL versions.
        """
        pass
