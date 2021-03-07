from .connections import client
from .fields import Field, ObjectIdField


class Document:

    _meta = {}

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
        for attr in dir(cls):
            if attr.startswith('__'):
                continue

            value = getattr(cls, attr, None)
            if not isinstance(value, Field):
                continue

            yield value

    @property
    def pk(self):
        return self._id

    def _get_collection(self):
        return client['test_db'][self._get_collection_name()]

    def _get_collection_name(self):
        collection_name = self._meta.get('collection_name')
        if collection_name is None:
            collection_name = self.__class__.__name__.tolower()
        return collection_name

    def to_dict(self):
        return {f.name: getattr(self, f.name) for f in self._get_fields()}

    def save(self, validate=True, clean=True):
        if clean:
            self.clean()
        
        if validate:
            self.validate()

        if self.pk:
            return self._update()
        
        return self._insert()

    def _insert(self):
        result = self._get_collection().insert_one(self.to_dict())
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
        pass
