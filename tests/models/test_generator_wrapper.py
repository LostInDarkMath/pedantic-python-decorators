from typing import Iterator

import pytest

from pedantic.models import GeneratorWrapper


def test_generator_wrapper():
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

    with pytest.raises(expected_exception=Exception):
        g.throw(Exception('error'))

    with pytest.raises(expected_exception=AttributeError):
        g.invalid

    g.close()
