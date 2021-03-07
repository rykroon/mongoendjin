from .connections import client

class Document:

    _meta = {}

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)

        for field in cls._get_fields():
            instance.__dict__[field.name] = field.get_default()

        return instance

    @classmethod
    def _get_fields(cls):
        return [v for k, v in cls.__dict__.items() if isinstance(v, Field)]

    @property
    def pk(self):
        pass

    def _get_collection(self):
        pass

    def save(self):
        pass

    def delete(self):
        pass

    def clean(self):
        pass

    def validate(self):
        pass