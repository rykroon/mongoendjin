from datetime import datetime, date
from bson import ObjectId, Decimal128
from .errors import ValidationError


EMPTY_VALUES = (None, '', [], (), {})


class Undefined:
    pass


class Field:
    _zero_value = None

    def __init__(self, blank=False, choices=None, default=Undefined, null=False, unique=False):
        self.blank = blank
        self.choices = choices
        self.default = default
        self.null = null
        self.unique=False


    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        
    def __delete__(self, instance):
        instance.__dict__[self.name] = self.get_default()

    def __set_name__(self, owner, name):
        self.name = name

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls
        cls._meta.add_field(self)

        if not hasattr(cls, self.name):
            setattr(cls, self.name, self)

    def get_default(self):
        if self.default is not Undefined:
            if callable(self.default):
                return self.default()
            return self.default
        
        if self.null:
            return None

        if callable(self._zero_value):
            return self._zero_value()

        return self._zero_value

    def to_python(self, value):
        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        return value

    def validate(self, value):
        if self.choices is not None and value not in EMPTY_VALUES:
            if value not in self.choices:
                msg = "Value '{}' is not a valid choice.".format(value)
                raise ValidationError(msg)

        if value is None and not self.null:
            msg = "This field cannot be null."
            raise ValidationError(msg)

        if not self.blank and value in EMPTY_VALUES:
            msg = "This field cannot be blank."
            raise ValidationError(msg)


class BinaryField(Field):
    _zero_value = bytes

    def to_python(self, value):
        if isinstance(value, str):
            return value.encode()
        return value


class BooleanField(Field):
    _zero_value = bool

    def to_python(self, value):
        if self.null and value in EMPTY_VALUES:
            return None

        if value in (True, False):
            # 1/0 are equal to True/False. bool() converts former to latter.
            return bool(value)

        if value in ('t', 'True', '1'):
            return True

        if value in ('f', 'False', '0'):
            return False

        raise ValidationError("Invalid value.")


class DictField(Field):
    _zero_value = dict


class FloatField(Field):
    _zero_value = float

    def to_python(self, value):
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValidationError('Invalid value.')


class IntField(Field):
    _zero_value = int

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError('Invalid value.')


class ListField(Field):
    _zero_value = list


class StringField(Field):
    _zero_value = str

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)


class ObjectIdField(Field):

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, ObjectId):
            return value

        try:
            return ObjectId(value)
        except Exception:
            raise ValidationError('Invalid value.')


class DateField(Field):

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime(
                year=value.date, 
                month=value.month, 
                day=value.day
            )

        try:
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)

        except (TypeError, ValueError) as e:
            pass

        raise ValidationError('Invalid value.')

    