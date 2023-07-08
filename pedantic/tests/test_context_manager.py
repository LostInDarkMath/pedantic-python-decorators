from unittest import TestCase

from pedantic.decorators import safe_contextmanager


class TestContextManager(TestCase):
    def test_safe_context_manager_no_exception(self):
        before = False
        after = False

        @safe_contextmanager
        def foo():
            nonlocal before, after
            before = True
            yield 42
            after = True

        self.assertFalse(before)
        self.assertFalse(after)

        with foo() as f:
            self.assertTrue(before)
            self.assertFalse(after)
            self.assertEqual(42, f)

        self.assertTrue(before)
        self.assertTrue(after)

    def test_safe_context_manager_with_exception(self):
        before = False
        after = False

        @safe_contextmanager
        def foo():
            nonlocal before, after
            before = True
            yield 42
            after = True

        self.assertFalse(before)
        self.assertFalse(after)

        with self.assertRaises(expected_exception=ValueError):
            with foo() as f:
                self.assertTrue(before)
                self.assertFalse(after)
                self.assertEqual(42, f)
                raise ValueError('oh no')

        self.assertTrue(before)
        self.assertTrue(after)

    def test_safe_context_manager_with_args_kwargs(self):
        @safe_contextmanager
        def foo(a, b):
            yield a, b

        with foo(42, b=43) as f:
            self.assertEqual((42, 43), f)

    def test_safe_context_manager_async(self):
        with self.assertRaises(expected_exception=AssertionError) as e:
            @safe_contextmanager
            async def foo(a, b):
                yield a, b

        expected = 'foo is async. So you need to use "safe_async_contextmanager" instead.'
        self.assertEqual(expected, e.exception.args[0])

    def test_safe_context_manager_non_generator(self):
        with self.assertRaises(expected_exception=AssertionError) as e:
            @safe_contextmanager
            def foo(a, b):
                return a, b

        expected = 'foo is not a generator.'
        self.assertEqual(expected, e.exception.args[0])
