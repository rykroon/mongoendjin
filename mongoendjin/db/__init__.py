from mongoendjin.db.utils import ConnectionHandler, ConnectionRouter


connections = ConnectionHandler()

router = ConnectionRouter()


def connect():
    #create helper method for connecting
    pass