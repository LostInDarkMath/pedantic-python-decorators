from typing import Generator, Iterator, Iterable, List

import pytest

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic


def test_iterator():
    @pedantic
    def gen_func() -> Iterator[int]:
        num = 0

        while num < 100:
            yield num
            num += 1

    gen = gen_func()
    next(gen)


def test_iterator_wrong_type_hint():
    @pedantic
    def genfunc() -> Iterator[float]:
        num = 0

        while num < 100:
            yield num
            num += 1

    gen = genfunc()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        next(gen)


def test_iterator_no_type_args():
    @pedantic
    def genfunc() -> Iterator:
        num = 0

        while num < 100:
            yield num
            num += 1

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        genfunc()


def test_iterator_completely_wrong_type_hint():
    @pedantic
    def gen_func() -> List[int]:
        num = 0

        while num < 100:
            yield num
            num += 1

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        gen_func()


def test_iterable():
    @pedantic
    def gen_func() -> Iterable[int]:
        num = 0

        while num < 100:
            yield num
            num += 1

    gen = gen_func()
    next(gen)


def test_iterable_no_type_args():
    @pedantic
    def gen_func() -> Iterable:
        num = 0

        while num < 100:
            yield num
            num += 1

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        gen_func()


def test_generator():
    @pedantic
    def gen_func() -> Generator[int, None, str]:
        num = 0

        while num < 100:
            yield num
            num += 1
        return 'Done'

    gen = gen_func()
    next(gen)


def test_invalid_no_type_args_generator():
    @pedantic
    def gen_func() -> Generator:
        num = 0

        while num < 100:
            yield num
            num += 1
        return 'Done'

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        gen_func()
