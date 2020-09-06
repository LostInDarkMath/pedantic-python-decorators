# pedantic-python-decorators [![Build Status](https://travis-ci.com/LostInDarkMath/pedantic-python-decorators.svg?branch=master)](https://travis-ci.com/LostInDarkMath/pedantic-python-decorators)  [![Coverage Status](https://coveralls.io/repos/github/LostInDarkMath/pedantic-python-decorators/badge.svg?branch=master)](https://coveralls.io/github/LostInDarkMath/pedantic-python-decorators?branch=master) [![PyPI version](https://badge.fury.io/py/pedantic.svg)](https://badge.fury.io/py/pedantic)
These decorators will make you write cleaner and well-documented Python code. 

## Getting Started
There are multiple options for installing this package.

### Option 1: Installing with pip from [Pypi](https://pypi.org/)
Run `pip install pedantic`.

### Option 2: Installing with pip and git
1. Install [Git](https://git-scm.com/downloads) if you don't have it already.
2. Run `pip install git+https://github.com/LostInDarkMath/pedantic-python-decorators.git@master`

### Option 3: Offline installation using wheel
1. Download the [latest release here](https://github.com/LostInDarkMath/PythonHelpers/releases/latest) by clicking on `pedantic-python-decorators-x.y.z-py-none-any.whl`.
2. Execute `pip install pedantic-python-decorators-x.y.z-py3-none-any.whl`.

### Usage
Use `from pedantic import pedantic, pedantic_class` to import the pedantic decorators for example. Of course you could import whatever decorator you want to use as well.
Don't forget to check out the [documentation](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic).
Happy coding!

## Dependencies
Outside the Python standard library, the following dependencies are used:
- [Docstring-Parser](https://github.com/rr-/docstring_parser) (Version 0.7.2, requires Python 3.6 or later)

[This package works with Python 3.6 or newer.](https://travis-ci.com/github/LostInDarkMath/PythonHelpers)

## Risks and Side Effects
The usage of decorators may affect the performance of your application. For this reason, it would highly recommend you to disable the decorators during deployment automatically after all tests are passed.

## Contributing
Feel free to contribute by submitting a pull request :)

## Acknowledgments
* [Rathaustreppe](https://github.com/rathaustreppe)
* [Aran-Fey](https://stackoverflow.com/questions/55503673/how-do-i-check-if-a-value-matches-a-type-in-python/55504010#55504010)
* [user395760](https://stackoverflow.com/questions/55503673/how-do-i-check-if-a-value-matches-a-type-in-python/55504010#55504010)

## List of all decorators in this package
- [@count_calls](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.count_calls)
- [@deprecated](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.deprecated)
- [@dirty](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.dirty)
- [@does_same_as_function](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.does_same_as_function)
- [@for_all_methods](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/class_decorators.html#pedantic.class_decorators.for_all_methods)
- [@needs_refactoring](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.needs_refactoring)
- [@overrides](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.overrides)
- [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.pedantic)
- [@pedantic_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/class_decorators.html#pedantic.class_decorators.pedantic_class)
- [@pedantic_class_require_docstring](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/class_decorators.html#pedantic.class_decorators.pedantic_class_require_docstring)
- [@pedantic_require_docstring](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.pedantic_require_docstring)
- [@require_kwargs](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.require_kwargs)
- [@require_not_empty_strings](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.require_not_empty_strings)
- [@require_not_none](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.require_not_none)
- [@timer](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.timer)
- [@timer_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/class_decorators.html#pedantic.class_decorators.timer_class)
- [@trace](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.trace)
- [@trace_class](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/class_decorators.html#pedantic.class_decorators.trace_class)
- [@trace_if_returns](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.trace_if_returns)
- [@unimplemented](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.unimplemented)
- [@validate_args](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.validate_args)

## The [@pedantic](https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/method_decorators.html#pedantic.method_decorators.pedantic) decorator
The `@pedantic` decorator does the following things:
- The decorated function can only be called by using keyword arguments. Positional arguments are not accepted.
- The decorated function must have [Type annotations](https://docs.python.org/3/library/typing.html).
- Each time the decorated function is called, pedantic checks that the passed arguments and the return value of the function matches the given type annotations. 
As a consquence, the arguments are also checked for `None`, because `None` is only a valid argument, if it is annoted via `typing.Optional`.
- If the decorated function has a docstring which lists the arguments, the docstring is parsed and compared with the type annotations. In other words, pedantic ensures that the docstring is everytime up-to-date.
Currently, only docstrings in the [Google style](https://google.github.io/styleguide/pyguide.html) are supported.

In a nutshell:
`@pedantic` raises an `AssertionError` if one of the following happend:
- The decorated function is called with positional arguments.
- The function has no type annotation for their return type or one or more parameters do not have type annotations.
- A type annotation is incorrect.
- A type annotation misses type arguments, e.g. `typing.List` instead of `typing.List[int]`.
- The documented arguments do not match the argument list or their type annotations.
