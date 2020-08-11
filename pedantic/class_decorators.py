from typing import Callable, Any

# local file imports
from pedantic.method_decorators import pedantic, pedantic_require_docstring, trace, timer


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


def pedantic_class_require_docstring(cls: Any) -> Callable:
    """Shortcut for @for_all_methods(pedantic_require_docstring) """
    return for_all_methods(decorator=pedantic_require_docstring)(cls=cls)


def trace_class(cls: Any) -> Callable:
    """Shortcut for @for_all_methods(trace) """
    return for_all_methods(decorator=trace)(cls=cls)


def timer_class(cls: Any) -> Callable:
    """Shortcut for @for_all_methods(timer) """
    return for_all_methods(decorator=timer)(cls=cls)
