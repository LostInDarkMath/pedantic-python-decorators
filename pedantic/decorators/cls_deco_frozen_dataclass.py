from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Type, TypeVar, Any

from pedantic.type_checking_logic.check_types import assert_value_matches_type

T = TypeVar('T')


def frozen_dataclass(cls: Type[T]) -> Type[T]:
    """
        Makes the decorated class immutable by adding the [@dataclass(frozen=True)]
        decorator and add a useful [copy_with()] instance method to this class.

        In a nutshell, the followings methods will be added to the decorated class automatically:
        - __init__()
        - __eq__()
        - __hash__()
        - __repr__()
        - copy_with()
        - validate_types()

        Example:

        >>> @frozen_dataclass
        ... class Foo:
        ...     a: int
        ...     b: str
        ...     c: bool
        >>> foo = Foo(a=6, b='hi', c=True)
        >>> print(foo)
        Foo(a=6, b='hi', c=True)
        >>> print(foo.copy_with())
        Foo(a=6, b='hi', c=True)
        >>> print(foo.copy_with(a=42))
        Foo(a=42, b='hi', c=True)
        >>> print(foo.copy_with(b='Hello'))
        Foo(a=6, b='Hello', c=True)
        >>> print(foo.copy_with(c=False))
        Foo(a=6, b='hi', c=False)
        >>> print(foo.copy_with(a=676676, b='new', c=False))
        Foo(a=676676, b='new', c=False)
    """

    def copy_with(self, **kwargs: Any) -> T:
        """
            Creates a new immutable instance that by copying all fields of this instance replaced by the new values.
        """

        return cls(**{**asdict(self), **kwargs})  # python >= 3.9.0: cls(**(asdict(self) | kwargs))

    def validate_types(self) -> None:
        """
            Checks that all instance variable have the correct type.
            Raises an Exception if at least one type is incorrect.
        """

        props = fields(cls)

        for field in props:
            assert_value_matches_type(
                value=getattr(self, field.name),
                type_=field.type,
                err=f'In dataclass "{cls.__name__}" in field "{field.name}": ',
                type_vars={},
            )

    if is_dataclass(obj=cls):
        raise AssertionError(f'Dataclass "{cls}" cannot be decorated with '
                             f'"@frozen_dataclass" because it already is a dataclass.')

    setattr(cls, 'copy_with', copy_with)
    setattr(cls, 'validate_types', validate_types)
    return dataclass(frozen=True)(cls)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
