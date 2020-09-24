from typing import Callable, Any, Optional, Dict
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
        for attr in cls.__dict__:
            attr_value = getattr(cls, attr)

            if isinstance(attr_value, types.FunctionType):  # if callable(attr_value):  # does not work with Python 3.6
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

        _add_method_to_class(cls=cls, name='get_type_vars')
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


def _add_method_to_class(cls: Any, name: str) -> None:
    attr_name_type_vars = '__pedantic_type_vars__'

    def type_vars(self) -> Dict:
        if not hasattr(self, attr_name_type_vars):
            setattr(self, attr_name_type_vars, dict())
        return getattr(self, attr_name_type_vars)
    setattr(cls, name, type_vars)
