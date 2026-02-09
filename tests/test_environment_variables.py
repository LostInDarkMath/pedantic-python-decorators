import pytest

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.env_var_logic import enable_pedantic, disable_pedantic, is_enabled
from pedantic.decorators.fn_deco_pedantic import pedantic


def test_pedantic_enabled():
    enable_pedantic()

    @pedantic
    def some_method():
        return 42

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_method()


def test_pedantic_disabled():
    disable_pedantic()

    @pedantic
    def some_method():
        return 42

    some_method()


def test_enable_disable():
    enable_pedantic()
    assert is_enabled() is True
    disable_pedantic()
    assert is_enabled() is False
    enable_pedantic()
    assert is_enabled() is True
