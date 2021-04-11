from mongoendjin.models.utils import tree


class Q(tree.Node):

    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND
    conditional = True

    def __init__(self, *args, _connector=None, _negated=False, **kwargs):
        super().__init__(children=[*args, *sorted(kwargs.items())], connector=_connector, negated=_negated)
        
    def _combine(self, other, conn):
        if not(isinstance(other, Q) or getattr(other, 'conditional', False) is True):
            raise TypeError(other)

        # If the other Q() is empty, ignore it and just use `self`.
        if not other:
            args, kwargs = self.deconstruct()
            return type(self)(*args, **kwargs)
        # Or if this Q is empty, ignore it and just use `other`.
        elif not self:
            args, kwargs = other.deconstruct()
            return type(other)(*args, **kwargs)

        obj = type(self)()
        obj.connector = conn
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def deconstruct(self):
        args = tuple(self.children)
        kwargs = {}
        if self.connector != self.default:
            kwargs['_connector'] = self.connector
        if self.negated:
            kwargs['_negated'] = True
        return args, kwargs


class RegisterLookupMixin:

    def get_lookup(self, lookup_name):
        return self.__class__.get_lookups().get(lookup_name, None)

    @classmethod
    def get_lookups(cls):
        class_lookups = [parent.__dict__.get('class_lookups', {}) for parent in cls.mro()]
        merged = {}
        for d in reversed(class_lookups):
            merged.update(d)
        return merged

    @classmethod
    def register_lookup(cls, lookup, lookup_name=None):
        if lookup_name is None:
            lookup_name = lookup.lookup_name
        if 'class_lookups' not in cls.__dict__:
            cls.class_lookups = {}
        cls.class_lookups[lookup_name] = lookup
        return lookup
        

        