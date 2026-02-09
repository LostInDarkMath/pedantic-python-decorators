import pytest

from pedantic.decorators.fn_deco_retry import retry_func

def test_retry_positive_no_args():
    count = 0

    def foo():
        nonlocal count
        count += 1

    retry_func(func=foo, attempts=5)
    assert count == 1


def test_retry_positive_args_and_kwargs():
    count = 0

    def foo(x, y):
        nonlocal count
        count += x + y

    retry_func(foo, 12, attempts=5, y=42)
    assert count == 54


def test_retry_positive_no_args_fails_every_time():
    count = 0

    def foo():
        nonlocal count
        count += 1
        raise ValueError('foo')

    with pytest.raises(ValueError):
        retry_func(func=foo, attempts=5)

    assert count == 5


def test_retry_positive_no_args_fails_different_exception_type():
    count = 0

    def foo():
        nonlocal count
        count += 1
        raise ValueError('foo')

    with pytest.raises(ValueError):
        retry_func(func=foo, attempts=5, exceptions=AssertionError)

    assert count == 1


def test_retry_fails_same_exception_type():
    count = 0

    def foo():
        nonlocal count
        count += 1
        raise AssertionError('foo')

    with pytest.raises(AssertionError):
        retry_func(func=foo, attempts=5, exceptions=AssertionError)

    assert count == 5


def test_retry_positive_no_args_fails_on_first_times():
    count = 0

    def foo() -> int:
        nonlocal count
        count += 1

        if count < 3:
            raise ValueError('foo')

        return count

    assert retry_func(func=foo, attempts=5) == 3
    assert count == 3
