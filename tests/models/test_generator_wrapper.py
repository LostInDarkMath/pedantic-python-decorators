from typing import Iterator  # noqa: UP035

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

    assert sum(x for x in g) == 4950

    with pytest.raises(expected_exception=ValueError, match='error'):
        g.throw(ValueError('error'))

    with pytest.raises(expected_exception=AttributeError):
        g.invalid  # noqa: B018

    g.close()
