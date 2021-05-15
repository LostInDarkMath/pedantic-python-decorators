import sys
import unittest
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Union, Dict

from pedantic.env_var_logic import disable_pedantic, enable_pedantic
from pedantic import overrides
from pedantic.decorators.class_decorators import pedantic_class
from pedantic.exceptions import PedanticOverrideException, PedanticTypeCheckException, \
    PedanticCallWithArgsException


class TestPedanticClass(unittest.TestCase):
    def tearDown(self) -> None:
        enable_pedantic()

    def test_constructor(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

        MyClass(a=42)

    def test_constructor_param_without_type_hint(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a) -> None:
                self.a = a

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass(a=42)

    def test_constructor_without_return_type(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int):
                self.a = a

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass(a=42)

    def test_constructor_wrong_return_type(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> int:
                self.a = a

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass(a=42)

    def test_constructor_must_be_called_with_kwargs(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            MyClass(42)

    def test_multiple_methods(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b: int) -> int:
                return self.a - b

            def print(self, s: str) -> None:
                print(f'{self.a} and {s}')

        m = MyClass(a=5)
        m.calc(b=42)
        m.print(s='Hi')
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            m.calc(45)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.calc(b=45.0)
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            m.print('Hi')

    def test_multiple_methods_with_missing_and_wrong_type_hints(self):
        @pedantic_class
        class MyClass:
            def __init__(self, a: int) -> None:
                self.a = a

            def calc(self, b: int) -> float:
                return self.a - b

            def dream(self, b) -> int:
                return self.a * b

            def print(self, s: str):
                print(f'{self.a} and {s}')

        m = MyClass(a=5)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.calc(b=42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.print(s='Hi')
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.dream(b=2)

    def test_type_annotation_string(self):
        @pedantic_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            @staticmethod
            def generator() -> 'MyClass':
                return MyClass(s='generated')

        MyClass.generator()

    def test_typo_in_type_annotation_string(self):
        @pedantic_class
        class MyClass:
            def __init__(self, s: str) -> None:
                self.s = s

            @staticmethod
            def generator() -> 'MyClas':
                return MyClass(s='generated')

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.generator()

    def test_overriding_contains(self):
        @pedantic_class
        class MyClass(list):
            def __contains__(self, item: int) -> bool:
                return True

        m = MyClass()
        print(42 in m)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            print('something' in m)

    def test_type_annotation_string_typo(self):
        @pedantic_class
        class MyClass:
            def compare(self, other: 'MyClas') -> bool:
                return self == other

            def fixed_compare(self, other: 'MyClass') -> bool:
                return self == other

        m = MyClass()
        m.fixed_compare(other=m)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.compare(other=m)

    def test_docstring_not_required(self):
        @pedantic_class
        class Foo:
            def __init__(self, a: int) -> None:
                self.a = a

            def bunk(self) -> int:
                '''
                Function with correct docstring. Yes, single-quoted docstrings are allowed too.
                Returns:
                    int: 42
                '''
                return self.a

        foo = Foo(a=10)
        foo.bunk()

    def test_overrides(self):
        @pedantic_class
        class Abstract:
            def func(self, b: str) -> str:
                pass

            def bunk(self) -> int:
                pass

        @pedantic_class
        class Foo(Abstract):
            def __init__(self, a: int) -> None:
                self.a = a

            @overrides(Abstract)
            def func(self, b: str) -> str:
                return b

            @overrides(Abstract)
            def bunk(self) -> int:
                return 42

        f = Foo(a=42)
        f.func(b='Hi')
        f.bunk()

    def test_overrides_abc(self):
        @pedantic_class
        class Abstract(ABC):
            @abstractmethod
            def func(self, b: str) -> str:
                pass

            @abstractmethod
            def bunk(self) -> int:
                pass

        @pedantic_class
        class Foo(Abstract):
            def __init__(self, a: int) -> None:
                self.a = a

            @overrides(Abstract)
            def func(self, b: str) -> str:
                return b

            @overrides(Abstract)
            def bunk(self) -> int:
                return 42

        f = Foo(a=42)
        f.func(b='Hi')
        f.bunk()

    def test_overrides_with_type_errors_and_call_by_args3(self):
        @pedantic_class
        class Abstract:
            def func(self, b: str) -> str:
                pass

            def bunk(self) -> int:
                pass

        @pedantic_class
        class Foo(Abstract):
            def __init__(self, a: int) -> None:
                self.a = a

            @overrides(Abstract)
            def func(self, b: str) -> str:
                return b

            @overrides(Abstract)
            def bunk(self) -> int:
                return self.a

        f = Foo(a=42)
        f.func(b='Hi')
        f.bunk()
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            f.func('Hi')
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo(a=3.1415)
        f.a = 3.145
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f.bunk()

    def test_overrides_goes_wrong(self):
        @pedantic_class
        class Parent:
            def func(self, b: str) -> str:
                return b + b + b

            def bunk(self) -> int:
                return 42

        with self.assertRaises(expected_exception=PedanticOverrideException):
            @pedantic_class
            class Foo(Parent):
                def __init__(self, a: int) -> None:
                    self.a = a

                @overrides(Parent)
                def funcy(self, b: str) -> str:
                    return b

                @overrides(Parent)
                def bunk(self) -> int:
                    return self.a

            f = Foo(a=40002)
            f.func(b='Hi')
            f.bunk()

        p = Parent()
        p.func(b='Hi')
        p.bunk()

    def test_static_method_with_sloppy_type_annotation(self):
        @pedantic_class
        class MyStaticClass:
            @staticmethod
            def double_func(a: int) -> int:
                x, y = MyStaticClass.static_bar()
                return x

            @staticmethod
            def static_bar() -> (int, int):  # this is wrong. Correct would be Tuple[int, int]
                return 0, 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            print(MyStaticClass.double_func(a=0))

    def test_property(self):
        @pedantic_class
        class MyClass(object):
            def __init__(self, some_arg: Any) -> None:
                self._some_attribute = some_arg

            @property
            def some_attribute(self) -> int:
                return self._some_attribute

            @some_attribute.setter
            def some_attribute(self, value: str) -> None:
                self._some_attribute = value

            def calc(self, value: float) -> float:
                return 2 * value

        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            MyClass(42)

        m = MyClass(some_arg=42)
        self.assertEqual(m.some_attribute, 42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_attribute = 100
        self.assertEqual(m.some_attribute, 42)
        m.some_attribute = '100'
        self.assertEqual(m._some_attribute, '100')
        m.calc(value=42.0)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            print(m.some_attribute)

    def test_property_getter_and_setter_misses_type_hints(self):
        @pedantic_class
        class MyClass(object):
            def __init__(self, some_arg: int) -> None:
                self._some_attribute = some_arg

            @property
            def some_attribute(self):
                return self._some_attribute

            @some_attribute.setter
            def some_attribute(self, value: int):
                self._some_attribute = value

            def calc(self, value: float) -> float:
                return 2 * value

        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            MyClass(42)

        m = MyClass(some_arg=42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.some_attribute = 100

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            print(m.some_attribute)
        m.calc(value=42.0)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.calc(value=42)

    def test_default_constructor(self):
        @pedantic_class
        class MyClass:
            def fun(self) -> int:
                return 42
        m = MyClass()
        m.fun()

    def test_optional_callable(self):
        @pedantic_class
        class SemanticSimilarity:
            def __init__(self, post_processing: bool = True, val: Optional[Callable[[float], float]] = None) -> None:
                if post_processing is None:
                    self.post_processing = val
                else:
                    self.post_processing = lambda x: x

        SemanticSimilarity()

    def test_optional_lambda(self):
        @pedantic_class
        class SemanticSimilarity:
            def __init__(self, val: Callable[[float], float] = lambda x: x) -> None:
                self.post_processing = val

        SemanticSimilarity()

    def test_class_method_type_annotation_missing(self):
        @pedantic_class
        class MyClass:
            @classmethod
            def do(cls):
                print('i did something')

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.do()

    def test_class_method_type_annotation(self):
        @pedantic_class
        class MyClass:
            @classmethod
            def do(cls) -> None:
                print('i did something')

            @classmethod
            def calc(cls, x: Union[int, float]) -> int:
                return x * x

        MyClass.do()
        MyClass.calc(x=5)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.calc(5)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.calc(x=5.1)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            MyClass.calc('hi')

    def test_dataclass_inside(self):
        """Pedantic cannot be used on dataclasses."""

        if sys.version_info < (3, 7):
            return

        from dataclasses import dataclass

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            @pedantic_class
            @dataclass
            class MyClass:
                name: str
                unit_price: float
                quantity_on_hand: int = 0

    def test_dataclass_outside(self):
        """Pedantic cannot check the constructor of dataclasses"""

        if sys.version_info < (3, 7):
            return

        from dataclasses import dataclass

        @dataclass
        @pedantic_class
        class MyClass:
            name: str
            unit_price: float
            quantity_on_hand: int = 0

            def total_cost(self) -> int:
                return self.unit_price * self.quantity_on_hand

        MyClass(name='name', unit_price=5.1)
        a = MyClass(name='name', unit_price=5.0, quantity_on_hand=42)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            a.total_cost()

    def test_class_decorator_static_class_method(self):
        @pedantic_class
        class Foo:
            @staticmethod
            def staticmethod() -> int:
                return 'foo'

            @classmethod
            def classmethod(cls) -> int:
                return 'foo'

            def method(self) -> int:
                return 'foo'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.staticmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo.classmethod()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            Foo().method()

    def test_pedantic_class_disable_pedantic(self):
        disable_pedantic()

        @pedantic_class
        class MyClass:
            def __init__(self, pw, **kwargs):
                self._validate_str_len(new_values=kwargs)

            @staticmethod
            def _validate_str_len(new_values: Dict[str, Any]) -> None:
                return 42

            def method(pw, **kwargs):
                MyClass._validate_str_len(new_values=kwargs)

        MyClass._validate_str_len(None)
        MyClass._validate_str_len(new_values={1: 1, 2: 2})
        MyClass(name='hi', age=12, pw='123')

    def test_disable_pedantic_2(self):
        """ https://github.com/LostInDarkMath/pedantic-python-decorators/issues/37 """

        disable_pedantic()

        @pedantic_class
        class Foo:
            def __init__(self) -> None:
                self._value = 42

            def do(self) -> None:
                print(self.bar(value=self._value))

            @staticmethod
            def bar(value: int) -> int:
                return value + 75

        f = Foo()
        f.do()
