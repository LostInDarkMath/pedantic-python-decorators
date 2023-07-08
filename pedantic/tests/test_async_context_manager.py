import unittest

from pedantic.decorators import safe_async_contextmanager


class TestAsyncContextManager(unittest.IsolatedAsyncioTestCase):
    async def test_safe_context_manager_no_exception(self):
        before = False
        after = False

        @safe_async_contextmanager
        async def foo():
            nonlocal before, after
            before = True
            yield 42
            after = True

        self.assertFalse(before)
        self.assertFalse(after)

        async with foo() as f:
            self.assertTrue(before)
            self.assertFalse(after)
            self.assertEqual(42, f)

        self.assertTrue(before)
        self.assertTrue(after)

    async def test_safe_context_manager_with_exception(self):
        before = False
        after = False

        @safe_async_contextmanager
        async def foo():
            nonlocal before, after
            before = True
            yield 42
            after = True

        self.assertFalse(before)
        self.assertFalse(after)

        with self.assertRaises(expected_exception=ValueError):
            async with foo() as f:
                self.assertTrue(before)
                self.assertFalse(after)
                self.assertEqual(42, f)
                raise ValueError('oh no')

        self.assertTrue(before)
        self.assertTrue(after)

    async def test_safe_context_manager_with_args_kwargs(self):
        @safe_async_contextmanager
        async def foo(a, b):
            yield a, b

        async with foo(42, b=43) as f:
            self.assertEqual((42, 43), f)

    def test_safe_context_manager_async(self):
        with self.assertRaises(expected_exception=AssertionError) as e:
            @safe_async_contextmanager
            def foo(a, b):
                yield a, b

        expected = 'foo is not an async generator. So you need to use "safe_contextmanager" instead.'
        self.assertEqual(expected, e.exception.args[0])

    async def test_safe_context_manager_non_generator(self):
        with self.assertRaises(expected_exception=AssertionError) as e:
            @safe_async_contextmanager
            async def foo(a, b):
                return a, b

        expected = 'foo is not a generator.'
        self.assertEqual(expected, e.exception.args[0])
