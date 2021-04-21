from mongoendjin.utils.functional import cached_property


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

    def __init__(self, settings=None):
        self._settings = settings
        self._connections = {}

    @cached_property
    def settings(self):
        self._settings = self.configure_settings(self._settings)
        return self._settings

    def configure_settings(self, settings):
        if settings is None:
            #settings = getattr(django_settings, self.settings_name)
            settings = {}
        return settings

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