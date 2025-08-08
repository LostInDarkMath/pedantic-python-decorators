from abc import ABC
from enum import StrEnum
from typing import TypeVar, Callable, Generic

from pedantic.mixins.generic_mixin import GenericMixin


class DecoratorType(StrEnum):
    """
    The interface that defines all possible decorators types.

    The values of this enum are used as property names and the properties are added to the decorated functions.
    So I would recommend naming them with a leading underscore to keep them private and also write it lowercase.

    Example:
        >>> class Decorators(DecoratorType):
        ...     FOO = '_foo'
    """


DecoratorTypeVar = TypeVar('DecoratorTypeVar', bound=DecoratorType)
T = TypeVar('T')
C = TypeVar('C', bound=Callable)


def create_decorator(
    decorator_type: DecoratorType,
    transformation: Callable[[C, DecoratorType, T], C] = None,
) -> Callable[[T], Callable[[C], C]]:
    """
    Creates a new decorator that is parametrized with one argument of an arbitrary type.
    You can also pass an arbitrary [transformation] to add custom behavior to the decorator.
    """

    def decorator(value: T) -> Callable[[C], C]:
        def fun(f: C) -> C:
            setattr(f, decorator_type, value)

            if transformation is None:
                return f

            return transformation(f, decorator_type, value)

        return fun  # we do not need functools.wraps, because we return the original function here

    return decorator


class WithDecoratedMethods(ABC, Generic[DecoratorTypeVar], GenericMixin):
    """
    A mixin that is used to figure out which method is decorated with custom parameterized decorators.
    Example:
        >>> class Decorators(DecoratorType):
        ...     FOO = '_foo'
        ...     BAR = '_bar'
        >>> foo = create_decorator(decorator_type=Decorators.FOO)
        >>> bar = create_decorator(decorator_type=Decorators.BAR)
        >>> class MyClass(WithDecoratedMethods[Decorators]):
        ...    @foo(42)
        ...    def m1(self) -> None:
        ...        print('bar')
        ...
        ...    @foo(value=43)
        ...    def m2(self) -> None:
        ...        print('bar')
        ...
        ...    @bar(value=44)
        ...    def m3(self) -> None:
        ...        print('bar')
        >>> instance = MyClass()
        >>> instance.get_decorated_functions()
        {
            <Decorators.FOO: '_foo'>: {
                <bound method MyClass.m1 of <__main__.MyClass object at 0x7fea7a6e2610>>: 42,
                <bound method MyClass.m2 of <__main__.MyClass object at 0x7fea7a6e2610>>: 43,
            },
            <Decorators.BAR: '_bar'>: {
                <bound method MyClass.m3 of <__main__.MyClass object at 0x7fea7a6e2610>>: 44,
            }
        }
    """

    def get_decorated_functions(self) -> dict[DecoratorTypeVar, dict[C, T]]:
        decorator_types = self.type_vars[DecoratorTypeVar]
        decorated_functions = {t: dict() for t in decorator_types}  # type: ignore

        for attribute_name in dir(self):
            if attribute_name.startswith('__') or attribute_name in ['type_var', 'type_vars']:
                continue

            attribute = getattr(self, attribute_name)

            for decorator_type in decorator_types:  # type: ignore
                if hasattr(attribute, decorator_type):
                    decorated_functions[decorator_type][attribute] = getattr(attribute, decorator_type)

        return decorated_functions
