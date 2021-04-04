"""
    This is where the codebase will deviate the most from Django.
    In Django the Query class is used to genereate an SQL query.
    For Mongopy, this class will be used to generate a pymongo cursor.
"""



class Query:


    def add_q(self, q_object):
        pass

    def as_mongo(self):
        pass