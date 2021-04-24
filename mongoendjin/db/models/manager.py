

class BaseManager:
    def __init__(self):
        super().__init__()
        self.model = None
        self.name = None
        self._db = None

    def contribute_to_class(self, cls, name):
        self.name = self.name or name
        self.model = cls

        setattr(cls, name, ManagerDescriptor(self))

        cls._meta.add_manager(self)


class Manager(BaseManager):
    pass


class ManagerDescriptor:
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, owner=None):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via %s instances" % owner.__name__)

        return owner._meta.managers_map[self.manager.name]