from typing import Callable, Any

# local file imports
from PythonHelpers.method_decorators import pedantic


def for_all_methods(decorator: Callable) -> Callable:
    """
    From: https://stackoverflow.com/questions/6307761/how-to-decorate-all-functions-of-a-class-without-typing-it-over-and-over-for-eac/6307868#6307868
    Example:
    >>> @for_all_methods(my_decorator)
    >>> class C(object):
    >>>     def m1(self): pass
    >>>     def m2(self, x): pass
    """
    def decorate(cls: Any):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def pedantic_class(cls: Any) -> Callable:
    """Shortcut for @for_all_methods(pedantic) """
    return for_all_methods(decorator=pedantic)(cls=cls)
