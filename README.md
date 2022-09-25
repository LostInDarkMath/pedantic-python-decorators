# pedantic-python-decorators [![Build Status](https://travis-ci.com/LostInDarkMath/pedantic-python-decorators.svg?branch=master)](https://travis-ci.com/LostInDarkMath/pedantic-python-decorators)  [![Coverage Status](https://coveralls.io/repos/github/LostInDarkMath/pedantic-python-decorators/badge.svg?branch=master)](https://coveralls.io/github/LostInDarkMath/pedantic-python-decorators?branch=master) [![PyPI version](https://badge.fury.io/py/pedantic.svg)](https://badge.fury.io/py/pedantic)
This packages includes many decorators that will make you write cleaner Python code. 

## Getting Started
This package requires Python 3.7 or later.
Python 3.6 is only supported by `pedantic` 1.9.1 or lower.
There are multiple options for installing this package.

### Option 1: Installing with pip from [Pypi](https://pypi.org/)
Run `pip install pedantic`.

### Option 2: Installing with pip and git
1. Install [Git](https://git-scm.com/downloads) if you don't have it already.
2. Run `pip install git+https://github.com/LostInDarkMath/pedantic-python-decorators.git@master`

### Option 3: Offline installation using wheel
1. Download the [latest release here](https://github.com/LostInDarkMath/PythonHelpers/releases/latest) by clicking on `pedantic-python-decorators-x.y.z-py-none-any.whl`.
2. Execute `pip install pedantic-python-decorators-x.y.z-py3-none-any.whl`.

## The [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.pedantic) decorator - Type checking at runtime
The `@pedantic` decorator does the following things:
- The decorated function can only be called by using keyword arguments. Positional arguments are not accepted.
- The decorated function must have [type annotations](https://docs.python.org/3/library/typing.html).
- Each time the decorated function is called, pedantic checks that the passed arguments and the return value of the function matches the given type annotations. 
As a consequence, the arguments are also checked for `None`, because `None` is only a valid argument, if it is annotated via `typing.Optional`.
- If the decorated function has a docstring which lists the arguments, the docstring is parsed and compared with the type annotations. In other words, pedantic ensures that the docstring is everytime up-to-date.
Currently, only docstrings in the [Google style](https://google.github.io/styleguide/pyguide.html) are supported. **Note:** you need install the [docstring-parser](https://github.com/rr-/docstring_parser) to make this work. 

In a nutshell:
`@pedantic` raises an `PedanticException` if one of the following happened:
- The decorated function is called with positional arguments.
- The function has no type annotation for their return type or one or more parameters do not have type annotations.
- A type annotation is incorrect.
- A type annotation misses type arguments, e.g. `typing.List` instead of `typing.List[int]`.
- The documented arguments do not match the argument list or their type annotations.

### Minimal example
```python
from typing import Union, List
from pedantic import pedantic, pedantic_class

@pedantic
def get_sum_of(values: List[Union[int, float]]) -> Union[int, float]:
    return sum(values)

@pedantic_class
class MyClass:
    def __init__(self, x: float, y: int) -> None:
        self.x = x
        self.y = y

    def print_sum(self) -> None:
        print(get_sum_of(values=[self.x, self.y]))

m = MyClass(x=3.14, y=2)
m.print_sum()
```


## The [@validate]() decorator
As the name suggests, with `@validate` you are able to validate the values that are passed to the decorated function.
That is done in a highly customizable way. 
But the highest benefit of this decorator is that it makes it extremely easy to write decoupled easy testable, maintainable and scalable code.
The following example shows the decoupled implementation of a configurable algorithm with the help of `@validate`:
```python
import os
from dataclasses import dataclass

from pedantic import validate, ExternalParameter, overrides, Validator, Parameter, Min, ReturnAs


@dataclass(frozen=True)
class Configuration:
    iterations: int
    max_error: float


class ConfigurationValidator(Validator):
    @overrides(Validator)
    def validate(self, value: Configuration) -> Configuration:
        if value.iterations < 1 or value.max_error < 0:
            self.raise_exception(msg=f'Invalid configuration: {value}', value=value)

        return value


class ConfigFromEnvVar(ExternalParameter):
    """ Reads the configuration from environment variables. """

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return 'iterations' in os.environ and 'max_error' in os.environ

    @overrides(ExternalParameter)
    def load_value(self) -> Configuration:
        return Configuration(
            iterations=int(os.environ['iterations']),
            max_error=float(os.environ['max_error']),
        )


class ConfigFromFile(ExternalParameter):
    """ Reads the configuration from a config file. """

    @overrides(ExternalParameter)
    def has_value(self) -> bool:
        return os.path.isfile('config.csv')

    @overrides(ExternalParameter)
    def load_value(self) -> Configuration:
        with open(file='config.csv', mode='r') as file:
            content = file.readlines()
            return Configuration(
                iterations=int(content[0].strip('\n')),
                max_error=float(content[1]),
            )


# choose your configuration source here:
@validate(ConfigFromEnvVar(name='config', validators=[ConfigurationValidator()]), strict=False, return_as=ReturnAs.KWARGS_WITH_NONE)
# @validate(ConfigFromFile(name='config', validators=[ConfigurationValidator()]), strict=False)

# with strict_mode = True (which is the default)
# you need to pass a Parameter for each parameter of the decorated function
# @validate(
#     Parameter(name='value', validators=[Min(5, include_boundary=False)]),
#     ConfigFromFile(name='config', validators=[ConfigurationValidator()]),
# )
def my_algorithm(value: float, config: Configuration) -> float:
    """
        This method calculates something that depends on the given value with considering the configuration.
        Note how well this small piece of code is designed:
            - Fhe function my_algorithm() need a Configuration but has no knowledge where this come from.
            - Furthermore, it need does not care about parameter validation.
            - The ConfigurationValidator doesn't now anything about the creation of the data.
            - The @validate decorator is the only you need to change, if you want a different configuration source.
    """
    print(value)
    print(config)
    return value


if __name__ == '__main__':
    # we can call the function with a config like there is no decorator.
    # This makes testing extremely easy: no config files, no environment variables or stuff like that
    print(my_algorithm(value=2, config=Configuration(iterations=3, max_error=4.4)))

    os.environ['iterations'] = '12'
    os.environ['max_error'] = '3.1415'

    # but we also can omit the config and load it implicitly by our custom Parameters
    print(my_algorithm(value=42.0))
```

## List of all decorators in this package
- [@count_calls](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_count_calls.html)
- [@deprecated](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_deprecated.html)
- [@does_same_as_function](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_does_same_as_function.html)
- [@frozen_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/cls_deco_frozen_dataclass.html#pedantic.decorators.cls_deco_frozen_dataclass.frozen_dataclass)
- [@frozen_type_safe_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/cls_deco_frozen_dataclass.html#pedantic.decorators.cls_deco_frozen_dataclass.frozen_type_safe_dataclass)
- [@for_all_methods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.for_all_methods)
- [@mock](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_mock.html)
- [@overrides](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_overrides.html)
- [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_pedantic.html#pedantic.decorators.fn_deco_pedantic.pedantic)
- [@pedantic_require_docstring](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_pedantic.html#pedantic.decorators.fn_deco_pedantic.pedantic_require_docstring)
- [@pedantic_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.pedantic_class)
- [@pedantic_class_require_docstring](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.pedantic_class_require_docstring)
- [@rename_kwargs](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_rename_kwargs.html)
- [@require_kwargs](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_require_kwargs.html)
- [@timer](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_timer.html)
- [@timer_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.timer_class)
- [@trace](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_trace.html)
- [@trace_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.trace_class)
- [@trace_if_returns](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_trace_if_returns.html)
- [@unimplemented](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_unimplemented.html)
- [@validate](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_validate/fn_deco_validate.html)

## Dependencies
There are no hard dependencies. But if you want to use some advanced features you need to install the following packages:
- [Docstring-Parser](https://github.com/rr-/docstring_parser) if you need to verify your docstrings.
- [flask](https://pypi.org/project/Flask/) if want to you the request validators which are designed for `Flask` (see unit tests for examples): 
  - `FlaskParameter` (abstract class)
  - `FlaskJsonParameter`
  - `FlaskFormParameter`
  - `FlaskPathParameter`
  - `FlaskGetParameter`
  - `FlaskHeaderParameter`
  - `GenericFlaskDeserializer`

## Contributing
Feel free to contribute by submitting a pull request :)

## Acknowledgments
* [Rathaustreppe](https://github.com/rathaustreppe)
* [Aran-Fey](https://stackoverflow.com/questions/55503673/how-do-i-check-if-a-value-matches-a-type-in-python/55504010#55504010)
* [user395760](https://stackoverflow.com/questions/55503673/how-do-i-check-if-a-value-matches-a-type-in-python/55504010#55504010)

## Risks and side effects
The usage of decorators may affect the performance of your application. 
For this reason, I would highly recommend you to disable the decorators if your code runs in a productive environment.
You can disable `pedantic` by set an environment variable:
```
export ENABLE_PEDANTIC=0
```
You can also disable or enable the environment variables in your project by calling a method:
```python
from pedantic import enable_pedantic, disable_pedantic
enable_pedantic()
```

## Issues with compiled Python code
This package is **not** compatible with compiled source code (e.g. with [Nuitka](https://github.com/Nuitka/Nuitka)).
That's because it uses the `inspect` module from the standard library which will raise errors like `OSError: could not get source code` in case of compiled source code.


Don't forget to check out the [documentation](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic).
Happy coding!
