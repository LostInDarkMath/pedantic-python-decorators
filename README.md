# pedantic-python-decorators [![Coverage Status](https://coveralls.io/repos/github/LostInDarkMath/pedantic-python-decorators/badge.svg?branch=master)](https://coveralls.io/github/LostInDarkMath/pedantic-python-decorators?branch=master) [![PyPI version](https://badge.fury.io/py/pedantic.svg)](https://badge.fury.io/py/pedantic) [![Conda Version](https://img.shields.io/conda/vn/conda-forge/pedantic.svg)](https://anaconda.org/conda-forge/pedantic) [![Last Commit](https://badgen.net/github/last-commit/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators) [![Stars](https://badgen.net/github/stars/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators) [![Open Issues](https://badgen.net/github/open-issues/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators/issues) [![Open PRs](https://badgen.net/github/open-prs/LostInDarkMath/pedantic-python-decorators?color=green)](https://GitHub.com/LostInDarkMath/pedantic-python-decorators/pulls)

This packages includes many decorators that will make you write cleaner Python code. 

## The [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.pedantic) decorator - Type checking at runtime
The `@pedantic` decorator does the following things:
- The decorated function can only be called by using keyword arguments. Positional arguments are not accepted.
- The decorated function must have [type annotations](https://docs.python.org/3/library/typing.html).
- Each time the decorated function is called, pedantic checks that the passed arguments and the return value of the function matches the given type annotations. 
As a consequence, the arguments are also checked for `None`, because `None` is only a valid argument, if it is annotated via `typing.Optional`.

In a nutshell:
`@pedantic` raises an `PedanticException` if one of the following happened:
- The decorated function is called with positional arguments.
- The function has no type annotation for their return type or one or more parameters do not have type annotations.
- A type annotation is incorrect.
- A type annotation misses type arguments, e.g. `typing.List` instead of `typing.List[int]`.

### Minimal example
```python
from pedantic import pedantic


@pedantic
def get_sum_of(values: list[int | float]) -> int:
    return sum(values)

get_sum_of(values=[0, 1.2, 3, 5.4])  # this raises the following runtime error: 
# Type hint of return value is incorrect: Expected type <class 'int'> but 10.0 of type <class 'float'> was the return value which does not match.
```


## The [@validate]() decorator
As the name suggests, with `@validate` you are able to validate the values that are passed to the decorated function.

## List of all decorators in this package
- [@deprecated](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_deprecated.html)
- [@frozen_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/cls_deco_frozen_dataclass.html#pedantic.decorators.cls_deco_frozen_dataclass.frozen_dataclass)
- [@frozen_type_safe_dataclass](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/cls_deco_frozen_dataclass.html#pedantic.decorators.cls_deco_frozen_dataclass.frozen_type_safe_dataclass)
- [@for_all_methods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.for_all_methods)
- [@in_subprocess](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_in_subprocess.html)
- [@overrides](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_overrides.html)
- [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_pedantic.html#pedantic.decorators.fn_deco_pedantic.pedantic)
- [@pedantic_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.pedantic_class)
- [@require_kwargs](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_require_kwargs.html)
- [@retry](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_retry.html)
- [@trace](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_trace.html)
- [@trace_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/class_decorators.html#pedantic.decorators.class_decorators.trace_class)
- [@trace_if_returns](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_trace_if_returns.html)
- [@validate](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/decorators/fn_deco_validate/fn_deco_validate.html)

## List of all mixins in this package
- [GenericMixin](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/generic_mixin.html)
- [WithDecoratedMethods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/mixins/with_decorated_methods.html)

## Dependencies
There are no hard dependencies. But if you want to use some advanced features you need to install the following packages:
- [multiprocess](https://github.com/uqfoundation/multiprocess) if you want to use the `@in_subprocess` decorator
- [flask](https://pypi.org/project/Flask/) if you want to you the request validators which are designed for `Flask` (see unit tests for examples): 
  - `FlaskParameter` (abstract class)
  - `FlaskJsonParameter`
  - `FlaskFormParameter`
  - `FlaskPathParameter`
  - `FlaskGetParameter`
  - `FlaskHeaderParameter`
  - `GenericFlaskDeserializer`

## Contributing
This project is based on [poetry](https://python-poetry.org/) and [taskfile](https://taskfile.dev).
**Tip:** Run `task validate` before making commits.

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
