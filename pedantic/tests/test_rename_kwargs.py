import unittest

from pedantic import rename_kwargs, Rename


class TestRenameKwargs(unittest.TestCase):
    def test_rename_kwargs(self):
        @rename_kwargs(
            Rename(from_='x', to='a'),
            Rename(from_='y', to='b'),
        )
        def operation(a: int, b: int) -> int:
            return a + b

        operation(4, 5)
        operation(a=4, b=5)
        operation(x=4, y=5)
        operation(x=4, b=5)
