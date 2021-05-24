from unittest import TestCase

from pedantic import mock


class TestMock(TestCase):
    def test_mock(self) -> None:
        @mock(return_value=42)
        def my_function(a, b, c):
            return a + b + c

        assert my_function(1, 2, 3) == 42
        assert my_function(100, 200, 300) == 42
