import unittest
from typing import TypeVar, Generic, List, Type

from pedantic import GenericMixin

T = TypeVar('T')
U = TypeVar('U')


class TestGenericMixin(unittest.TestCase):
    def test_single_type_var(self):
        class Foo(Generic[T], GenericMixin):
            value: T

        foo = Foo[str]()
        assert foo.type_var == str
        assert foo.type_vars == {T: str}

        invalid = Foo()

        with self.assertRaises(expected_exception=AssertionError) as err:
            invalid.type_var

        assert f'You need to instantiate this class with type parameters! Example: Foo[int]()' in err.exception.args[0]

    def test_multiple_type_vars(self):
        class Foo(Generic[T, U], GenericMixin):
            value: T
            values: List[U]

        foo = Foo[str, int]()

        with self.assertRaises(expected_exception=AssertionError) as err:
           foo.type_var

        self.assertEqual(err.exception.args[0], 'You have multiple type parameters. '
                                                'Please use "type_vars" instead of "type_var".')

        assert foo.type_vars == {T: str, U: int}

        invalid = Foo()

        with self.assertRaises(expected_exception=AssertionError) as err:
            invalid.type_var

        assert f'You need to instantiate this class with type parameters! Example: Foo[int]()' in err.exception.args[0]

    def test_non_generic_class(self):
        class Foo(GenericMixin):
            value: int

        invalid = Foo()

        with self.assertRaises(expected_exception=AssertionError) as err:
            invalid.type_var

        self.assertEqual(err.exception.args[0], f'Foo is not a generic class. To make it generic, declare it like: '
                                                f'class Foo(Generic[T], GenericMixin):...')

    def test_call_type_var_in_constructor(self):
        class Foo(Generic[T], GenericMixin):
            def __init__(self) -> None:
                self.x = self.type_var()

        with self.assertRaises(expected_exception=AssertionError) as err:
            Foo[str]()

        assert 'make sure that you do not call this in the __init__() method' in err.exception.args[0]

    def test_subclass_set_type_variable(self):
        class Gen(Generic[T], GenericMixin):
            def __init__(self, value: T) -> None:
                self.value = value

            def get_type(self) -> dict[TypeVar, Type]:
                return self.type_vars

        class MyClass(Gen[int]):
            pass

        bar = Gen[int](value=4)
        assert bar.get_type() == {T: int}

        foo = MyClass(value=4)
        assert foo.get_type() == {T: int}