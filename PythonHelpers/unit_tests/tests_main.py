import unittest
import sys
import os
sys.path.append(os.getcwd())

# local file imports
from PythonHelpers.unit_tests.tests_require_docstrings_google_format import TestRequireDocstringGoogleFormat
from PythonHelpers.unit_tests.tests_require_kwargs import TestRequireKwargs
from PythonHelpers.unit_tests.tests_require_kwargs_and_type_check import TestDecoratorRequireKwargsAndTypeCheck

if __name__ == '__main__':
    unittest.main()
