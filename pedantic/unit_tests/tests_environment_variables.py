import unittest

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.set_envionment_variables import enable_pedantic, disable_pedantic, is_enabled
from pedantic.method_decorators import pedantic


class TestEnvironmentVariables(unittest.TestCase):
    def setUp(self) -> None:
        self.state = is_enabled()
        enable_pedantic()

    def tearDown(self) -> None:
        if self.state:
            enable_pedantic()
        else:
            disable_pedantic()

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
