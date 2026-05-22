import inspect
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from pedantic.constants import TYPE_VAR_ATTR_NAME, TYPE_VAR_METHOD_NAME, TYPE_VAR_SELF
from pedantic.type_checking_logic.check_generic_classes import (
    check_instance_of_generic_class_and_get_type_vars,
    is_instance_of_generic_class,
)

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T', bound=type)


def decorate_class(
    cls: T,
    decorate_callable: Callable[[Callable, ...], Callable],
    *args: Any,
    allowed_dunder_methods: list[str] | None = None,
) -> T:
    """Applies a decorator with optional arguments to each method of a class."""

    if allowed_dunder_methods is None:
        allowed_dunder_methods = []

    for attr_name, attr_value in vars(cls).items():
        if attr_name.startswith('__') and attr_name.endswith('__') and attr_name not in allowed_dunder_methods:
            continue

        if inspect.isfunction(attr_value) or inspect.ismethod(attr_value):
            setattr(cls, attr_name, decorate_callable(attr_value, *args))
        elif isinstance(attr_value, staticmethod):
            wrapped = decorate_callable(attr_value.__func__, *args)
            setattr(cls, attr_name, staticmethod(wrapped))
        elif isinstance(attr_value, classmethod):
            wrapped = decorate_callable(attr_value.__func__, *args)
            setattr(cls, attr_name, classmethod(wrapped))
        elif isinstance(attr_value, property):
            fget = decorate_callable(attr_value.fget, *args) if attr_value.fget is not None else None
            fset = decorate_callable(attr_value.fset, *args) if attr_value.fset is not None else None
            fdel = decorate_callable(attr_value.fdel, *args) if attr_value.fdel is not None else None

            setattr(
                cls,
                attr_name,
                property(
                    fget=fget,
                    fset=fset,
                    fdel=fdel,
                    doc=attr_value.__doc__,
                ),
            )

    return cls


def add_type_var_attr_and_method_to_class(cls: type) -> None:
    """Adds a special attribute that stores resolved type vars to the given class."""

    def type_vars(self: Any) -> dict:
        t_vars = {TYPE_VAR_SELF: cls}

        if is_instance_of_generic_class(instance=self):
            type_vars_fifo = getattr(self, TYPE_VAR_ATTR_NAME, {})
            type_vars_generics = check_instance_of_generic_class_and_get_type_vars(instance=self)
            setattr(self, TYPE_VAR_ATTR_NAME, {**type_vars_fifo, **type_vars_generics, **t_vars})
        else:
            setattr(self, TYPE_VAR_ATTR_NAME, t_vars)

        return getattr(self, TYPE_VAR_ATTR_NAME)

    setattr(cls, TYPE_VAR_METHOD_NAME, type_vars)
