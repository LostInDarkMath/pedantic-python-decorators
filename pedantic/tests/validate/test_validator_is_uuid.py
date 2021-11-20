from unittest import TestCase
from uuid import uuid1, uuid3, uuid4, uuid5

from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import IsUuid


class TestValidatorIsUUID(TestCase):
    def test_validator_is_enum_convert_true(self) -> None:
        @validate(Parameter(name='x', validators=[IsUuid()]))
        def foo(x):
            return x

        for id_ in [str(uuid1()), str(uuid3(uuid1(), 'b')), str(uuid4()), str(uuid5(uuid1(), 'b'))]:
            self.assertEqual(id_, foo(id_))

        with self.assertRaises(expected_exception=ParameterException):
            foo('invalid')
