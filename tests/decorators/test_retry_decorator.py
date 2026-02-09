import pytest

from pedantic import retry


def test_retry_positive_no_args():
    count = 0

    @retry(attempts=5)
    def foo():
        nonlocal count
        count += 1

    foo()
    assert count == 1


def test_retry_positive_args_and_kwargs():
    count = 0

    @retry(attempts=5)
    def foo(x, y):
        nonlocal count
        count += x + y

    foo(12, y=42)
    assert count == 54


def test_retry_positive_no_args_fails_every_time():
    count = 0

    @retry(attempts=5)
    def foo():
        nonlocal count
        count += 1
        raise ValueError('foo')

    with pytest.raises(ValueError):
        foo()

    assert count == 5


def test_retry_positive_no_args_fails_different_exception_type():
    count = 0

    @retry(attempts=5, exceptions=AssertionError)
    def foo():
        nonlocal count
        count += 1
        raise ValueError('foo')

    with pytest.raises(ValueError):
        foo()

    assert count == 1


def test_retry_fails_same_exception_type():
    count = 0

    @retry(attempts=5, exceptions=AssertionError)
    def foo():
        nonlocal count
        count += 1
        raise AssertionError('foo')

    with pytest.raises(AssertionError):
        foo()

    assert count == 5


def test_retry_positive_no_args_fails_on_first_times():
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
