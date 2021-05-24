from typing import Iterator
from unittest import TestCase

from pedantic.models import GeneratorWrapper


class TestGeneratorWrapper(TestCase):
    def test_generator_wrapper(self) -> None:
        def gen_func() -> Iterator[int]:
            num = 0

            while num < 100:
                yield num
                num += 1

        generator = gen_func()

        g = GeneratorWrapper(
            wrapped=generator,
            expected_type=Iterator[int],
            err_msg='msg',
            type_vars={},
        )

        print(sum([x for x in g]))

        with self.assertRaises(expected_exception=Exception):
            g.throw(Exception('error'))

        with self.assertRaises(expected_exception=AttributeError):
            g.invalid

        g.close()
