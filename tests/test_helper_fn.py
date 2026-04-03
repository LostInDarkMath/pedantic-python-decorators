import pytest

from pedantic import run_doctest_of_single_function


def foo(x):
    """
    Examples:
    >>> foo(1)
    1
    >>> foo(2)
    2
    """
    return x


def test_run_doctests_single_green():
    run_doctest_of_single_function(foo)


def test_run_doctests_single_red():
    foo.__doc__ = """
    Examples:
    >>> foo(1)
    1
    >>> foo(2)
    2
    >>> foo(3)
    4
    """

    with pytest.raises(AssertionError, match=r'Failed tests: 1'):
        run_doctest_of_single_function(foo)
