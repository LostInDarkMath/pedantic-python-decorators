import pytest

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import Email


def test_validator_email():
    @validate(Parameter(name='x', validators=[Email()]))
    def foo(x):
        return x

    for value in ['fred@web.de', 'genial@gmail.com', 'test@test.co.uk']:
        assert foo(value) == value

    for value in ['fred', 'fred@web', 'fred@w@eb.de', 'fred@@web.de', 'invalid@invalid']:
        with pytest.raises(expected_exception=ParameterException):
            foo(value)


def test_validator_email_converts_to_lower_case():
    @validate(Parameter(name='x', validators=[Email(post_processor=lambda x: x.lower())]))
    def foo(x):
        return x

    for value in ['Fred@Web.de', 'GENIAL@GMAIL.com', 'test@test.CO.UK']:
        assert foo(value) == value.lower()
