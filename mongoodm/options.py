import inspect
from .fields import Field
from .utils import CachedProperty

class Options:

    def __init__(self):
        self.owner = None

    def __get__(self, instance, owner=None):
        self.owner = owner
        return self

    #@CachedProperty
    @property
    def fields(self):
        return self.get_fields()

    def get_fields(self):
        fields = {}
        for class_ in self.parents:
            for attr, value in vars(class_).items():
                if isinstance(value, Field):
                    if attr in fields:
                        continue
                    fields[attr] = value

        return list(fields.values())

    #@CachedProperty
    @property
    def meta(self):
        return self.get_meta()

    def get_meta(self):
        meta = getattr(self.owner, 'Meta', None)
        meta_dict = meta.__dict__
        for name in meta.__dict__:
            if name.startswith('_'):
                del meta_dict[name]
        return meta_dict

    #@CachedProperty
    @property
    def parents(self):
        return self.get_parents()

    def get_parents(self):
        return inspect.getmro(self.owner)

    def get_connection_name(self):
        return self.meta.get('connection_name', DEFAULT_CONNECTION_NAME)

    def get_database_name(self):
        return self.meta.get('database_name', DEFAULT_DATABASE_NAME)

    def get_collection_name(self):
        return self.meta.get('collection_name', self.owner.__name__.lower())