import json
import os
from unittest import TestCase

from flask import Flask, jsonify, Response

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate
from pedantic.decorators.fn_deco_validate.parameters import Parameter, EnvironmentVariableParameter
from pedantic.decorators.fn_deco_validate.parameters.flask_parameters import FlaskJsonParameter
from pedantic.decorators.fn_deco_validate.validators import MaxLength, NotEmpty

JSON = 'application/json'
OK = 200
INVALID = 422


class TestValidate(TestCase):
    def test_validator_max_length(self) -> None:
        @validate(Parameter(name='x', validators=[MaxLength(3)]))
        def foo(x):
            return x

        self.assertEqual('hi', foo('hi'))
        self.assertEqual('hi!', foo('hi!'))
        self.assertEqual([1, 2, 3], foo([1, 2, 3]))

        with self.assertRaises(expected_exception=ValidationError):
            foo('hi!!')

        with self.assertRaises(expected_exception=ValidationError):
            foo([1, 2, 3, 4])

        with self.assertRaises(expected_exception=ValidationError):
            foo(42)

    def test_parameter(self) -> None:
        parameter = Parameter(name='x', validators=[MaxLength(3)])
        converted_value = parameter.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ValidationError):
            parameter.validate(value='hello world')

    def test_validator(self) -> None:
        validator = MaxLength(3)
        converted_value = validator.validate(value='hed')
        self.assertEqual(converted_value, 'hed')

        with self.assertRaises(expected_exception=ValidationError):
            validator.validate(value='hello world')

    def test_validator_is_not_empty(self) -> None:
        @validate(Parameter(name='x', validators=[NotEmpty()]))
        def foo(x: str) -> str:
            return x

        self.assertEqual('hi', foo('hi'))
        self.assertEqual('hi', foo('   hi     '))

        with self.assertRaises(expected_exception=ValidationError):
            foo('')

        with self.assertRaises(expected_exception=ValidationError):
            foo('      ')

    def test_validator_flask_json(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskJsonParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', data=json.dumps({'key': '  hello world  '}), content_type=JSON)
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', data=json.dumps({'key': '  '}), content_type=JSON)
            self.assertEqual(INVALID, res.status_code)
            expected = [{
                'rule': 'NotEmpty',
                'value': '  ',
                'message': 'Got empty String which is invalid.',
            }]
            self.assertEqual(expected, res.json)

    def test_parameter_environment_variable(self) -> None:
        @validate(EnvironmentVariableParameter(name='foo'))
        def bar(foo: str) -> str:
            return foo

        os.environ['foo'] = '42'
        self.assertEqual('42', bar())
