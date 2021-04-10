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

    def get_db(self, using):
        return connections[using]

    def get_collection(self, using):
        db = self.get_db(using)
        return db[self.get_meta().collection_name]


    ###

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

    def as_mongo(self):
        pass