from pymongo import MongoClient


DEFAULT_CONNECTION_NAME = 'default'
DEFAULT_DATABASE_NAME = 'test'


connections = {}


def connect(alias=DEFAULT_CONNECTION_NAME, **kwargs):
    conn = MongoClient(**kwargs)
    connections[alias] = conn
    return client


def get_connection(alias):
    return connections[alias]