import unittest
import sys
import os

sys.path.append(os.getcwd())

from pedantic.tests.validate.test_convert_value import TestConvertValue
from pedantic.tests.test_rename_kwargs import TestRenameKwargs
from pedantic.tests.validate.test_datetime_isoformat import TestValidatorDatetimeIsoformat
from pedantic.tests.validate.test_flask_parameters import TestFlaskParameters
from pedantic.tests.validate.test_parameter_environment_variable import TestParameterEnvironmentVariable
from pedantic.tests.validate.test_validate import TestValidate

if sys.version_info >= (3, 8):
    from pedantic.tests.validate.test_validate import AsyncValidateTests
    from pedantic.tests.tests_small_method_decorators import AsyncSmallDecoratorTests
    from pedantic.tests.tests_pedantic_async import TestPedanticAsyncio

from pedantic.tests.validate.test_validator_composite import TestValidatorComposite
from pedantic.tests.validate.test_validator_datetime_unix_timestamp import TestValidatorDatetimeUnixTimestamp
from pedantic.tests.validate.test_validator_email import TestValidatorEmail
from pedantic.tests.validate.test_validator_for_each import TestValidatorForEach
from pedantic.tests.validate.test_validator_is_enum import TestValidatorIsEnum
from pedantic.tests.validate.test_validator_is_uuid import TestValidatorIsUUID
from pedantic.tests.validate.test_validator_match_pattern import TestValidatorMatchPattern
from pedantic.tests.validate.test_validator_max import TestValidatorMax
from pedantic.tests.validate.test_validator_max_length import TestValidatorMaxLength
from pedantic.tests.validate.test_validator_min import TestValidatorMin
from pedantic.tests.validate.test_validator_min_length import TestValidatorMinLength
from pedantic.tests.validate.test_validator_not_empty import TestValidatorNotEmpty
from pedantic.tests.test_generator_wrapper import TestGeneratorWrapper
from pedantic.tests.tests_mock import TestMock
from pedantic.tests.tests_doctests import get_doctest_test_suite
from pedantic.tests.tests_require_kwargs import TestRequireKwargs
from pedantic.tests.tests_class_decorators import TestClassDecorators
from pedantic.tests.tests_pedantic_class import TestPedanticClass
from pedantic.tests.tests_pedantic import TestDecoratorRequireKwargsAndTypeCheck
from pedantic.tests.tests_small_method_decorators import TestSmallDecoratorMethods
from pedantic.tests.tests_combination_of_decorators import TestCombinationOfDecorators
from pedantic.tests.tests_docstring import TestRequireDocstringGoogleFormat
from pedantic.tests.tests_pedantic_class_docstring import TestPedanticClassDocstring
from pedantic.tests.tests_decorated_function import TestDecoratedFunction
from pedantic.tests.tests_environment_variables import TestEnvironmentVariables
from pedantic.tests.tests_generic_classes import TestGenericClasses
from pedantic.tests.tests_generator import TestGenerator


def run_all_tests() -> None:
    test_classes_to_run = [
        TestRequireKwargs,
        TestClassDecorators,
        TestPedanticClass,
        TestDecoratorRequireKwargsAndTypeCheck,
        TestSmallDecoratorMethods,
        TestCombinationOfDecorators,
        TestRequireDocstringGoogleFormat,
        TestPedanticClassDocstring,
        TestDecoratedFunction,
        TestEnvironmentVariables,
        TestGenericClasses,
        TestGenerator,
        TestMock,
        TestGeneratorWrapper,
        TestRenameKwargs,
        # validate
        TestValidatorDatetimeIsoformat,
        TestFlaskParameters,
        TestParameterEnvironmentVariable,
        TestConvertValue,
        TestValidate,
        TestValidatorComposite,
        TestValidatorDatetimeUnixTimestamp,
        TestValidatorEmail,
        TestValidatorForEach,
        TestValidatorIsEnum,
        TestValidatorIsUUID,
        TestValidatorMatchPattern,
        TestValidatorMax,
        TestValidatorMaxLength,
        TestValidatorMin,
        TestValidatorMinLength,
        TestValidatorNotEmpty,
    ]

    if sys.version_info >= (3, 8):
        async_test_classes_to_run = [
            AsyncValidateTests,
            AsyncSmallDecoratorTests,
            TestPedanticAsyncio,
        ]
        test_classes_to_run.extend(async_test_classes_to_run)

    loader = unittest.TestLoader()
    suites_list = [get_doctest_test_suite()]

    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)
    runner = unittest.TextTestRunner()
    result = runner.run(big_suite)
    assert not result.errors and not result.failures, f'Some tests failed!'


if __name__ == '__main__':
    run_all_tests()
