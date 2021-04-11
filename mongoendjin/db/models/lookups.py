from datetime import datetime
from bson import ObjectId
from mongoendjin.db.models.fields import Field


class Lookup:
    lookup_name = None
    mongo_op = None

    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs

    def rhs_is_direct_value(self):
        return not hasattr(self.rhs, 'as_mongo')

    def process_rhs(self):
        value = self.rhs
        if self.rhs_is_direct_value():
            value = self.lhs.to_python(self.rhs)
        return {self.mongo_op: value}

    def as_mongo(self):
        return {self.lhs.name: self.process_rhs()}


@Field.register_lookup
class Exact(Lookup):
    lookup_name = 'exact'
    mongo_op = '$eq'
    

@Field.register_lookup
class GreaterThan(Lookup):
    lookup_name = 'gt'
    mongo_op = '$gt'


@Field.register_lookup
class GreaterThanOrEqual(Lookup):
    lookup_name = 'gte'
    mongo_op = '$gte'


@Field.register_lookup
class LessThan(Lookup):
    lookup_name = 'lt'
    mongo_op = '$lt'


@Field.register_lookup
class LessThanOrEqual(Lookup):
    lookup_name = 'lte'
    mongo_op = '$lte'


@Field.register_lookup
class In(Lookup):
    lookup_name = 'in'
    mongo_op = '$in'

    # will need to add logic to verify that the rhs
    # is an iterable


class PatternLookup(Lookup):
    mongo_op = '$regex'
    pattern = None
    options = ''

    def process_rhs(self):
        value = self.rhs
        if self.pattern:
            value = self.pattern % self.rhs
        return {self.mongo_op: value, '$options': self.options}


@Field.register_lookup
class Contains(PatternLookup):
    lookup_name = 'contains'


@Field.register_lookup
class IContains(Contains):
    lookup_name = 'icontains'
    options = 'i'


@Field.register_lookup
class StartsWith(PatternLookup):
    lookup_name = 'startswith'
    pattern = '^%s'


@Field.register_lookup
class IStartsWith(StartsWith):
    lookup_name = 'istartswith'
    options = 'i'


@Field.register_lookup
class EndsWith(PatternLookup):
    lookup_name = 'endswith'
    pattern = '%s$'


@Field.register_lookup
class IEndsWith(EndsWith):
    lookup_name = 'iendswith'
    options = 'i'


@Field.register_lookup
class Range(Lookup):
    lookup_name = 'range'
    
    def process_rhs(self):
        return {
            '$gt': self.rhs[0], 
            '$lt': self.rhs[1]
        }

@Field.register_lookup
class Type(Lookup):
    lookup_name = 'type'
    mongo_op = '$type'

    def process_rhs(self):
        value = self.rhs

        if value is None:
            value = 'null'

        if isinstance(value, type):
            value = {
                bool: 'bool',
                bytes: 'binData',
                datetime: 'date',
                dict: 'object',
                float: 'double',
                int: 'int',
                list: 'array',
                ObjectId: 'objectId',
                str: 'string',
                type(None): 'null'
            }[value]

        return {self.mongo_op: value}


class IsType(Type):
    type_name = None

    def process_rhs(self):
        if self.rhs:
            return {self.mongo_op: self.type_name}
        else:
            return {'$not': {self.mongo_op: self.type_name}}


@Field.register_lookup
class IsNull(IsType):
    lookup_name = 'isnull'
    type_name = 'null'


@Field.register_lookup
class Exists(Lookup):
    lookup_name = 'exists'
    mongo_op = '$exists'

    def process_rhs(self):
        return {self.mongo_op: bool(self.rhs)}

