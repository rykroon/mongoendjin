from pymongo import MongoClient

from mongoendjin.utils.connection import BaseConnectionHandler

DEFAULT_DB_ALIAS = 'default'



class MyConnectionHandler:

    def __init__(self, settings):
        """
            settings is a dictionary containing aliases as keys and kwargs
            to be passed into MongoClient as values.
        """
        self._settings = settings
        self._connections = {}

    def __getitem__(self, key):
        try:
            return self._connections[key]
        except KeyError:
            if key not in self._settings:
                raise Exception

        kwargs = self._settings[key]
        conn = MongoClient(**kwargs)
        self._connections[alias] = conn
        return conn

    def __setitem__(self, key, value):
        if not isinstance(value, MongoClient):
            raise Exception

        self._connections[key] = value

    def __delitem__(self, key):
        del self._connections[key]


class ConnectionDoesNotExist(Exception):
    pass


class BaseConnectionHandler:
    """
        Note to self:
            This class can be simplified a lot.
            It can also be less Django-like
    """

    exception_class = ConnectionDoesNotExist
    thread_critical = False

    def __init__(self, settings):
        self._settings = settings
        self._connections = {}

    @property
    def settings(self):
        return self._settings

    def create_connection(self, alias):
        raise NotImplementedError('Subclasses must implement create_connection().')

    def __getitem__(self, alias):
        try:
            return self._connections[alias]
        except KeyError:
            if alias not in self.settings:
                raise self.exception_class(f"The connection '{alias}' doesn't exist.")

        conn = self.create_connection(alias)
        self._connections[alias] = conn
        return conn

    def __setitem__(self, key, value):
        self._connections[key] = value

    def __delitem__(self, key):
        del self._connections[key]

    def __iter__(self):
        return iter(self.settings)

    def all(self):
        return [self[alias] for alias in self]


class ConnectionHandler(BaseConnectionHandler):

    def create_connection(self, alias):
        settings = self.settings[alias]
        conn = MongoClient(**settings)
        return conn


class ConnectionRouter:
    pass
