import sys
from copy import deepcopy
from dataclasses import dataclass, fields
from typing import Type, TypeVar, Any, Union, Callable, Dict

from pedantic.get_context import get_context
from pedantic.type_checking_logic.check_types import assert_value_matches_type

T = TypeVar('T')


def frozen_type_safe_dataclass(cls: Type[T]) -> Type[T]:
    """ Shortcut for @frozen_dataclass(type_safe=True) """

    return frozen_dataclass(type_safe=True)(cls)


def frozen_dataclass(
        cls: Type[T] = None,
        type_safe: bool = False,
        order: bool = False,
) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
        Makes the decorated class immutable and a dataclass by adding the [@dataclass(frozen=True)]
        decorator. Also adds useful copy_with() and validate_types() instance methods to this class (see below).

        If [type_safe] is True, a type check is performed for each field after the __post_init__ method was called
        which itself s directly called after the __init__ constructor.
        Note this have a negative impact on the performance. It's recommend to use this for debugging and testing only.

        In a nutshell, the followings methods will be added to the decorated class automatically:
        - __init__() gives you a simple constructor like "Foo(a=6, b='hi', c=True)"
        - __eq__() lets you compare objects easily with "a == b"
        - __hash__() is also needed for instance comparison
        - __repr__() gives you a nice output when you call "print(foo)"
        - copy_with() allows you to quickly create new similar frozen instances. Use this instead of setters.
        - deep_copy_with() allows you to create deep copies and modify them.
        - validate_types() allows you to validate the types of the dataclass.
                           This is called automatically when [type_safe] is True.

        If the [order] parameter is True (default is False), the following comparison methods
        will be added additionally:
        - __lt__() lets you compare instance like "a < b"
        - __le__() lets you compare instance like "a <= b"
        - __gt__() lets you compare instance like "a > b"
        - __ge__() lets you compare instance like "a >= b"

        These compare the class as if it were a tuple of its fields, in order.
        Both instances in the comparison must be of the identical type.

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

    def decorator(cls_: Type[T]) -> Type[T]:
        def copy_with(self, **kwargs: Any) -> T:
            """
                Creates a new immutable instance that by copying all fields of this instance replaced by the new values.
                Keep in mind that this is a shallow copy!
            """

            current_values = {field.name: getattr(self, field.name) for field in fields(self)}
            return cls_(**{**current_values, **kwargs})

        def deep_copy_with(self, **kwargs: Any) -> T:
            """
                Creates a new immutable instance that by deep copying all fields of
                this instance replaced by the new values.
            """

            current_values = {field.name: deepcopy(getattr(self, field.name)) for field in fields(self)}
            return cls_(**{**current_values, **kwargs})

        def validate_types(self, *, _context: Dict[str, Type] = None) -> None:
            """
                Checks that all instance variable have the correct type.
                Raises a [PedanticTypeCheckException] if at least one type is incorrect.
            """

            props = fields(cls_)

            if _context is None:
                # method was called by user
                _context = get_context(depth=2)

            for field in props:
                assert_value_matches_type(
                    value=getattr(self, field.name),
                    type_=field.type,
                    err=f'In dataclass "{cls_.__name__}" in field "{field.name}": ',
                    type_vars={},
                    context=_context,
                )

        methods_to_add = [copy_with, deep_copy_with, validate_types]

        for method in methods_to_add:
            setattr(cls_, method.__name__, method)

        if type_safe:
            old_post_init = getattr(cls_, '__post_init__', lambda _: None)

            def new_post_init(self) -> None:
                old_post_init(self)
                context = get_context(depth=3, increase_depth_if_name_matches=[
                    copy_with.__name__,
                    deep_copy_with.__name__,
                ])
                self.validate_types(_context=context)

            setattr(cls_, '__post_init__', new_post_init)

        args = {'frozen': True, 'order': order}

        if sys.version_info >= (3, 10):
            args['kw_only'] = True

        return dataclass(**args)(cls_)

    if cls is None:
        return decorator

    return decorator(cls_=cls)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
