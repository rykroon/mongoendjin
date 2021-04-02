
from mongopy.query_utils import Q, LOOKUP_SEP


class QuerySet():
    
    def __init__(self, model=None, cursor=None, using=None):
        self.model = model
        self._db = using
        self.cursor = cursor

    def all(self):
        return self._chain()

    def filter(self, *args, **kwargs):
        pass

    def exclude(self, *args, **kwargs):
        pass

    def _filter_or_exclude(self, negate, args, kwargs):
        for arg in args:
            if not isinstance(arg, Q):
                raise TypeError

        for k, v in kwargs.items():
            lookup = k.split(LOOKUP_SEP)
            field_name = lookup[0]
            field = self.model._meta.get_field(field_name)
            if len(lookup) == 1:  
                operator = '$eq'

            elif len(lookup) == 2:
                operator = '${}'.format(lookup[1])

            else:
                raise ValueError


    def _chain(self):
        obj = self._clone()
        return obj

    def _clone(self):
        c = self.__class__(model=self.model, cursor=self.cursor.clone(), using=self._db)
        return c