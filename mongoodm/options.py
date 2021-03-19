import copy
from .errors import FieldDoesNotExist
from .fields import Field
from .utils import CachedProperty


DEFAULT_NAMES = (
    'abstract',
    'collection_name',
    'connection_name',
    'database_name',
    'indexes'
)


class Options:

    def __init__(self, meta):
        self.meta = meta
        self.local_fields = []
        self.local_managers = []

    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.model = cls

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]

                for attr_name in DEFAULT_NAMES:
                    if attr_name in meta_attrs:
                        setattr(self, attr_name, meta_attrs.pop(attr_name))

            if meta_attrs:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs))

    def add_field(self, field):
        self.local_fields.append(field)

    def add_manager(self, manager):
        self.local_managers.append(manager)

    def get_field(self, field_name):
        try:
            return self.fields_map[field_name]
        except KeyError:
            raise FieldDoesNotExist

    @CachedProperty
    def fields(self):
        return list(self.fields_map.values())

    @CachedProperty
    def fields(self):
        fields = []
        seen_fields = set()
        bases = (b for b in self.model.mro() if hasattr(b, '_meta'))
        for base in bases:
            for field in base._meta.local_fields:
                if field.name in seen_fields:
                    continue
                field = copy.copy(field)
                field.model = self.model
                seen_fields.add(field.name)
                fields.append(field)

        return fields

    @CachedProperty
    def fields_map(self):
        return {field.name: field for field in self.fields}

    @CachedProperty
    def managers(self):
        managers = []
        seen_managers = set()
        bases = (b for b in self.model.mro() if hasattr(b, '_meta'))
        for base in bases:
            for manager in base._meta.local_managers:
                if manager.name in seen_managers:
                    continue

                manager = copy.copy(manager)
                manager.model = self.model
                seen_managers.add(manager.name)
                managers.append(manager)

        return managers

    @CachedProperty
    def managers_map(self):
        return {manager.name: manager for manager in self.managers}

    def get_connection_name(self):
        return self.meta.get('connection_name', DEFAULT_CONNECTION_NAME)

    def get_database_name(self):
        return self.meta.get('database_name', DEFAULT_DATABASE_NAME)

    def get_collection_name(self):
        return self.meta.get('collection_name', self.model.__name__.lower())