


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
        return {self.lhs: self.process_rhs()}


class Exact(Lookup):
    lookup_name = 'exact'
    mongo_op = '$eq'
    

class GreaterThan(Lookup):
    lookup_name = 'gt'
    mongo_op = '$gt'


class GreaterThanOrEqual(Lookup):
    lookup_name = 'gte'
    mongo_op = '$gte'


class LessThan(Lookup):
    lookup_name = 'lt'
    mongo_op = '$lt'


class LessThanOrEqual(Lookup):
    lookup_name = 'lte'
    mongo_op = '$lte'


class In(Lookup):
    lookup_name = 'in'
    mongo_op = '$in'


class PatternLookup(Lookup):
    mongo_op = '$regex'
    pattern = None
    options = ''

    def process_rhs(self):
        value = self.rhs
        if self.pattern:
            value = self.pattern % self.rhs
        return {self.mongo_op: value, '$options', self.options}


class Contains(PatternLookup):
    lookup_name = 'contains'


class IContains(Contains):
    lookup_name = 'icontains'
    options = 'i'


class StartsWith(PatternLookup):
    lookup_name = 'startswith'
    pattern = '^%s'


class IStarsWith(StartsWith):
    lookup_name = 'istartswith'
    options = 'i'


class EndsWith(PatternLookup):
    lookup_name = 'endswith'
    pattern = '%s$'


class IEndsWith(EndsWith):
    lookup_name = 'iendswith'
    options = 'i'


class IsNull(Lookup):
    Lookup_name = 'isnull'
    mongo_op = '$type'

    def process_rhs(self):
        if self.rhs:
            return {self.mongo_op: 'null'}
        else:
            return {'$not': {self.mongo_op: 'null'}}

