import asyncio
from abc import abstractmethod, ABC

import pytest

from pedantic import overrides
from pedantic.exceptions import PedanticOverrideException


def test_overrides_parent_has_no_such_method():
    class MyClassA:
        pass

    with pytest.raises(expected_exception=PedanticOverrideException):
        class MyClassB(MyClassA):
            @overrides(MyClassA)
            def operation(self): pass


def test_overrides_all_good():
    class MyClassA:
        def operation(self): pass

    class MyClassB(MyClassA):
        @overrides(MyClassA)
        def operation(self):
            return 42

    b = MyClassB()
    b.operation()


def test_overrides_static_method():
    class MyClassA:
        @staticmethod
        def operation(): pass

    class MyClassB(MyClassA):
        @staticmethod
        @overrides(MyClassA)
        def operation():
            return 42

    b = MyClassB()
    assert b.operation() ==  42
    assert MyClassB.operation() == 42


def test_overrides_below_property():
    class MyClassA(ABC):
        @property
        @abstractmethod
        def operation(self): pass

    class MyClassB(MyClassA):
        @property
        @overrides(MyClassA)   # Note: it does not work the other way around
        def operation(self):
            return 43

    b = MyClassB()
    assert b.operation == 43


def test_overrides_function():
    class MyClassA:
        pass

    with pytest.raises(expected_exception=PedanticOverrideException):
        @overrides(MyClassA)
        def operation(): return 42


@pytest.mark.asyncio
async def test_overrides_async_instance_method() -> None:
    class MyClassA:
        async def operation(self): pass

    class MyClassB(MyClassA):
        @overrides(MyClassA)
        async def operation(self):
            await asyncio.sleep(0)
            return 42

    b = MyClassB()
    await b.operation()


@pytest.mark.asyncio
async def test_overrides_parent_has_no_such_method_async():
    class MyClassA:
        pass

    with pytest.raises(expected_exception=PedanticOverrideException):
        class MyClassB(MyClassA):
            @overrides(MyClassA)
            async def operation(self): return 42
