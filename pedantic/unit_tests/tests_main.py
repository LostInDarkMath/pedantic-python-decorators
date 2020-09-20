import unittest
import sys
import os

sys.path.append(os.getcwd())

from pedantic.unit_tests.tests_doctests import run_doctests

from pedantic.unit_tests.tests_require_kwargs import TestRequireKwargs
from pedantic.unit_tests.tests_class_decorators import TestClassDecorators
from pedantic.unit_tests.tests_pedantic_class import TestPedanticClass
from pedantic.unit_tests.tests_pedantic import TestDecoratorRequireKwargsAndTypeCheck
from pedantic.unit_tests.tests_small_method_decorators import TestSmallDecoratorMethods
from pedantic.unit_tests.tests_combination_of_decorators import TestCombinationOfDecorators

if sys.version_info >= (3, 7):
    from pedantic.unit_tests.tests_docstring import TestRequireDocstringGoogleFormat
    from pedantic.unit_tests.tests_pedantic_class_docstring import TestPedanticClassDocstring
else:
    from pedantic.unit_tests.tests_assertion_error_3_6 import TestAssertionError36


def run_tests() -> None:
    run_doctests()
    unittest.main()


if __name__ == '__main__':
    run_tests()
