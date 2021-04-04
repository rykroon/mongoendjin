from mongopy.nosql.datastructures import Empty


"""
    This is where the codebase will deviate the most from Django.
    In Django the Query class is used to genereate an SQL query.
    For Mongopy, this class will be used to generate a pymongo cursor.
"""



class Query:

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

    def get_count(self):
        obj = self.clone()


    def add_q(self, q_object):
        pass

    def as_mongo(self):
        pass