
from mongopy.constants import LOOKUP_SEP
from mongopy.query_utils import Q


class BaseIterable:
    def __init__(self, queryset):
        self.queryset = queryset


class ModelIterable(BaseIterable):
    pass


class ValuesIterable(BaseIterable):
    pass



class QuerySet():
    
    def __init__(self, model=None, query=None, using=None):
        self.model = model
        self._db = using
        self._query = query or mongo.Query(self.model)
        self._result_cache = None
        self._iterable_class = ModelIterable

    @property
    def query(self):
        return self._query

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __bool__(self):
        self._fetch_all()
        return bool(self._result_cache)

    def __getitem__(self, k):
        if not isinstance(k, (int, slice)):
            raise TypeError

        #check negative indexing

        if self._result_cache is not None:
            return self._result_cache[k]

        #additional logic goes here

    
    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################

    def count(self):
        if self._result_cache is not None:
            return len(self._result_cache)

        return self.query.get_count()

    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        num = len(clone)
        if num == 1:
            return clone._result_cache[0]
        
        if not num:
            raise Exception('DoesNotExist')

        raise Exception('MultipleObjectsReturned')

    def create(self, **kwargs):
        pass

    def first(self):
        pass

    def last(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def exists(self):
        pass


    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def all(self):
        return self._chain()

    def filter(self, *args, **kwargs):
        return self._filter_or_exclude(False, args, kwargs)

    def exclude(self, *args, **kwargs):
        return self._filter_or_exclude(True, args, kwargs)

    def _filter_or_exclude(self, negate, args, kwargs):
        clone = self._chain()
        clone._filter_or_exclude_inplace(negate, args, kwargs)
        return clone

    def _filter_or_exclude_inplace(self, negate, args, kwargs):
        if negate:
            self._query.add_q(~Q(*args, **kwargs))
        else:
            self._query.add_q(Q(*args, **kwargs))

    def order_by(self, *field_names):
        pass

    def defer(self, *fields):
        pass

    def only(self, *fields):
        pass

    ###################
    # PRIVATE METHODS #
    ###################

    def _chain(self):
        obj = self._clone()
        return obj

    def _clone(self):
        c = self.__class__(model=self.model, query=self.query.chain(), using=self._db)
        c._iterable_class = self._iterable_class
        c._fields = self._fields
        return c

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))