import json
from unittest import TestCase

from flask import Flask, Response, jsonify

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError, ValidateException
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate, ReturnAs
from pedantic.decorators.fn_deco_validate.parameters.flask_parameters import FlaskJsonParameter, FlaskFormParameter, \
    FlaskHeaderParameter, FlaskGetParameter, FlaskPathParameter
from pedantic.decorators.fn_deco_validate.validators import NotEmpty, Min


JSON = 'application/json'
OK = 200
INVALID = 422


class TestFlaskParameters(TestCase):
    def test_validator_flask_json(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(
            FlaskJsonParameter(name='key', validators=[NotEmpty()]),
        )
        def hello_world(
                key: str,
        ) -> Response:
            return jsonify(key)

        @app.route('/required')
        @validate(
            FlaskJsonParameter(name='required', required=True),
            FlaskJsonParameter(name='not_required', required=False),
            FlaskJsonParameter(name='not_required_with_default', required=False, default=42),
        )
        def required_params(required, not_required, not_required_with_default) -> Response:
            return jsonify({
                'required': required,
                'not_required': not_required,
                'not_required_with_default': not_required_with_default,
            })

        @app.route('/types')
        @validate(
            FlaskJsonParameter(name='bool_param', value_type=bool),
            FlaskJsonParameter(name='int_param', value_type=int),
            FlaskJsonParameter(name='float_param', value_type=float),
            FlaskJsonParameter(name='str_param', value_type=str),
            FlaskJsonParameter(name='list_param', value_type=list),
            FlaskJsonParameter(name='dict_param', value_type=dict),
        )
        def different_types(
                bool_param,
                int_param,
                float_param,
                str_param,
                list_param,
                dict_param,
        ) -> Response:
            return jsonify({
                'bool_param': bool_param,
                'int_param': int_param,
                'float_param': float_param,
                'str_param': str_param,
                'list_param': list_param,
                'dict_param': dict_param,
            })

        @app.route('/args')
        @validate(
            FlaskJsonParameter(name='a', validators=[NotEmpty()]),
            FlaskJsonParameter(name='b', validators=[NotEmpty()]),
            return_as=ReturnAs.ARGS,
        )
        def names_do_not_need_to_match(my_key: str, another: str) -> Response:
            return jsonify({
                'my_key': my_key,
                'another': another,
            })

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', data=json.dumps({'key': '  hello world  '}), content_type=JSON)
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', data=json.dumps({'key': '  '}), content_type=JSON)
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': 'NotEmpty',
                'value': '  ',
                'message': 'Got empty String which is invalid.',
            }
            self.assertEqual(expected, res.json)

            data = {
                'key': '  hello world  ',
                'required': '1',
            }
            res = client.get('/', data=json.dumps(data), content_type=JSON)
            self.assertEqual(OK, res.status_code)

    def test_validator_flask_form_data(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', data={'key': '  hello world  '})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', data={'key': '  '})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': 'NotEmpty',
                'value': '  ',
                'message': 'Got empty String which is invalid.',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_header(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskHeaderParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', headers={'key': '  hello world  '}, data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', headers={'key': '  '}, data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': 'NotEmpty',
                'value': '  ',
                'message': 'Got empty String which is invalid.',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_header_optional_parameter(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskHeaderParameter(name='key', validators=[NotEmpty()], required=False))
        def hello_world(key: str = None) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', headers={'key': '  hello world  '}, data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', headers={}, data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual(None, res.json)

    def test_validator_flask_get(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskGetParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/?key=hello_world', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello_world', res.json)

            res = client.get('/?key=hello world', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/?key= ', data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': 'NotEmpty',
                'value': ' ',
                'message': 'Got empty String which is invalid.',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_path(self) -> None:
        app = Flask(__name__)

        @app.route('/<string:key>')
        @validate(FlaskPathParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/hello_world', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello_world', res.json)

            res = client.get('/hello world', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/   ', data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': 'NotEmpty',
                'value': '   ',
                'message': 'Got empty String which is invalid.',
            }
            self.assertEqual(expected, res.json)

    def test_invalid_value_type(self) -> None:
        app = Flask(__name__)

        with self.assertRaises(expected_exception=AssertionError):
            @app.route('/')
            @validate(FlaskFormParameter(name='key', value_type=tuple))
            def hello_world(key: str) -> Response:
                return jsonify(key)

    def test_wrong_name(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='k', value_type=str))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidateException)
        def handle_validation_error(exception: ValidateException) -> Response:
            print(str(exception))
            response = jsonify(str(exception))
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get(data={'key': 'k'})
            self.assertEqual(INVALID, res.status_code)
            self.assertEqual('Value for key k is required.', res.json)

    def test_default_value(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', value_type=str, default='42'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get(data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('42', res.json)

    def test_not_required_allows_none_kwargs_without_none(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', value_type=str, required=False),
                  return_as=ReturnAs.KWARGS_WITHOUT_NONE)
        def hello_world(key: str = 'it works') -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get(data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('it works', res.json)

    def test_not_required_allows_none_kwargs_with_none(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', value_type=str, required=False), return_as=ReturnAs.KWARGS_WITH_NONE)
        def hello_world(key: str) -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get(data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual(None, res.json)

    def test_not_required_with_default(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', value_type=str, required=False, default='42'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get(data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('42', res.json)

    def test_validator_flask_path_type_conversion(self) -> None:
        app = Flask(__name__)

        @app.route('/<string:key>')
        @validate(FlaskPathParameter(name='key', value_type=int, validators=[Min(42)]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/42', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual(42, res.json)

    def test_validator_flask_json_parameter_does_not_get_json(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskJsonParameter(name='key'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ValidationError)
        def handle_validation_error(exception: ValidationError) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                'rule': '',
                'value': 'None',
                'message': 'Data is not in JSON format.',
            }
            self.assertEqual(expected, res.json)
