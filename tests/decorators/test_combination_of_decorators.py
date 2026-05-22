from abc import ABC, abstractmethod

import pytest

from pedantic import overrides, pedantic
from pedantic.decorators.validate.exceptions import ParameterException
from pedantic.decorators.validate.validate import Parameter, ReturnAs, validate
from pedantic.decorators.validate.validators import Min
from pedantic.exceptions import PedanticCallWithArgsException, PedanticException, PedanticTypeCheckException


def test_pedantic_overrides():
    class MyClass(ABC):
        @pedantic
        @abstractmethod
        def op(self, a: int) -> None:
            pass

    class Child(MyClass):
        a = 0

        @pedantic
        @overrides(MyClass)
        def op(self, a: int) -> None:
            self.a = a

    c = Child()
    c.op(a=42)


def test_pedantic_below_validate():
    @validate(
        Parameter(name='x', validators=[Min(0)]),
        return_as=ReturnAs.KWARGS_WITH_NONE,
    )
    @pedantic
    def some_calculation(x: int) -> int:
        return x

    some_calculation(x=42)
    some_calculation(42)

    with pytest.raises(expected_exception=ParameterException):
        some_calculation(x=-1)
    with pytest.raises(expected_exception=ParameterException):
        some_calculation(x=-42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_calculation(x=1.0)


def test_pedantic_above_validate():
    @pedantic
    @validate(
        Parameter(name='x', validators=[Min(0)]),
    )
    def some_calculation(x: int) -> int:
        return x

    some_calculation(x=42)

    with pytest.raises(expected_exception=ParameterException):
        some_calculation(x=-1)
    with pytest.raises(expected_exception=ParameterException):
        some_calculation(x=-42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_calculation(x=1.0)
    with pytest.raises(expected_exception=PedanticException):
        some_calculation(42)


def test_pedantic_above_validate_on_instance_method():
    class MyClass:
        @pedantic
        @validate(
            Parameter(name='x', validators=[Min(0)]),
        )
        def some_calculation(self, x: int) -> int:
            return x

    m = MyClass()
    m.some_calculation(x=42)
    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-1)
    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        m.some_calculation(x=1.0)
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        m.some_calculation(42)


def test_pedantic_below_validate_on_instance_method():
    class MyClass:
        @validate(
            Parameter(name='x', validators=[Min(0)]),
        )
        @pedantic
        def some_calculation(self, x: int) -> int:
            return x

    m = MyClass()
    m.some_calculation(x=42)
    m.some_calculation(42)

    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-1)
    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        m.some_calculation(x=1.0)


def test_pedantic_class_with_validate_instance_method():
    @pedantic
    class MyClass:
        @validate(
            Parameter(name='x', validators=[Min(0)]),
        )
        def some_calculation(self, x: int) -> int:
            return x

    m = MyClass()
    m.some_calculation(x=42)
    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-1)
    with pytest.raises(expected_exception=ParameterException):
        m.some_calculation(x=-42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        m.some_calculation(x=1.0)
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        m.some_calculation(42)


def test_pedantic_class_static_method_1():
    @pedantic
    class MyClass:
        @staticmethod
        def some_calculation(x: int) -> int:
            return x

    m = MyClass()
    m.some_calculation(x=42)
    MyClass.some_calculation(x=45)


def test_pedantic_static_method_1():
    class MyClass:
        @staticmethod
        @pedantic
        def some_calculation(x: int) -> int:
            return x

    m = MyClass()
    m.some_calculation(x=42)
    MyClass.some_calculation(x=45)
