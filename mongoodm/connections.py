from pymongo import MongoClient

client = None
db_name = None


def connect(db_name, **kwargs):
    global client
    global db
    db = db
    client = MongoClient(**kwargs)
    return client


def get_db():
    global client
    global db_name
    return client[db_name]