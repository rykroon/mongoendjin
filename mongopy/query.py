
from mongopy.constants import LOOKUP_SEP
from mongopy.query_utils import Q


class QuerySet():
    
    def __init__(self, model=None, query=None, using=None):
        self.model = model
        self._db = using
        self._query = query or mongo.Query(self.model)

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

    def _chain(self):
        obj = self._clone()
        return obj

    def _clone(self):
        c = self.__class__(model=self.model, query=self._query.chain(), using=self._db)
        return c