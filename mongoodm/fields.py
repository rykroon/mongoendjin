from datetime import datetime, date
from bson import ObjectId, Decimal128
from .errors import ValidationError


class Field:

    _python_type = None
    _zero_value = None

    def __init__(self, choices=None, default=None, null=False, required=False, unique=False):
        self.choices = choices
        self.default = default
        self.null = null
        self.required = required
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

    def get_default(self):
        if self.default:
            if callable(self.default):
                return self.default()
            return self.default
        
        if self.null:
            return None

        if callable(self._zero_value):
            return self._zero_value()

        return self._zero_value

    def to_python(self, value):
        if isinstance(value, self._python_type) or value is None:
            return value

        try:
            return self._python_type(value)

        except (TypeError, ValueError):
            raise ValidationError

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        return value

    def validate(self, value):
        if not value and self.required:
            msg = "Field '{}' is required.".format(self.name)
            raise ValidationError(msg)

        if value is None and not self.null:
            msg = "Field '{}' cannot be None.".format(self.name)
            raise ValidationError(msg)

        if self.choices and value is not None:
            if value not in self.choices:
                msg = "Invalid choice for field '{}'.".format(self.name)
                raise ValidationError(msg)


class BinaryField(Field):
    _python_type = bytes
    _zero_value = bytes


class BooleanField(Field):
    _python_type = bool
    _zero_value = bool

    def to_python(self, value):
        if value in ('t', 'true', '1', 1):
            return True

        if value in ('f', 'false', '0', 0):
            return False

        return super().to_python(value)


class DictField(Field):
    _python_type = dict
    _zero_value = dict


class FloatField(Field):
    _python_type = float
    _zero_value = float


class IntField(Field):
    _python_type = int
    _zero_value = int


class ListField(Field):
    _python_type = list
    _zero_value = list


class StringField(Field):
    _python_type = str
    _zero_value = str


class ObjectIdField(Field):
    _python_type = ObjectId


class DateField(Field):
    _python_type = datetime

    def to_python(self, value):
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

        return super().to_python(value)

    