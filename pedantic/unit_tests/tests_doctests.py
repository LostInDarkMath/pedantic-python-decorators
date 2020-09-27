import unittest
import doctest


def run_doctests() -> None:
    unittest.TextTestRunner().run(get_doctest_test_suite())


def get_doctest_test_suite() -> unittest.TestSuite:
    parent_module = __import__('pedantic')
    modules = [
        parent_module.method_decorators,
        parent_module.type_hint_parser,
        parent_module.check_generic_classes,
    ]
    test_suites = [doctest.DocTestSuite(module=module, optionflags=doctest.ELLIPSIS) for module in modules]
    return unittest.TestSuite(test_suites)


if __name__ == '__main__':
    run_doctests()
