from mongoendjin.utils.connection import BaseConnectionHandler

DEFAULT_DB_ALIAS = 'default'


class ConnectionHandler(BaseConnectionHandler):

    def create_connection(self, alias):
        pass


class ConnectionRouter:
    pass
