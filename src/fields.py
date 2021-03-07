from datetime import datetime
from bson import ObjectId, Decimal128
from.errors import ValidationError


class Field:

    python_type = None
    zero_value = None

    def __init__(self, null=False, required=False, choices=None, default=None):
        self.null = null
        self.required = required
        self.choices = choices
        self.default = default

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        
    def __del__(self, instance):
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

        if callable(self.zero_value):
            return self.zero_value()

        return self.zero_value

    def clean(self, value):
        if not isinstance(value, self.python_type):
            try:
                value = self.python_type(value)
            
            except Exception:
                pass

        return value

    def validate(self, value):
        if not value and self.required:
            raise ValidationError

        if value is None and not self.null:
            raise ValidationError

        if self.choices and value is not None:
            if value not in self.choices:
                raise ValidationError

        if not isinstance(value, self.python_type):
            raise ValidationError


class BinaryField(Field):
    python_type = bytes
    zero_value = bytes


class BooleanField(Field):
    python_type = bool
    zero_value = bool


class DictField(Field):
    python_type = dict
    zero_value = dict


class FloatField(Field):
    python_type = float
    zero_value = float


class IntField(Field):
    python_type = int
    zero_value = int


class ListField(Field):
    python_type = list
    zero_value = list


class StringField(Field):
    python_type = str
    zero_value = str


class ObjectIdField(Field):
    python_type = ObjectId


class DateField(Field):
    python_type = datetime

    def clean(self, value):
        value = super().clean(value)
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                pass
        
        if isinstance(value, (int, float)):
            try:
                value = datetime.fromtimestamp(value)
            except Exception:
                pass

        return value
    