
from mongopy.models.constants import LOOKUP_SEP
from mongopy.models.query_utils import Q


class BaseIterable:
    def __init__(self, queryset):
        self.queryset = queryset


class ModelIterable(BaseIterable):
    
    def __iter__(self):
        pass


class ValuesIterable(BaseIterable):
    
    def __iter__(self):
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

        if isinstance(k, slice):
            if k.start is not None:
                assert k.start >= 0, "Negative indexing is not supported."

            if k.stop is not None:
                assert k.stop >= 0, "Negative indexing is not supported."

        else:
            assert k >= 0, "Negative indexing is not supported."

        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._chain()
            start = int(k.start) if k.start is not None else None
            stop = int(k.stop) if k.stop is not None else None
            qs.query.set_limits(start, stop)
            return list(qs)[::k.step] if k.step else qs

        qs = self._chain()
        qs.query.set_limits(k, k + 1)
        qs._fetch_all()
        return qs._result_cache[0]

    
    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################

    def count(self):
        if self._result_cache is not None:
            return len(self._result_cache)

        return self.query.get_count(using=self.db)

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
        if self.query.is_sliced:
            raise TypeError('Cannot reorder a query once a slice has been taken.')

        obj = self._chain()
        obj.query.clear_ordering(force_empty=False)
        obj.query.add_ordering(*field_names)
        return obj

    def reverse(self):
        if self.query.is_sliced:
            raise TypeError('Cannot reverse a query once a slice has been taken.')
        clone = self._chain()
        clone.query.standard_ordering = not clone.query.standard_ordering
        return clone

    def defer(self, *fields):
        if self._fields is not None:
            raise TypeError("Cannot call defer() after .values() or .values_list()")

        clone = self._chain()
        if fields == (None,):
            self.query.clear_deferred_loading()
        else:
            self.query.add_deferred_loading(fields)

        return clone

    def only(self, *fields):
        if self._fields is not None:
            raise TypeError("Cannot call only() after .values() or .values_list()")

        if fields == (None,):
            raise TypeError("Cannot pass None as an argument to only().")

        clone = self._chain()
        clone.query.add_immediate_loading(field)
        return clone

    ###################################
    # PUBLIC INTROSPECTION ATTRIBUTES #
    ###################################

    @property
    def db(self):
        return self._db

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