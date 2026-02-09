import pytest

from pedantic.exceptions import PedanticCallWithArgsException
from pedantic import require_kwargs


def test_kwargs():
    @require_kwargs
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    calc(n=1, m=2, i=3)


def test_no_kwargs_1():
    @require_kwargs
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        calc(1, m=2, i=3)

def test_no_kwargs_2():
    @require_kwargs
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        calc(1, 2, 3)
