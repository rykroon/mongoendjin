import inspect

from .connections import get_connection, DEFAULT_CONNECTION_NAME, \
    DEFAULT_DATABASE_NAME
from .errors import ValidationError
from .fields import Field, ObjectIdField
from .options import Options


class DocumentMetaClass(type):
    def __new__(cls, name, base, dct):
        # each Document CLASS instance should have it's own _meta property
        cls._meta = Options()



class BaseDocument:

    _meta = Options()

    class Meta:
        abstract = False
        connection_name = DEFAULT_CONNECTION_NAME,
        database_name = DEFAULT_DATABASE_NAME,
        collection_name = None
        indexes = None


    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        for f in cls._meta.fields:
            instance.__dict__[f.name] = kwargs.get(f.name, f.get_default())

        return instance

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.pk is None:
            return self is other

        return self.pk == other.pk

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.pk)

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are unhashable")
        return hash(self.pk)


class Document(BaseDocument):
    _id = ObjectIdField()

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