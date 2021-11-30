import asyncio
import sys
import unittest
import warnings

from pedantic.exceptions import NotImplementedException, PedanticOverrideException, PedanticCallWithArgsException
from pedantic import overrides, timer, count_calls, trace, trace_if_returns, does_same_as_function, deprecated, \
    unimplemented, mock, require_kwargs


class TestSmallDecoratorMethods(unittest.TestCase):
    def test_overrides_parent_has_no_such_method(self):
        class MyClassA:
            pass

        with self.assertRaises(expected_exception=PedanticOverrideException):
            class MyClassB(MyClassA):
                @overrides(MyClassA)
                def operation(self):
                    return 42

    def test_overrides_all_good(self):
        class MyClassA:
            def operation(self):
                pass

        class MyClassB(MyClassA):
            @overrides(MyClassA)
            def operation(self):
                return 42

        b = MyClassB()
        b.operation()

    def test_overrides_static_method(self):
        class MyClassA:
            @staticmethod
            def operation():
                pass

        class MyClassB(MyClassA):
            @staticmethod
            @overrides(MyClassA)
            def operation():
                return 42

        b = MyClassB()
        self.assertEqual(b.operation(), 42)
        self.assertEqual(MyClassB.operation(), 42)

    def test_overrides_function(self):
        class MyClassA:
            pass

        with self.assertRaises(expected_exception=PedanticOverrideException):
            @overrides(MyClassA)
            def operation():
                return 42

    def test_deprecated_1(self):
        @deprecated
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "deprecated" in str(w[-1].message)

    def test_deprecated_2(self):
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert not len(w) == 1

    def test_unimplemented(self):
        @unimplemented
        def dirt(i: int) -> str:
            return str(i)

        with self.assertRaises(expected_exception=NotImplementedException):
            dirt(42)

    def test_timer(self):
        @timer
        def operation(i: int) -> str:
            return str(i)

        operation(42)

    def test_count_calls(self):
        @count_calls
        def operation(i: int) -> str:
            return str(i)

        operation(42)

    def test_trace(self):
        def some_method(x, y):
            return x + y

        traced_method = trace(some_method)
        self.assertEqual(some_method(42, 99), traced_method(42, 99))

    def test_trace_if_returns(self):
        def some_method(x, y):
            return x + y
        traced_method = trace_if_returns(100)(some_method)
        self.assertEqual(some_method(42, 99), traced_method(42, 99))
        self.assertEqual(some_method(42, 58), traced_method(42, 58))

    def test_does_same_as_function(self):
        def some_method(x, y, z):
            return x * (y + z)

        @does_same_as_function(some_method)
        def other_method(x, y, z):
            return x * y + x * z

        other_method(1, 2, 3)
        other_method(4, 5, 6)

    def test_does_same_as_function_wrong(self):
        def some_method(x, y, z):
            return x * (y + z)

        @does_same_as_function(some_method)
        def other_method(x, y, z):
            return x * y + z

        other_method(0, 2, 0)
        with self.assertRaises(expected_exception=AssertionError):
            other_method(4, 5, 6)


if sys.version_info >= (3, 8):
    # IsolatedAsyncioTestCase exists since Python 3.8
    from unittest import IsolatedAsyncioTestCase

    class AsyncSmallDecoratorTests(IsolatedAsyncioTestCase):
        async def test_overrides_async_instance_method(self) -> None:
            class MyClassA:
                async def operation(self):
                    pass

            class MyClassB(MyClassA):
                @overrides(MyClassA)
                async def operation(self):
                    await asyncio.sleep(0)
                    return 42

            b = MyClassB()
            await b.operation()

        async def test_overrides_parent_has_no_such_method_async(self):
            class MyClassA:
                pass

            with self.assertRaises(expected_exception=PedanticOverrideException):
                class MyClassB(MyClassA):
                    @overrides(MyClassA)
                    async def operation(self):
                        return 42

        async def test_count_calls_async(self):
            @count_calls
            async def operation(i: int) -> str:
                await asyncio.sleep(0)
                return str(i)

            res = await operation(42)
            self.assertEqual('42', res)

        async def test_trace_async(self):
            async def some_method(x, y):
                await asyncio.sleep(0)
                return x + y

            traced_method = trace(some_method)
            self.assertEqual(await some_method(42, 99), await traced_method(42, 99))

        async def test_trace_if_returns_async(self):
            async def some_method(x, y):
                await asyncio.sleep(0)
                return x + y

            traced_method = trace_if_returns(100)(some_method)
            self.assertEqual(await some_method(42, 99), await traced_method(42, 99))
            self.assertEqual(await some_method(42, 58), await traced_method(42, 58))

        async def test_timer_async(self):
            @timer
            async def operation(i: int) -> str:
                await asyncio.sleep(0.05)
                return str(i)

            await operation(42)

        async def test_deprecated_async(self):
            @deprecated
            async def old_method(i: int) -> str:
                return str(i)

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                await old_method(42)
                assert len(w) == 1
                assert issubclass(w[-1].category, DeprecationWarning)
                assert "deprecated" in str(w[-1].message)

        async def test_does_same_as_function_async(self):
            async def some_method(x, y, z):
                await asyncio.sleep(0)
                return x * (y + z)

            @does_same_as_function(some_method)
            async def other_method(x, y, z):
                await asyncio.sleep(0)
                return x * y + x * z

            await other_method(1, 2, 3)
            await other_method(4, 5, 6)

        async def test_does_same_as_function_async_and_sync(self):
            def some_method(x, y, z):
                return x * (y + z)

            @does_same_as_function(some_method)
            async def other_method(x, y, z):
                await asyncio.sleep(0)
                return x * y + x * z

            await other_method(1, 2, 3)
            await other_method(4, 5, 6)

        async def test_does_same_as_function_wrong(self):
            async def some_method(x, y, z):
                await asyncio.sleep(0)
                return x * (y + z)

            @does_same_as_function(some_method)
            async def other_method(x, y, z):
                await asyncio.sleep(0)
                return x * y + z

            await other_method(0, 2, 0)

            with self.assertRaises(expected_exception=AssertionError):
                await other_method(4, 5, 6)

        async def test_mock_async(self) -> None:
            @mock(return_value=42)
            async def my_function(a, b, c):
                await asyncio.sleep(0)
                return a + b + c

            assert await my_function(1, 2, 3) == 42
            assert await my_function(100, 200, 300) == 42

        async def test_require_kwargs(self):
            @require_kwargs
            async def calc(n: int, m: int, i: int) -> int:
                return n + m + i

            await calc(n=1, m=2, i=3)

            with self.assertRaises(expected_exception=PedanticCallWithArgsException):
                await calc(1, m=2, i=3)
