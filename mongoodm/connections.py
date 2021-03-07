from pymongo import MongoClient


DEFAULT_CLIENT_NAME = 'default'
DEFAULT_DB_NAME = 'test'


clients = {}


def connect(client_name=DEFAULT_CLIENT_NAME, **kwargs):
    client = MongoClient(**kwargs)
    clients[client_name] = client
    return client


def get_client(client_name):
    return clients[client_name]