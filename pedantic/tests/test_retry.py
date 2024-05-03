import unittest

from pedantic import retry
from pedantic.decorators.fn_deco_retry import retry_func


class TestRetry(unittest.TestCase):
    def test_retry_positive_no_args(self):
        count = 0

        @retry(attempts=5)
        def foo():
            nonlocal count
            count += 1

        foo()
        assert count == 1

    def test_retry_positive_args_and_kwargs(self):
        count = 0

        @retry(attempts=5)
        def foo(x, y):
            nonlocal count
            count += x + y

        foo(12, y=42)
        assert count == 54

    def test_retry_positive_no_args_fails_every_time(self):
        count = 0

        @retry(attempts=5)
        def foo():
            nonlocal count
            count += 1
            raise ValueError('foo')

        with self.assertRaises(ValueError):
            foo()

        assert count == 5

    def test_retry_positive_no_args_fails_different_exception_type(self):
        count = 0

        @retry(attempts=5, exceptions=AssertionError)
        def foo():
            nonlocal count
            count += 1
            raise ValueError('foo')

        with self.assertRaises(ValueError):
            foo()

        assert count == 1

    def test_retry_fails_same_exception_type(self):
        count = 0

        @retry(attempts=5, exceptions=AssertionError)
        def foo():
            nonlocal count
            count += 1
            raise AssertionError('foo')

        with self.assertRaises(AssertionError):
            foo()

        assert count == 5

    def test_retry_positive_no_args_fails_on_first_times(self):
        count = 0

        @retry(attempts=5)
        def foo() -> int:
            nonlocal count
            count += 1

            if count < 3:
                raise ValueError('foo')

            return count

        assert foo() == 3
        assert count == 3


class TestRetryFunc(unittest.TestCase):
    def test_retry_positive_no_args(self):
        count = 0

        def foo():
            nonlocal count
            count += 1

        retry_func(func=foo, attempts=5)
        assert count == 1

    def test_retry_positive_args_and_kwargs(self):
        count = 0

        def foo(x, y):
            nonlocal count
            count += x + y

        retry_func(foo, 12, attempts=5, y=42)
        assert count == 54

    def test_retry_positive_no_args_fails_every_time(self):
        count = 0

        def foo():
            nonlocal count
            count += 1
            raise ValueError('foo')

        with self.assertRaises(ValueError):
            retry_func(func=foo, attempts=5)

        assert count == 5

    def test_retry_positive_no_args_fails_different_exception_type(self):
        count = 0

        def foo():
            nonlocal count
            count += 1
            raise ValueError('foo')

        with self.assertRaises(ValueError):
            retry_func(func=foo, attempts=5, exceptions=AssertionError)

        assert count == 1

    def test_retry_fails_same_exception_type(self):
        count = 0

        def foo():
            nonlocal count
            count += 1
            raise AssertionError('foo')

        with self.assertRaises(AssertionError):
            retry_func(func=foo, attempts=5, exceptions=AssertionError)

        assert count == 5

    def test_retry_positive_no_args_fails_on_first_times(self):
        count = 0

        def foo() -> int:
            nonlocal count
            count += 1

            if count < 3:
                raise ValueError('foo')

            return count

        assert retry_func(func=foo, attempts=5) == 3
        assert count == 3
