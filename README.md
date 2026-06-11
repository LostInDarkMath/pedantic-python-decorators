# Pedantic 
[![Coverage Status](https://coveralls.io/repos/github/LostInDarkMath/pedantic-python-decorators/badge.svg?branch=master)](https://coveralls.io/github/LostInDarkMath/pedantic-python-decorators?branch=master) [![PyPI version](https://badge.fury.io/py/pedantic.svg)](https://badge.fury.io/py/pedantic) [![Conda Version](https://img.shields.io/conda/vn/conda-forge/pedantic.svg)](https://anaconda.org/conda-forge/pedantic) [![Last Commit](https://badgen.net/github/last-commit/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators) [![Stars](https://badgen.net/github/stars/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators) [![Open Issues](https://badgen.net/github/open-issues/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators/issues) [![Open PRs](https://badgen.net/github/open-prs/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators/pulls)

A collection of useful decorators in mixins for Python development. 

## [GenericMixin](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/generic_mixin.html)
Do you need a way to figure out to which type a type variable is bound?
With `GenericMixin` you can do exactly this:
```python
from pedantic import GenericMixin

class Foo[T, U](GenericMixin):
    values: list[T]
    value: U

f = Foo[str, int]()
print(f.type_vars)  # {T: <class 'str'>, U: <class 'int'>}
```

## [@frozen_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/frozen_dataclass.html)
With `@frozen_dataclass` you can create immutable data classes with provides a `copy_with()` instance method.
So you can write
```python
from pedantic import frozen_dataclass

@frozen_dataclass
class Foo:
    a: int
    b: str

foo = Foo(a=6, b='hi')
bar = foo.copy_with(a=42)
```
instead of 
```python
from dataclasses import dataclass, replace
@dataclass(frozen=True)
class Foo:
    a: int
    b: str

foo = Foo(a=6, b='hi')
bar = replace(foo, a=42)
```
You also can enfore run-time type checks for you dataclasses with `@frozen_dataclass(type_safe=True)`.

## [@in_subprocess](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/in_subprocess.html)
If you have an asynchronous service, that should perform some long-running calculation without blocking the event loop to keep the service responsive, you can use `@in_subprocess` to run the calculation in a separate process.
```python
import time
from pedantic import in_subprocess

@in_subprocess
def f() -> int:
    time.sleep(10)  # a long-taking synchronous operation, e.g., a calculation
    return 42

await f() == 42  # calculation is done in a separate process => event loop is not blocked
```

## [WithDecoratedMethods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/with_decorated_methods.html)
You want to register instance methods of a class as callbacks with a decorator? Easy!
```python
from pedantic import DecoratorType, create_decorator, WithDecoratedMethods

class Decorators(DecoratorType):
    ON_SUBJECT = 'on_subject'

on_subject = create_decorator(decorator_type=Decorators.ON_SUBJECT)

class MyClass(WithDecoratedMethods[Decorators]):
    message_broker_client = None
    
    @on_subject("msg_received")
    def on_new_message(self, msg) -> None:
        print(msg)

    def subscribe(self) -> None:
        to_subscribe = self.get_decorated_functions()[Decorators.ON_SUBJECT]
        
        for callback, subject in to_subscribe.items():
            self.message_broker_client.subscribe(subject=subject, on_new_message=callback)        
```

## [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/pedantic_decorator.html)
The `@pedantic` decorator enforces type annotations and check that passed arguments and returned values match those type annotations.

```python
from pedantic import pedantic

@pedantic
class MyClass:
    def print(self, s: str) -> None: pass

m = MyClass()
m.calc(b=42)
m.print(s='Hi')
m.calc(s=45.0)  # raises PedanticTypeCheckException
```

Since this is type checking at runtime, it might be slow. So it is recommended to use it only in development mode.
This is also **not** compatible with compiled source code (e.g., with [Nuitka](https://github.com/Nuitka/Nuitka)).

## [@validate](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/validate/validate.html)
This is an alternative to the [flask-request-validator](https://github.com/d-ganchar/flask_request_validator) that allows you to make parsing arguments from requests and validate them easy.
```python
from flask import Flask, Response, jsonify

from pedantic import (
    FlaskJsonParameter,
    NotEmpty,
    ParameterException,
    ReturnAs,
    TooManyArguments,
    validate,
)

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
def different_types(  # noqa: PLR0913
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
def handle_parameter_exception(exception: ParameterException) -> Response:
    response = jsonify(exception.to_dict)
    response.status_code = 422
    return response


@app.errorhandler(TooManyArguments)
def handle_too_many_arguments(exception: TooManyArguments) -> Response:
    response = jsonify(str(exception))
    response.status_code = 400
    return response

```
And it is not only for `flask`! The implementation is fully generic.

## Content of the package
### Decorators
- [@deprecated](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/deprecated.html)
- [@frozen_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/frozen_dataclass.html#pedantic.decorators.frozen_dataclass.frozen_dataclass)
- [@frozen_type_safe_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/frozen_dataclass.html#pedantic.decorators.frozen_dataclass.frozen_type_safe_dataclass)
- [@in_subprocess](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/in_subprocess.html)
- [@overrides](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/overrides.html)
- [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/pedantic_decorator.html)
- [@retry](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/retry.html)
- [@safe_async_contextmanager](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/safe_context_manager.html#pedantic.decorators.safe_context_manager.safe_async_contextmanager)
- [@safe_contextmanager](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/safe_context_manager.html#pedantic.decorators.safe_context_manager.safe_contextmanager)
- [@trace](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/trace.html)
- [@validate](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/validate/validate.html)

### Mixins
- [GenericMixin](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/generic_mixin.html)
- [WithDecoratedMethods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/with_decorated_methods.html)

### Helper Functions
- [decorate_class()]()
- [run_doctest_of_single_function()]()

## Contributing
This project is based on [poetry](https://python-poetry.org/) and [taskfile](https://taskfile.dev).
**Tip:** Run `task validate` before making commits.
