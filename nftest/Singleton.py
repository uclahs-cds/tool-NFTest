#pylint: disable=C0103
#pylint: disable=E1003
#pylint: disable=W0613
#pylint: disable=C0204
""" Module containg Singleton metaclass """

class Singleton(type):
    """ Singleton metaclass """
    def __new__(metacls, cls, bases, members):
        _new_type = type(cls, bases, members)
        _instance = None
        def __new__(cls, *args, **kwargs):
            nonlocal _instance
            if _instance is None:
                _instance = super(_new_type, cls).__new__(cls)
                child_init = _instance.__init__
                def __init__(cls, *args, **kwargs):
                    child_init(*args, **kwargs)
                    cls._block_change = True

                def __setattr__(self, name, value):
                    if hasattr(self, '_block_change') and self._block_change:
                        return
                    object.__setattr__(self, name, value)

                def __delattr__(self, name):
                    if hasattr(self, '_block_change') and self._block_change:
                        return
                    object.__delattr__(self, name)

                _new_type.__init__ = __init__
                _new_type.__setattr__ = __setattr__
                _new_type.__delattr__ = __delattr__
            return _instance

        _new_type.__new__ = __new__
        return _new_type
