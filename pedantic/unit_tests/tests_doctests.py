import sys
import unittest
import doctest


def run_doctests() -> None:
    unittest.TextTestRunner().run(get_doctest_test_suite())


def get_doctest_test_suite() -> unittest.TestSuite:
    parent_module = __import__('pedantic')
    method_decorators = parent_module.method_decorators
    doctest_suite = doctest.DocTestSuite(method_decorators, optionflags=doctest.ELLIPSIS)

    if sys.version_info >= (3, 7):
        return doctest_suite

    blacklist = [
        '_parse_documented_type',
        '_update_context',
    ]
    new_suite = unittest.TestSuite()

    for test in doctest_suite._tests:
        if test._dt_test.name.split('.')[-1] not in blacklist:
            new_suite.addTest(test)

    return new_suite


if __name__ == '__main__':
    run_doctests()
