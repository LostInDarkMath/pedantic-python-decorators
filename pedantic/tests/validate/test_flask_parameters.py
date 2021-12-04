import json
import sys
from typing import List
from unittest import TestCase

from flask import Flask, Response, jsonify

from pedantic import Email
from pedantic.decorators.fn_deco_validate.exceptions import ValidateException, TooManyArguments, \
    ParameterException, ExceptionDictKey, InvalidHeader
from pedantic.decorators.fn_deco_validate.fn_deco_validate import validate, ReturnAs
from pedantic.decorators.fn_deco_validate.parameters.flask_parameters import FlaskJsonParameter, FlaskFormParameter, \
    FlaskHeaderParameter, FlaskGetParameter, FlaskPathParameter
from pedantic.decorators.fn_deco_validate.validators import NotEmpty, Min


JSON = 'application/json'
OK = 200
INVALID = 422
TOO_MANY_ARGS = 400


class TestFlaskParameters(TestCase):
    def test_validator_flask_json(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(
            FlaskJsonParameter(name='key', validators=[NotEmpty()]),
        )
        def hello_world(key: str) -> Response:
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

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        @app.errorhandler(TooManyArguments)
        def handle_validation_error(exception: TooManyArguments) -> Response:
            print(str(exception))
            response = jsonify(str(exception))
            response.status_code = TOO_MANY_ARGS
            return response

        with app.test_client() as client:
            res = client.get('/', data=json.dumps({'key': '  hello world  '}), content_type=JSON)
            self.assertEqual(OK, res.status_code)
            self.assertEqual('hello world', res.json)

            res = client.get('/', data=json.dumps({'key': '  '}), content_type=JSON)
            self.assertEqual(INVALID, res.status_code)
            expected = {
                ExceptionDictKey.VALIDATOR: 'NotEmpty',
                ExceptionDictKey.VALUE: '  ',
                ExceptionDictKey.MESSAGE: 'Got empty String which is invalid.',
                ExceptionDictKey.PARAMETER: 'key',
            }
            self.assertEqual(expected, res.json)

            data = {
                'key': '  hello world  ',
                'required': '1',
            }
            res = client.get('/', data=json.dumps(data), content_type=JSON)
            self.assertEqual(TOO_MANY_ARGS, res.status_code)
            self.assertEqual("Got unexpected arguments: ['required']", res.json)

    def test_validator_flask_form_data(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
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
                ExceptionDictKey.VALIDATOR: 'NotEmpty',
                ExceptionDictKey.VALUE: '  ',
                ExceptionDictKey.MESSAGE: 'Got empty String which is invalid.',
                ExceptionDictKey.PARAMETER: 'key',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_header(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskHeaderParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(InvalidHeader)
        def handle_validation_error(exception: InvalidHeader) -> Response:
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
                ExceptionDictKey.VALUE: '  ',
                ExceptionDictKey.MESSAGE: 'Got empty String which is invalid.',
                ExceptionDictKey.PARAMETER: 'key',
                ExceptionDictKey.VALIDATOR: 'NotEmpty',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_header_optional_parameter(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskHeaderParameter(name='key', validators=[NotEmpty()], required=False))
        def hello_world(key: str = None) -> Response:
            return jsonify(key)

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
        @validate(FlaskGetParameter(name='key', value_type=str, validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
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
                ExceptionDictKey.VALIDATOR: 'NotEmpty',
                ExceptionDictKey.VALUE: ' ',
                ExceptionDictKey.MESSAGE: 'Got empty String which is invalid.',
                ExceptionDictKey.PARAMETER: 'key',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_get_multiple_values_for_same_key(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskGetParameter(name='key', value_type=list, validators=[NotEmpty()]))
        def hello_world(key: List[str]) -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get('/?key=hello&key=world', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual(['hello', 'world'], res.json)

    def test_validator_flask_path(self) -> None:
        app = Flask(__name__)

        @app.route('/<string:key>')
        @validate(FlaskPathParameter(name='key', validators=[NotEmpty()]))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
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
                ExceptionDictKey.VALIDATOR: 'NotEmpty',
                ExceptionDictKey.VALUE: '   ',
                ExceptionDictKey.MESSAGE: 'Got empty String which is invalid.',
                ExceptionDictKey.PARAMETER: 'key',
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
            self.assertIn('Value for parameter k is required.', res.json)

    def test_default_value(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskFormParameter(name='key', value_type=str, default='42'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

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
        @validate(FlaskFormParameter(name='key', value_type=str, required=False, default=None),
                  return_as=ReturnAs.KWARGS_WITH_NONE)
        def hello_world(key: str) -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get(data={'key': None})
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

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/42', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual(42, res.json)

            res = client.get('/42f', data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                ExceptionDictKey.VALIDATOR: None,
                ExceptionDictKey.VALUE: '42f',
                ExceptionDictKey.MESSAGE: "Value 42f cannot be converted to <class 'int'>.",
                ExceptionDictKey.PARAMETER: 'key',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_json_parameter_does_not_get_json(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskJsonParameter(name='key'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
            print(str(exception))
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get('/', data={})
            self.assertEqual(INVALID, res.status_code)
            expected = {
                ExceptionDictKey.VALIDATOR: None,
                ExceptionDictKey.VALUE: 'None',
                ExceptionDictKey.MESSAGE: 'Value for parameter key is required.',
                ExceptionDictKey.PARAMETER: 'key',
            }
            self.assertEqual(expected, res.json)

    def test_validator_flask_json_parameter_does_not_get_json_but_default(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskJsonParameter(name='key', default='42'))
        def hello_world(key: str) -> Response:
            return jsonify(key)

        with app.test_client() as client:
            res = client.get('/', data={})
            self.assertEqual(OK, res.status_code)
            self.assertEqual('42', res.json)

    def test_too_many_arguments(self) -> None:
        app = Flask(__name__)

        @app.route('/')
        @validate(FlaskJsonParameter(name='k', value_type=str))
        def hello_world(**kwargs) -> Response:
            return jsonify(str(kwargs))

        @app.errorhandler(TooManyArguments)
        def handle_validation_error(exception: TooManyArguments) -> Response:
            print(str(exception))
            response = jsonify(str(exception))
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get(data=json.dumps({'k': 'k', 'a': 1}), content_type=JSON)
            self.assertEqual(INVALID, res.status_code)
            self.assertEqual("Got unexpected arguments: ['a']", res.json)

    def test_exception_for_required_parameter(self) -> None:
        app = Flask(__name__)
        key = 'PASSWORD'

        @app.route('/')
        @validate(FlaskJsonParameter(name=key, value_type=str))
        def hello_world(**kwargs) -> Response:
            return jsonify(str(kwargs))

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
            reason = 'required' if 'required' in exception.message else 'invalid'
            response = jsonify({exception.parameter_name: [{'KEY': reason}]})
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get(data=json.dumps({}), content_type=JSON)
            self.assertEqual(INVALID, res.status_code)
            self.assertEqual({key: [{'KEY': 'required'}]}, res.json)

    def test_async_endpoints(self) -> None:
        """ This test requires Python 3.7 or above because async Flask endpoints require this. """

        if sys.version_info < (3, 7):
            print(f'Skip test, because Python 3.7+ is required.')
            return

        app = Flask(__name__)

        @app.route('/<int:k>')
        @validate(FlaskPathParameter(name='k', value_type=int, validators=[Min(42)]))
        async def hello_world(k) -> Response:
            return jsonify(str(k))

        @app.route('/foo/<int:k>')
        @validate(FlaskPathParameter(name='k', value_type=int, validators=[Min(42)]), return_as=ReturnAs.ARGS)
        async def return_args(k) -> Response:
            return jsonify(str(k))

        @app.route('/bar/<int:k>')
        @validate(FlaskPathParameter(name='k', value_type=int, validators=[Min(42)]),
                  return_as=ReturnAs.KWARGS_WITH_NONE)
        async def return_kwargs_with_none(k) -> Response:
            return jsonify(str(k))

        @app.errorhandler(ParameterException)
        def handle_validation_error(exception: ParameterException) -> Response:
            response = jsonify(exception.to_dict)
            response.status_code = INVALID
            return response

        with app.test_client() as client:
            res = client.get(path=f'/45')
            self.assertEqual(OK, res.status_code)

            res = client.get(path=f'/foo/45')
            self.assertEqual(OK, res.status_code)

            res = client.get(path=f'/bar/45')
            self.assertEqual(OK, res.status_code)

            res = client.get(path=f'/41')
            self.assertEqual(INVALID, res.status_code)
            expected = {
                ExceptionDictKey.MESSAGE: 'smaller then allowed: 41 is not >= 42',
                ExceptionDictKey.PARAMETER: 'k',
                ExceptionDictKey.VALIDATOR: 'Min',
                ExceptionDictKey.VALUE: '41',
            }
            self.assertEqual(expected, res.json)

    def test_json_parameter_with_default_value(self) -> None:
        app = Flask(__name__)

        @app.route('/testing/message/<string:email>', methods=['POST'])
        @validate(
            FlaskPathParameter(name='email', value_type=str, validators=[Email()]),
            FlaskJsonParameter(name='content', value_type=str, default='this is a fake message', required=False),
            return_as=ReturnAs.ARGS,
        )
        def testing_send_system_message(email: str, content: str) -> Response:
            return jsonify({'email': email, 'content': content})

        with app.test_client() as client:
            res = client.post(path=f'/testing/message/adam@eva.de')
            self.assertEqual(OK, res.status_code)
            expected = {
                'email': 'adam@eva.de',
                'content': 'this is a fake message',
            }
            self.assertEqual(expected, res.json)

            res = client.post(path=f'/testing/message/adam@eva.de', json={'content': 'hello world'})
            self.assertEqual(OK, res.status_code)
            expected = {
                'email': 'adam@eva.de',
                'content': 'hello world',
            }
            self.assertEqual(expected, res.json)
