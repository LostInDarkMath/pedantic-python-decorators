import unittest
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

from pedantic.decorators.cls_deco_frozen_dataclass import frozen_dataclass, frozen_type_safe_dataclass
from pedantic.exceptions import PedanticTypeCheckException


@frozen_dataclass
class Foo:
    a: int
    b: str
    c: bool


@frozen_type_safe_dataclass
class B:
    v: Set[int]


@frozen_type_safe_dataclass
class A:
    foo: List[int]
    bar: Dict[str, str]
    values: Tuple[B, B]

class TestFrozenDataclass(unittest.TestCase):
    def test_equals_and_hash(self):
        a = Foo(a=6, b='hi', c=True)
        b = Foo(a=6, b='hi', c=True)
        c = Foo(a=7, b='hi', c=True)

        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

        self.assertNotEqual(a, c)
        self.assertNotEqual(hash(a), hash(c))

    def test_copy_with(self):
        foo = Foo(a=6, b='hi', c=True)

        copy_1 = foo.copy_with()
        self.assertEqual(foo, copy_1)

        copy_2 = foo.copy_with(a=42)
        self.assertNotEqual(foo, copy_2)
        self.assertEqual(42, copy_2.a)
        self.assertEqual(foo.b, copy_2.b)
        self.assertEqual(foo.c, copy_2.c)

        copy_3 = foo.copy_with(b='Hello')
        self.assertNotEqual(foo, copy_3)
        self.assertEqual(foo.a, copy_3.a)
        self.assertEqual('Hello', copy_3.b)
        self.assertEqual(foo.c, copy_3.c)

        copy_4 = foo.copy_with(c=False)
        self.assertNotEqual(foo, copy_4)
        self.assertEqual(foo.a, copy_4.a)
        self.assertEqual(foo.b, copy_4.b)
        self.assertEqual(False, copy_4.c)

        copy_5 = foo.copy_with(a=676676, b='new', c=False)
        self.assertNotEqual(foo, copy_5)
        self.assertEqual(676676, copy_5.a)
        self.assertEqual('new', copy_5.b)
        self.assertEqual(False, copy_5.c)

    def test_validate_types(self):
        foo = Foo(a=6, b='hi', c=True)
        foo.validate_types()

        bar = Foo(a=6.6, b='hi', c=True)

        with self.assertRaises(expected_exception=PedanticTypeCheckException) as exc:
            bar.validate_types()

        expected = 'In dataclass "Foo" in field "a": Type hint is incorrect: Argument 6.6 of type <class \'float\'> ' \
                   'does not match expected type <class \'int\'>.'
        self.assertEqual(str(exc.exception), expected)

    def test_decorate_dataclass(self):
        with self.assertRaises(expected_exception=AssertionError) as exc:
            @frozen_dataclass
            @dataclass
            class A:
                foo: int

        self.assertIn(
            'cannot be decorated with "@frozen_dataclass" because it already is a dataclass',
            str(exc.exception)
        )

    def test_frozen_typesafe_dataclass_with_post_init(self):
        b = 3

        @frozen_dataclass(type_safe=True)
        class A:
            foo: int

            def __post_init__(self) -> None:
                nonlocal b
                b = 33

        with self.assertRaises(expected_exception=PedanticTypeCheckException) as exc:
            A(foo=42.7)

        self.assertEqual(
            'In dataclass "A" in field "foo": Type hint is incorrect: Argument 42.7 of type'
            ' <class \'float\'> does not match expected type <class \'int\'>.',
            str(exc.exception)
        )

        # we check that the __post_init__ method is executed
        self.assertEqual(33, b)

    def test_frozen_typesafe_dataclass_without_post_init(self):
        @frozen_dataclass(type_safe=True)
        class A:
            foo: int

        with self.assertRaises(expected_exception=PedanticTypeCheckException) as exc:
            A(foo=42.7)

        self.assertEqual(
            'In dataclass "A" in field "foo": Type hint is incorrect: Argument 42.7 of type'
            ' <class \'float\'> does not match expected type <class \'int\'>.',
            str(exc.exception)
        )

    def test_frozen_dataclass_with_empty_braces(self):
        @frozen_dataclass()
        class A:
            foo: int

        a = A(foo=42)
        self.assertEqual(42, a.foo)

    def test_frozen_dataclass_order(self):
        @frozen_dataclass(order=True)
        class A:
            foo: int
            bar: int

        a = A(foo=42, bar=43)
        b = A(foo=42, bar=42)
        c = A(foo=41, bar=44)
        d = A(foo=44, bar=0)
        self.assertLess(b, a)
        self.assertLess(c, b)
        self.assertLess(a, d)

    def test_frozen_type_safe_dataclass_copy_with_check(self):
        @frozen_type_safe_dataclass
        class A:
            foo: int
            bar: bool

        a = A(foo=42, bar=False)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            a.copy_with(foo=1.1)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            a.copy_with(bar=11)

        a.copy_with(foo=11, bar=True)

    def test_copy_with_is_shallow(self):
        a = A(foo=[1, 2], bar={'hello': 'world'}, values=(B(v={4, 5}), B(v={6})))
        shallow = a.copy_with()

        # manipulation
        shallow.bar['hello'] = 'pedantic'
        shallow.foo.append(3)

        self.assertEqual([1, 2, 3], a.foo)
        self.assertEqual([1, 2, 3], shallow.foo)
        self.assertEqual('pedantic', a.bar['hello'])
        self.assertEqual('pedantic', shallow.bar['hello'])

    def test_copy_with_and_deep_copy_with(self):
        a = A(foo=[1, 2], bar={'hello': 'world'}, values=(B(v={4, 5}), B(v={6})))
        deep = a.deep_copy_with()

        # manipulation
        deep.bar['hello'] = 'pedantic'
        deep.foo.append(3)

        self.assertEqual([1, 2], a.foo)
        self.assertEqual([1, 2, 3], deep.foo)
        self.assertEqual('world', a.bar['hello'])
        self.assertEqual('pedantic', deep.bar['hello'])
