import unittest
import doctest


def run_doctests() -> None:
    parent_module = __import__('pedantic')
    method_decorators = parent_module.method_decorators

    test_suite = doctest.DocTestSuite(method_decorators, optionflags=doctest.ELLIPSIS)
    unittest.TextTestRunner().run(test_suite)


if __name__ == '__main__':
    run_doctests()
