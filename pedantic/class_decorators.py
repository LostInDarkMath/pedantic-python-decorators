from typing import Callable, Any, Optional
import types

from pedantic.method_decorators import pedantic, pedantic_require_docstring, trace, timer


def for_all_methods(decorator: Callable[..., Any]) -> Callable[..., Any]:
    """
    Example:
    >>> @for_all_methods(pedantic)
    ... class C(object):
    ...     def m1(self): pass
    ...     def m2(self, x): pass
    """
    def decorate(cls: Any) -> Any:
        type_vars = {}

        for attr in cls.__dict__:
            attr_value = getattr(cls, attr)

            if isinstance(attr_value, types.FunctionType):  # if callable(attr_value):  # does not work with Python 3.6
                if decorator in [pedantic, pedantic_require_docstring]:
                    setattr(cls, attr, decorator(attr_value, is_class_decorator=True, type_vars=type_vars))
                else:
                    try:
                        setattr(cls, attr, decorator(attr_value, is_class_decorator=True))
                    except TypeError:
                        setattr(cls, attr, decorator(attr_value))
            elif isinstance(attr_value, property):
                prop = attr_value
                wrapped_getter = _get_wrapped(prop=prop.fget, decorator=decorator)
                wrapped_setter = _get_wrapped(prop=prop.fset, decorator=decorator)
                wrapped_deleter = _get_wrapped(prop=prop.fdel, decorator=decorator)
                new_prop = property(fget=wrapped_getter, fset=wrapped_setter, fdel=wrapped_deleter)
                setattr(cls, attr, new_prop)
        return cls
    return decorate


def pedantic_class(cls: Any) -> Callable[..., Any]:
    """Shortcut for @for_all_methods(pedantic) """
    return for_all_methods(decorator=pedantic)(cls=cls)


def pedantic_class_require_docstring(cls: Any) -> Callable[..., Any]:
    """Shortcut for @for_all_methods(pedantic_require_docstring) """
    return for_all_methods(decorator=pedantic_require_docstring)(cls=cls)


def trace_class(cls: Any) -> Callable[..., Any]:
    """Shortcut for @for_all_methods(trace) """
    return for_all_methods(decorator=trace)(cls=cls)


def timer_class(cls: Any) -> Callable[..., Any]:
    """Shortcut for @for_all_methods(timer) """
    return for_all_methods(decorator=timer)(cls=cls)


def _get_wrapped(prop: Optional[Callable[..., Any]], decorator: Callable[..., Any]) -> Optional[Callable[..., Any]]:
    return decorator(prop) if prop is not None else None
