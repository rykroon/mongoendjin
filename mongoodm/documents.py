from .connections import get_connection, DEFAULT_CONNECTION_NAME, \
    DEFAULT_DATABASE_NAME
from .fields import Field, ObjectIdField
from .errors import ValidationError


class Document:

    _meta = {
        'connection_name': DEFAULT_CONNECTION_NAME,
        'database_name': DEFAULT_DATABASE_NAME,
        'collection_name': None
    }

    _id = ObjectIdField()

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        for f in cls._get_fields():
            instance.__dict__[f.name] = kwargs.get(f.name, f.get_default())

        return instance

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.pk is None or other.pk is None:
            return False

        return self.pk == other.pk

    def __repr__(self):
        return '{}(pk={})'.format(self.__class__.__name__, self.pk)

    @classmethod
    def _get_fields(cls):
        if not hasattr(cls, '_fields'):
            cls._fields = []
            for attr in dir(cls):
                if attr.startswith('__'):
                    continue

                value = getattr(cls, attr, None)
                if not isinstance(value, Field):
                    continue

                cls._fields.append(value)
        return cls._fields

    def _get_connection(self):
        alias = self._meta.get('connection_name')
        return get_connection(alias)

    def _get_db(self):
        db_name = self._meta.get('database_name')
        return self._get_connection()[db_name]

    def _get_collection(self):
        collection_name = self._get_collection_name()
        return self._get_db()[collection_name]

    def _get_collection_name(self):
        collection_name = self._meta.get('collection_name')
        if collection_name is None:
            collection_name = self.__class__.__name__.lower()
        return collection_name

    @property
    def pk(self):
        return self._id

    def to_dict(self, inc=None, exc=None):
        d = {}
        for f in self._get_fields():
            if inc and f.name not in inc:
                continue
            if exc and f.name in exc:
                continue
            d[f.name] = getattr(self, f.name)
        return d

    def save(self, validate=True, clean=True):
        if clean:
            self.clean()
        
        if validate:
            self.validate(clean=clean)

        if self.pk:
            return self._update()
        
        return self._insert()

    def _insert(self):
        result = self._get_collection().insert_one(self.to_dict(exc=['_id']))
        self._id = result.inserted_id

    def _update(self):
        result = self._get_collection().update_one(
            filter={
                '_id': self._id
            },
            update={
                '$set': self.to_dict()
            }
        )

    def delete(self):
        pass

    def clean(self):
        pass

    def validate(self, clean=True):
        errors = {}
        if clean:
            self.clean()

        for f in self._get_fields():
            value = getattr(self, f.name)
            if clean:
                setattr(self, f.name, f.clean(value))

            try:
                f.validate(value)
            except ValidationError as e:
                errors[f.name] = str(e)

        if errors:
            raise ValidationError(errors)