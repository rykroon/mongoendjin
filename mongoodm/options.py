import inspect
from .fields import Field
from .utils import CachedProperty

class Options:

    def __init__(self):
        self.owner = None

    def __get__(self, instance, owner=None):
        if self.owner is None:
            self.owner = owner
        return self

    @CachedProperty
    def fields(self):
        return self.get_fields()

    def get_fields(self):
        fields = {}
        classes = inspect.getmro(self.owner)
        for class_ in classes:
            for attr, value in vars(class_).items():
                if isinstance(value, Field):
                    if attr in fields:
                        continue
                    fields[attr] = value

        return list(fields.values())

    @CachedProperty
    def meta(self):
        return self.get_meta()

    def get_meta(self):
        meta = getattr(self.owner, 'Meta', None)
        meta_dict = meta.__dict__.copy()
        for name in meta.__dict__:
            if name.startswith('_'):
                del meta_dict[name]
        return meta_dict

    def get_connection_name(self):
        return self.meta.get('connection_name', DEFAULT_CONNECTION_NAME)

    def get_database_name(self):
        return self.meta.get('database_name', DEFAULT_DATABASE_NAME)

    def get_collection_name(self):
        return self.meta.get('collection_name', self.owner.__name__.lower())