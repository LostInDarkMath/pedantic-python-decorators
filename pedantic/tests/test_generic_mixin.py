import unittest
from typing import TypeVar, Generic, List

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

        self.assertEqual(err.exception.args[0], f'You need to instantiate this class with type parameters! '
                                                f'Example: Foo[int]()')

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

        self.assertEqual(err.exception.args[0], f'You need to instantiate this class with type parameters! '
                                                f'Example: Foo[int]()')

    def test_non_generic_class(self):
        class Foo(GenericMixin):
            value: int

        invalid = Foo()

        with self.assertRaises(expected_exception=AssertionError) as err:
            invalid.type_var

        self.assertEqual(err.exception.args[0], f'Foo is not a generic class. To make it generic, declare it like: '
                                                f'class Foo(Generic[T], GenericMixin):...')

    def test_edge_case_orig_bases(self):
        class Foo(GenericMixin):
            __orig_bases__ = []

        invalid = Foo()

        with self.assertRaises(expected_exception=AssertionError) as err:
            invalid.type_var

        self.assertEqual(err.exception.args[0], f'Foo is not a generic class. To make it generic, declare it like: '
                                                f'class Foo(Generic[T], GenericMixin):...')
