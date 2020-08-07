import unittest

# local file imoorts
from PythonHelpers.decorators import require_kwargs


class TestRequireKwargs(unittest.TestCase):

    def test_kwargs(self):
        @require_kwargs
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        calc(n=1, m=2, i=3)

    def test_no_kwargs_1(self):
        @require_kwargs
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(1, m=2, i=3)

    def test_no_kwargs_2(self):
        @require_kwargs
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(1, 2, 3)
