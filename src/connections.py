from pymongo import MongoClient

client = None

def connect(**kwargs):
    global client
    client = MongoClient(**kwargs)
    return client()