from mongopy import connections
from mongopy.models.nosql.datastructures import Empty


"""
    This is where the codebase will deviate the most from Django.
    In Django the Query class is used to genereate an SQL query.
    For Mongopy, this class will be used to generate a pymongo cursor.
"""


class Query:

    def __init__(self, model):
        self.model = model

        self.default_ordering = True
        self.standard_ordering = True

        self.order_by = ()
        self.low_mark, self.high_mark = 0, None

        self.deferred_loading = (frozenset(), True)

    ### Mongo Specific methods ###

    def get_db(self, using):
        return connections[using]

    def get_collection(self, using):
        db = self.get_db(using)
        return db[self.get_meta().collection_name]

    def get_cursor(self):
        #plays the same role as 'get_compiler()'
        pass


    ### From Django ###

    def get_meta(self):
        return self.model._meta

    def clone(self):
        obj = Empty()
        obj.__class__ = self.__class__
        obj.__dict__ = self.__dict__.copy()
        return obj

    def chain(self, klass=None):
        obj = self.clone()
        if klass and obj.__class__ != klass:
            obj.__class__ = klass
        return obj

    def get_count(self, using):
        obj = self.clone()
        return obj.get_collection(using).count_documents(self.filter)

    def add_q(self, q_object):
        pass

    def set_empty(self):
        pass

    def is_empty(self):
        pass

    def set_limits(self, low=None, high=None):
        if high is not None:
            if self.high_mark is not None:
                self.high_mark = min(self.high_mark, self.low_mark + high)
            else:
                self.high_mark = self.low_mark + high

        if low is not None:
            if self.highmark is not None:
                self.low_mark = min(self.high_mark, self.low_mark + low)
            else:
                self.low_mark = self.low_mark + low

        if self.low_mark == self.high_mark:
            self.set_empty()

    def clear_limits(self):
        self.low_mark, self.high_mark = 0, None

    def add_ordering(self, *ordering):
        for item in ordering:
            if item.startswith('-'):
                item = item[1:]
            
            self.get_meta().get_field(item)

        if ordering:
            self.order_by += ordering
        else:
            self.default_ordering = False

    def clear_ordering(self, force_empty):
        self.order_by = ()
        if force_empty:
            self.default_ordering = False

    def clear_deferred_loading(self):
        self.deferred_loading = (frozenset(), True)

    def add_deferred_loading(self, field_names):
        existing, defer = self.deferred_loading
        if defer:
            self.deferred_loading = existing.union(field_names), True
        else:
            self.deferred_loading = existing.difference(field_names), False

    def add_immediate_loading(self, field_names):
        existing, defer = self.deferred_loading
        field_names = set(field_names)
        if 'pk' in field_names:
            field_names.remove('pk')
            field_names.add(self.get_meta().pk.name)

        if defer:
            self.deferred_loading = field_names.difference(existing), False
        else:
            self.deferred_loading = frozenset(field_names), False

