import unittest
import warnings

from pedantic import pedantic, pedantic_require_docstring


class TestAssertionError36(unittest.TestCase):
    def test_require_docstring(self):
        with self.assertRaises(expected_exception=AssertionError):
            @pedantic_require_docstring
            def calc(n: int, m: int, i: int) -> int:
                """Returns the sum of the three args.

                Args:
                    n (int): something
                    m (int): something
                    i (int): something

                Returns:
                    int: bar
                """
                return n + m + i

            calc(n=42, m=40, i=38)

    def test_require_docstring_flag(self):
        with self.assertRaises(expected_exception=AssertionError):
            @pedantic(require_docstring=True)
            def calc(n: int, m: int, i: int) -> int:
                """Returns the sum of the three args.

                Args:
                    n (int): something
                    m (int): something
                    i (int): something

                Returns:
                    int: bar
                """
                return n + m + i

            calc(n=42, m=40, i=38)

    def test_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            @pedantic
            def calc(n: int, m: int, i: int) -> int:
                """Returns the sum of the three args.

                Args:
                    n (int): something
                    m (int): something
                    i (int): something

                Returns:
                    int: bar
                """
                return n + m + i

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "Docstrings cannot be checked in Python versions below 3.7" in str(w[-1].message)
            calc(n=42, m=40, i=38)

