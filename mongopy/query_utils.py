

LOOKUP_SEP = '__'

EQ = '$eq'
GT = '$gt'
GTE = '$gte'
IN = '$in'
LT = '$lt'
LTE = '$lte'
NE = '$ne'
NIN = '$nin'

AND = '$and'
NOT = '$not'
OR = '$or'
NOR = '$nor'

EXISTS = '$exists'
TYPE = '$type'


COMPARISON_OPERATORS = [
    'eq',
    'gt',
    'gte',
    'in',
    'lt',
    'lte',
    'ne',
    'nin'
]


LOGICAL_OPERATORS = [
    'and',
    'not',
    'nor',
    'or'
]

ELEMENT_OPERATORS = [
    'exists',
    'type'
]


"""
    Notes
    - using the models' _meta.get_field() method, verify that the first named part is 
        a valid field. Then make sure that lookup is valid.
"""


class Q(dict):

    AND = '$and'
    OR = '$or'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for k, v in self.copy().items():
            if k.startswith('$'):
                continue

            try:
                key, op = k.split('__', 1)
                if op not in COMPARISON_OPERATORS:
                    raise ValueError
                op = '${}'.format(op)

            except ValueError:
                key, op = k, '$eq'

            del self[k]
            self[key] = Q({op: v})
        
    def _combine(self, other, cond):
        if not isinstance(other, Q):
            raise TypeError(other)

        obj = Q({
            cond: [self, other]
        })

        return obj

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __invert__(self):
        obj = Q()
        for field, expr in self.items():
            #this will definitely need some work
            if isinstance(expr, Q):
                obj[field] = {'$not': expr}
            else:
                obj[field] = {'$ne': expr}
        return obj


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
        

        