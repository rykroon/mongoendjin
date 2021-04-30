from pymongo import MongoClient

from mongoendjin.utils.connection import BaseConnectionHandler

DEFAULT_DB_ALIAS = 'default'


class ConnectionHandler(BaseConnectionHandler):

    def configure_settings(self, databases):
        databases = super().configure_settings(databases)
        if DEFAULT_DB_ALIAS not in databases:
            raise Exception("Improperly Configured.")
        return databases

    @property
    def databases(self):
        return self.settings

    def ensure_defaults(self, alias):
        """
        Put the defaults into the settings dictionary for a given connection
        where no settings is provided.
        """
        try:
            conn = self.databases[alias]
        except KeyError:
            raise self.exception_class(f"The connection '{alias}' doesn't exist.")

        for setting in ['NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']:
            conn.setdefault(setting, '')

    def create_connection(self, alias):
        self.ensure_defaults(alias)
        db = self.databases[alias]

        if not db['USER'] and not db['PASSWORD']:
            conn = MongoClient(
                host=db['HOST'] or None,
                port=db['PORT'] or None
            )
            db = conn[db['NAME']]
            return db

        else:
            uri_format = 'mongodb://{user}:{password}@{host}:{port}'
            uri = uri_format.format(
                db['USER'], db['PASSWORD'], 
                db['HOST'], db['PORT']
            )
            conn = MongoClient(host=uri)
            db = conn[db['NAME']]
            return db


class ConnectionRouter:
    pass
