import sys
import unittest
import doctest


def run_doctests() -> None:
    unittest.TextTestRunner().run(get_doctest_test_suite())


def get_doctest_test_suite() -> unittest.TestSuite:
    parent_module = __import__('pedantic')
    modules = [
        parent_module.method_decorators,
        parent_module.type_hint_parser,
    ]
    blacklist_python_version_below_3_7 = [
        '_parse_documented_type',
        '_update_context',
    ]
    test_suites = []

    for module in modules:
        doctest_suite = doctest.DocTestSuite(module=module, optionflags=doctest.ELLIPSIS)

        if sys.version_info >= (3, 7):
            test_suites.append(doctest_suite)
        else:
            test_suite_without_blacklist = unittest.TestSuite()

            for test in doctest_suite:
                if test.id().split('.')[-1] not in blacklist_python_version_below_3_7:
                    test_suite_without_blacklist.addTest(test)
            test_suites.append(test_suite_without_blacklist)
    return unittest.TestSuite(test_suites)


if __name__ == '__main__':
    run_doctests()
