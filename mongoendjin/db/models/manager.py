import inspect
from mongoendjin.db.models.query import QuerySet

class BaseManager:

    auto_created = False

    def __init__(self):
        super().__init__()
        self.model = None
        self.name = None
        self._db = None

    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        def create_method(name, method):
            def manager_method(self, *args, **kwargs):
                return getattr(self.get_queryset(), name)(*args, **kwargs)
            manager_method.__name__ = method.__name__
            manager_method.__doc__ = method.__doc__
            return manager_method

        new_methods = {}
        for name, method in inspect.getmembers(queryset_class, predicate=inspect.isfunction):
            # Only copy missing methods.
            if hasattr(cls, name):
                continue
            # Only copy public methods or methods with the attribute `queryset_only=False`.
            queryset_only = getattr(method, 'queryset_only', None)
            if queryset_only or (queryset_only is None and name.startswith('_')):
                continue
            # Copy the method onto the manager.
            new_methods[name] = create_method(name, method)
        return new_methods

    @classmethod
    def from_queryset(cls, queryset_class, class_name=None):
        if class_name is None:
            class_name = '%sFrom%s' % (cls.__name__, queryset_class.__name__)

        return type(class_name, (cls,), {
            '_queryset_class': queryset_class,
            **cls._get_queryset_methods(queryset_class),
        })

    def contribute_to_class(self, cls, name):
        self.name = self.name or name
        self.model = cls

        setattr(cls, name, ManagerDescriptor(self))

        cls._meta.add_manager(self)

    def get_queryset(self):
        return self._queryset_class(model=self.model, using=self._db)

    def all(self):
        return self.get_queryset()


class Manager(BaseManager.from_queryset(QuerySet)):
    pass


class ManagerDescriptor:
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, owner=None):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via %s instances" % owner.__name__)

        return owner._meta.managers_map[self.manager.name]