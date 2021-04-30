from mongoendjin.db.utils import ConnectionHandler, ConnectionRouter


connections = None

router = ConnectionRouter()


def connect(settings):
    #create helper method for connecting
    global connections
    connections = ConnectionHandler(settings)

def get_connection(alias):
    return connections[alias]