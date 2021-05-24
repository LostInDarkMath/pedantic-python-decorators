import unittest

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.env_var_logic import enable_pedantic, disable_pedantic, is_enabled
from pedantic.decorators.fn_deco_pedantic import pedantic


class TestEnvironmentVariables(unittest.TestCase):
    def setUp(self) -> None:
        self.state = is_enabled()
        enable_pedantic()

    def tearDown(self) -> None:
        enable_pedantic()

    def test_pedantic_enabled(self):
        enable_pedantic()

        @pedantic
        def some_method():
            return 42

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_method()

    def test_pedantic_disabled(self):
        disable_pedantic()

        @pedantic
        def some_method():
            return 42

        some_method()

    def test_enable_disable(self):
        enable_pedantic()
        self.assertTrue(is_enabled())
        disable_pedantic()
        self.assertFalse(is_enabled())
        enable_pedantic()
        self.assertTrue(is_enabled())
