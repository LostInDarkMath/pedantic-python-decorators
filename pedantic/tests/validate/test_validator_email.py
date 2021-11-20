from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Email


class TestValidatorEmail(TestCase):
    def test_validator_email(self) -> None:
        @validate(Parameter(name='x', validators=[Email()]))
        def foo(x):
            return x

        for value in ['fred@web.de', 'genial@gmail.com', 'test@test.co.uk']:
            self.assertEqual(value, foo(value))

        for value in ['fred', 'fred@web', 'fred@w@eb.de', 'fred@@web.de', 'invalid@invalid']:
            with self.assertRaises(expected_exception=ParameterException):
                foo(value)
