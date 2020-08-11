import unittest
import sys
import os
sys.path.append(os.getcwd())

# local file imports
from pedantic.unit_tests.tests_require_docstrings_google_format import TestRequireDocstringGoogleFormat
from pedantic.unit_tests.tests_require_kwargs import TestRequireKwargs
from pedantic.unit_tests.tests_class_decorators import TestClassDecorators
from pedantic.unit_tests.tests_require_kwargs_and_type_check import TestDecoratorRequireKwargsAndTypeCheck
from pedantic.unit_tests.tests_small_method_decorators import TestSmallDecoratorMethods

if __name__ == '__main__':
    unittest.main()
