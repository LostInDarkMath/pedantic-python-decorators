import unittest
import doctest


def run_doctests() -> None:
    unittest.TextTestRunner().run(get_doctest_test_suite())


def get_doctest_test_suite() -> unittest.TestSuite:
    parent_module = __import__('pedantic')
    method_decorators = parent_module.method_decorators
    return doctest.DocTestSuite(method_decorators, optionflags=doctest.ELLIPSIS)


if __name__ == '__main__':
    run_doctests()
