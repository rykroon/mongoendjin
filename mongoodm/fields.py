from datetime import datetime
import uuid
from bson import ObjectId, Decimal128
from.errors import ValidationError


class Field:

    _class = None
    _default = None

    def __init__(self, null=False, required=False, choices=None, \
            default=None):
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

        if callable(self._default):
            return self._default()

        return self._default

    def clean(self, value):
        if not isinstance(value, self._class):
            try:
                value = self._class(value)
            
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

        if not isinstance(value, self._class):
            raise ValidationError


class BinaryField(Field):
    _class = bytes
    _default = bytes


class BooleanField(Field):
    _class = bool
    _default = bool


class DictField(Field):
    _class = dict
    _default = dict


class FloatField(Field):
    _class = float
    _default = float


class IntField(Field):
    _class = int
    _default = int


class ListField(Field):
    _class = list
    _default = list


class StringField(Field):
    _class = str
    _default = str


class ObjectIdField(Field):
    _class = ObjectId
    _default = ObjectId


class DateField(Field):
    _class = datetime
    _default = datetime.utcnow

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


class UUIDField(Field):
    _class = uuid.UUID
    _default = uuid.uuid4

    