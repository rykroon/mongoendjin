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

    def __init__(self):
        self.model = None

    def contribute_to_class(self, cls):
        cls._meta = self
        self.model = cls

        meta_class = getattr(self.model, 'Meta', None)

        if meta_class:
            meta_attrs = meta_class.__dict__.copy()
            for name in meta_class.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]

                for attr_name in DEFAULT_NAMES:
                    if attr_name in meta_attrs:
                        setattr(self, attr_name, meta_attrs.pop(attr_name))

            if meta_attrs:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs))

    def get_field(self, field_name):
        try:
            return self.fields_map[field_name]
        except KeyError:
            raise FieldDoesNotExist

    @CachedProperty
    def fields(self):
        return list(self.fields_map.values())

    @CachedProperty
    def fields_map(self):
        fields = {}
        for class_ in self.model.mro():
            for attr, value in vars(class_).items():
                if isinstance(value, Field):
                    if attr in fields:
                        continue
                    fields[attr] = value
        return fields

    def get_connection_name(self):
        return self.meta.get('connection_name', DEFAULT_CONNECTION_NAME)

    def get_database_name(self):
        return self.meta.get('database_name', DEFAULT_DATABASE_NAME)

    def get_collection_name(self):
        return self.meta.get('collection_name', self.model.__name__.lower())