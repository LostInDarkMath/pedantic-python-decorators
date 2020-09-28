from typing import Callable, Any, Optional, Dict
import types

from pedantic.constants import TYPE_VAR_ATTR_NAME, TYPE_VAR_METHOD_NAME, F, C
from pedantic.check_generic_classes import _check_instance_of_generic_class_and_get_typ_vars, \
    _is_instance_of_generic_class
from pedantic.method_decorators import pedantic, pedantic_require_docstring, trace, timer


def for_all_methods(decorator: F) -> Callable[[C], C]:
    """
    Example:
    >>> @for_all_methods(pedantic)
    ... class MyClass(object):
    ...     def m1(self): pass
    ...     def m2(self, x): pass
    """
    def decorate(cls: C) -> C:
        for attr in cls.__dict__:
            attr_value = getattr(cls, attr)

            if isinstance(attr_value, types.FunctionType):
                setattr(cls, attr, decorator(attr_value))
            elif isinstance(attr_value, property):
                prop = attr_value
                wrapped_getter = _get_wrapped(prop=prop.fget, decorator=decorator)
                wrapped_setter = _get_wrapped(prop=prop.fset, decorator=decorator)
                wrapped_deleter = _get_wrapped(prop=prop.fdel, decorator=decorator)
                new_prop = property(fget=wrapped_getter, fset=wrapped_setter, fdel=wrapped_deleter)
                setattr(cls, attr, new_prop)

        _add_type_var_attr_and_method_to_class(cls=cls)
        return cls
    return decorate


def pedantic_class(cls: C) -> C:
    """ Shortcut for @for_all_methods(pedantic) """
    return for_all_methods(decorator=pedantic)(cls=cls)


def pedantic_class_require_docstring(cls: C) -> C:
    """ Shortcut for @for_all_methods(pedantic_require_docstring) """
    return for_all_methods(decorator=pedantic_require_docstring)(cls=cls)


def trace_class(cls: C) -> C:
    """ Shortcut for @for_all_methods(trace) """
    return for_all_methods(decorator=trace)(cls=cls)


def timer_class(cls: C) -> C:
    """ Shortcut for @for_all_methods(timer) """
    return for_all_methods(decorator=timer)(cls=cls)


def _get_wrapped(prop: Optional[F], decorator: F) -> Optional[F]:
    return decorator(prop) if prop is not None else None


def _add_type_var_attr_and_method_to_class(cls: C) -> None:
    def type_vars(self) -> Dict:
        if _is_instance_of_generic_class(instance=self):
            type_vars_fifo = getattr(self, TYPE_VAR_ATTR_NAME) if hasattr(self, TYPE_VAR_ATTR_NAME) else {}
            type_vars_generics = _check_instance_of_generic_class_and_get_typ_vars(instance=self)
            setattr(self, TYPE_VAR_ATTR_NAME, _merge_dicts(first=type_vars_generics, second=type_vars_fifo))
        else:
            setattr(self, TYPE_VAR_ATTR_NAME, dict())
        return getattr(self, TYPE_VAR_ATTR_NAME)
    setattr(cls, TYPE_VAR_METHOD_NAME, type_vars)


def _merge_dicts(first: Dict[Any, Any], second: Dict[Any, Any]) -> Dict[Any, Any]:
    for key in second:
        if key not in first:
            first[key] = second[key]
    return first
