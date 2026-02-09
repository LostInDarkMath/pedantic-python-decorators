import asyncio
import warnings
from abc import abstractmethod

import pytest

from pedantic import overrides, timer, count_calls, trace, trace_if_returns, does_same_as_function, deprecated, \
    unimplemented, mock, require_kwargs
from pedantic.exceptions import NotImplementedException, PedanticOverrideException, PedanticCallWithArgsException


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
    class MyClassA:
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


def test_deprecated_1():
    @deprecated
    def old_method(i: int) -> str: return str(i)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        old_method(42)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)


def test_deprecated_2():
    def old_method(i: int) -> str:
        return str(i)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        old_method(42)
        assert not len(w) == 1


def test_unimplemented():
    @unimplemented
    def dirt(i: int) -> str:
        return str(i)

    with pytest.raises(expected_exception=NotImplementedException):
        dirt(42)


def test_timer():
    @timer
    def operation(i: int) -> str:
        return str(i)

    operation(42)


def test_count_calls():
    @count_calls
    def operation(i: int) -> str:
        return str(i)

    operation(42)


def test_trace():
    def some_method(x, y):
        return x + y

    traced_method = trace(some_method)
    assert some_method(42, 99) == traced_method(42, 99)


def test_trace_if_returns():
    def some_method(x, y):
        return x + y
    
    traced_method = trace_if_returns(100)(some_method)
    assert some_method(42, 99) == traced_method(42, 99)
    assert some_method(42, 58) == traced_method(42, 58)


def test_does_same_as_function():
    def some_method(x, y, z):
        return x * (y + z)

    @does_same_as_function(some_method)
    def other_method(x, y, z):
        return x * y + x * z

    other_method(1, 2, 3)
    other_method(4, 5, 6)


def test_does_same_as_function_wrong():
    def some_method(x, y, z):
        return x * (y + z)

    @does_same_as_function(some_method)
    def other_method(x, y, z):
        return x * y + z

    other_method(0, 2, 0)
    with pytest.raises(expected_exception=AssertionError):
        other_method(4, 5, 6)


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


@pytest.mark.asyncio
async def test_count_calls_async():
    @count_calls
    async def operation(i: int) -> str:
        await asyncio.sleep(0)
        return str(i)

    res = await operation(42)
    assert res == '42'


@pytest.mark.asyncio
async def test_trace_async():
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    traced_method = trace(some_method)
    assert await some_method(42, 99) == await traced_method(42, 99)


@pytest.mark.asyncio
async def test_trace_if_returns_async():
    async def some_method(x, y):
        await asyncio.sleep(0)
        return x + y

    traced_method = trace_if_returns(100)(some_method)
    assert await some_method(42, 99) == await traced_method(42, 99)
    assert await some_method(42, 58), await traced_method(42, 58)


@pytest.mark.asyncio
async def test_timer_async():
    @timer
    async def operation(i: int) -> str:
        await asyncio.sleep(0.05)
        return str(i)

    await operation(42)


@pytest.mark.asyncio
async def test_deprecated_async():
    @deprecated
    async def old_method(i: int) -> str:
        return str(i)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        await old_method(42)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)


@pytest.mark.asyncio
async def test_does_same_as_function_async():
    async def some_method(x, y, z):
        await asyncio.sleep(0)
        return x * (y + z)

    @does_same_as_function(some_method)
    async def other_method(x, y, z):
        await asyncio.sleep(0)
        return x * y + x * z

    await other_method(1, 2, 3)
    await other_method(4, 5, 6)


@pytest.mark.asyncio
async def test_does_same_as_function_async_and_sync():
    def some_method(x, y, z):
        return x * (y + z)

    @does_same_as_function(some_method)
    async def other_method(x, y, z):
        await asyncio.sleep(0)
        return x * y + x * z

    await other_method(1, 2, 3)
    await other_method(4, 5, 6)


@pytest.mark.asyncio
async def test_does_same_as_function_wrong():
    async def some_method(x, y, z):
        await asyncio.sleep(0)
        return x * (y + z)

    @does_same_as_function(some_method)
    async def other_method(x, y, z):
        await asyncio.sleep(0)
        return x * y + z

    await other_method(0, 2, 0)

    with pytest.raises(expected_exception=AssertionError):
        await other_method(4, 5, 6)


@pytest.mark.asyncio
async def test_mock_async():
    @mock(return_value=42)
    async def my_function(a, b, c): return a + b + c

    assert await my_function(1, 2, 3) == 42
    assert await my_function(100, 200, 300) == 42


@pytest.mark.asyncio
async def test_require_kwargs():
    @require_kwargs
    async def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    await calc(n=1, m=2, i=3)

    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        await calc(1, m=2, i=3)
