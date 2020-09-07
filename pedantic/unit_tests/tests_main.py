import unittest
import sys
import os
sys.path.append(os.getcwd())

# local file imports
from pedantic.unit_tests.tests_require_docstrings_google_format import TestRequireDocstringGoogleFormat
from pedantic.unit_tests.tests_require_kwargs import TestRequireKwargs
from pedantic.unit_tests.tests_class_decorators import TestClassDecorators
from pedantic.unit_tests.tests_pedantic_class import TestPedanticClass
from pedantic.unit_tests.tests_pedantic import TestDecoratorRequireKwargsAndTypeCheck
from pedantic.unit_tests.tests_small_method_decorators import TestSmallDecoratorMethods
from pedantic.unit_tests.tests_combination_of_decorators import TestCombinationOfDecorators

if __name__ == '__main__':
    unittest.main()
