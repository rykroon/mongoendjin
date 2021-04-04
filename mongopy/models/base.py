import copy
import inspect

from .errors import ValidationError
from .fields import ObjectIdField
from .options import Options


def _has_contribute_to_class(value):
    # Only call contribute_to_class() if it's bound.
    return not inspect.isclass(value) and hasattr(value, 'contribute_to_class')


class ModelBase(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_attrs = {}
        attr_meta = attrs.pop('Meta', None)
        contributable_attrs = {}

        for obj_name, obj in attrs.items():
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj
        
        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        #abstract = getattr(attr_meta, 'abstract', False)
        meta = attr_meta or getattr(new_class, 'Meta', None)
        new_class.add_to_class('_meta', Options(meta))

        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)

        #field_names = {f.name for f in new_fields}

        for base in new_class.mro():
            if base not in parents or not hasattr(base, '_meta'):
                continue

            parent_fields = base._meta.local_fields
            for field in parent_fields:
                new_field = copy.deepcopy(field)
                new_class.add_to_class(field.name, new_field)

        return new_class

    def add_to_class(cls, name, value):
        if _has_contribute_to_class(value):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Model(metaclass=ModelBase):

    _id = ObjectIdField()

    def __init__(self, **kwargs):
        cls = self.__class__
        opts = cls._meta
        if opts.abstract:
            raise TypeError('Abstract models cannot be instantiated.')

        for field in opts.fields:
            try:
                val = kwargs.pop(field.name)
            except KeyError:
                val = field.get_default()

            setattr(self, field.name, val)

        for kwarg in kwargs:
            raise TypeError("%s() got an unexpected keyword argument '%s'" % (cls.__name__, kwarg))

        super().__init__()

    @classmethod
    def from_db(cls, db, field_names, values):
        #more logic goes here
        new = cls(*values)
        return new

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.pk)
    
    def __eq__(self, other):
        if not isinstance(other, Model):
            return NotImplemented

        if self.pk is None:
            return self is other

        return self.pk == other.pk

    def __hash__(self):
        if self.pk is None:
            raise TypeError("Model instances without primary key value are unhashable")
        return hash(self.pk)

    @property
    def pk(self):
        return self._id

    def to_dict(self, inc=None, exc=None):
        d = {}
        for f in self._meta.fields:
            if inc and f.name not in inc:
                continue
            if exc and f.name in exc:
                continue
            d[f.name] = getattr(self, f.name)
        return d

    def save(self):
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

    def clean_fields(self):
        errors = {}

        for f in self._meta.fields:
            value = getattr(self, f.name)
            try:
                setattr(self, f.name, f.clean(value))
            except ValidationError as e:
                errors[f.name] = str(e)

        if errors:
            raise ValidationError(errors)

    def full_clean(self):
        errors = {}

        try:
            self.clean_fields()
        except ValidationError as e:
            pass

        try:
            self.clean()
        except ValidationError as e:
            pass

        if errors:
            raise ValidationError(errors)

