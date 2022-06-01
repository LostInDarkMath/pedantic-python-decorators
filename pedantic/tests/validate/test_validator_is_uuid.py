from unittest import TestCase
from uuid import uuid1, uuid3, uuid4, uuid5

from pedantic import ForEach
from pedantic.decorators.fn_deco_validate.exceptions import ParameterException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter
from pedantic.decorators.fn_deco_validate.validators import IsUuid


class TestValidatorIsUUID(TestCase):
    def test_validator_is_uuid(self):
        @validate(Parameter(name='x', validators=[IsUuid()], required=False))
        def foo(x):
            return x

        for id_ in [str(uuid1()), str(uuid3(uuid1(), 'b')), str(uuid4()), str(uuid5(uuid1(), 'b'))]:
            self.assertEqual(id_, foo(id_))

        for no_id in ['invalid', 12]:
            with self.assertRaises(expected_exception=ParameterException):
                foo(no_id)

    def test_validator_is_uuid_with_for_each_and_none_value(self):
        @validate(Parameter(name='x', validators=[ForEach(IsUuid())]))
        def foo(x):
            return x

        uuid = str(uuid1())
        self.assertEqual([], foo([]))
        self.assertEqual([uuid], foo([uuid]))

        with self.assertRaises(expected_exception=ParameterException):
            foo([None])
