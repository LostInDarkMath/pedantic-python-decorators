import unittest
from typing import Generator, Iterator, Iterable, List

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic


class TestGenerator(unittest.TestCase):
    def test_iterator(self):
        @pedantic
        def gen_func() -> Iterator[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = gen_func()
        next(gen)

    def test_iterator_wrong_type_hint(self):
        @pedantic
        def genfunc() -> Iterator[float]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = genfunc()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            next(gen)

    def test_iterator_no_type_args(self):
        @pedantic
        def genfunc() -> Iterator:
            num = 0

            while num < 100:
                yield num
                num += 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            genfunc()

    def test_iterator_completely_wrong_type_hint(self):
        @pedantic
        def gen_func() -> List[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            gen_func()

    def test_iterable(self):
        @pedantic
        def gen_func() -> Iterable[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        gen = gen_func()
        next(gen)

    def test_iterable_no_type_args(self):
        @pedantic
        def gen_func() -> Iterable:
            num = 0

            while num < 100:
                yield num
                num += 1

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            gen_func()

    def test_generator(self):
        @pedantic
        def gen_func() -> Generator[int, None, str]:
            num = 0

            while num < 100:
                yield num
                num += 1
            return 'Done'

        gen = gen_func()
        next(gen)

    def test_invalid_no_type_args_generator(self):
        @pedantic
        def gen_func() -> Generator:
            num = 0

            while num < 100:
                yield num
                num += 1
            return 'Done'

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            gen_func()
