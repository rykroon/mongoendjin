

Undefined = object()


class CachedProperty:

    def __init__(self, func):
        self.func = func
        self.name = '_{}'.format(func.__name__)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        value = getattr(instance, self.name, Undefined)
        if value is Undefined:
            value = self.func(instance)
            setattr(instance, self.name, value)
        return value


def process_key(k, v):
    if '__' not in k:
        return {k: v}
    
    k1, k2 = k.rsplit('__', 1)
    k2 = '$' + k2
    return process_key(k1, {k2: v})
