import copy
from .errors import FieldDoesNotExist
from mongoendjin.utils.functional import cached_property
from mongoendjin.utils.text import camel_case_to_spaces


DEFAULT_NAMES = (
    'abstract',
    'collection_name',
    #'database_name',
    'indexes',
    'verbose_name',
    'verbose_name_plural',
)


class Options:

    def __init__(self, meta):
        self.meta = meta
        self.abstract = False
        self.collection_name = ''
        self.indexes = []
        self.local_fields = []
        self.local_managers = []
        self.model_name = None
        self.object_name = None
        self.pk = None
        self.verbose_name = None
        self.verbose_name_plural = None

    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.model = cls

        self.object_name = cls.__name__
        self.model_name = self.object_name.lower()
        self.verbose_name = camel_case_to_spaces(self.object_name)

        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                if name.startswith('_'):
                    del meta_attrs[name]

            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))

            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs))

        if self.verbose_name_plural is None:
            self.verbose_name_plural = '{}s'.format(self.verbose_name)

        del self.meta

        if not self.collection_name:
            self.collection_name = self.model_name

    def _prepare(self, model):
        pass

    def add_manager(self, manager):
        self.local_managers.append(manager)
        #expire cache
        if 'managers' in self.__dict__:
            delattr(self, 'managers')

    def add_field(self, field):
        self.local_fields.append(field)

    def get_field(self, field_name):
        try:
            return self.fields_map[field_name]
        except KeyError:
            raise FieldDoesNotExist

    @cached_property
    def fields(self):
        return list(self.fields_map.values())

    @cached_property
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

    @cached_property
    def fields_map(self):
        return {field.name: field for field in self.fields}

    @cached_property
    def managers(self):
        print('managers')
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

    @cached_property
    def managers_map(self):
        return {manager.name: manager for manager in self.managers}
