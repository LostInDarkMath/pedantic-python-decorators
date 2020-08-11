# pedantic-python-decorators [![Build Status](https://travis-ci.com/LostInDarkMath/PythonHelpers.svg?branch=master)](https://travis-ci.com/LostInDarkMath/PythonHelpers) [![Coverage Status](https://coveralls.io/repos/github/LostInDarkMath/pedantic-python-decorators/badge.svg?branch=master)](https://coveralls.io/github/LostInDarkMath/pedantic-python-decorators?branch=master)
Some useful decorators which I use in almost every python project.
These decorators will make you write cleaner and well-documented Python code.

## The powerful decorators
### @pedantic
The `@pedantic` decorator does the following things:
- The decorated function can only be called by using keyword arguments. Positional arguments are not accepted. Normally, the following snippets are valid Python code, but `@pedantic` there aren't valid any longer:
  ```python
  @pedantic
  def do(s: str, a: float: b: int) -> List[str]:
    return [s, str(a + b)]

  do('hi', 3.14, 4)  # error! Correct would be: do(s=hi', a=3.14, b=4)
  ```
- The decorated function must have [Type annotations](https://docs.python.org/3/library/typing.html). If some type hints are missing, an `AssertionError` is thrown. Examples:
  ```python
  @pedantic
  def foo():    # will raise an error. Correct would be: def foo() -> None:
    print'bar'

  @pedantic
  def foo2(s): # will raise an error. Correct would be: def foo(s: str) -> None:
    print(s)
  ```
- The decorator parses the type annotations and each time the function is called, is checks, the argument matches the type annotations, before the function is executed and that the return value matches the corresponding return type annotation. As a consquence, the arguments are also checked for `None`, because `None` is only a valid argument, if it is annoted via `Optional[str]` or equivalently `Union[str, None]`. So the following examples will cause `@pedantic` to raise an error:
    ```python
    @pedantic
    def do(s: str, a: float: b: int) -> List[str]:
        return [s, str(a + b)]

    do(s=None, a=3.14, b=4)     # will raise an error. None is not a string.
    de(s='None', a=3.14, b=4.0) # will raise an error: 4.0 is not an int.

    @pedantic
    def do2(s: str, a: float: b: int) -> List[str]:
        return [s, a + b]  # will raise an error: Expected List[str], but a + b is a float
    ```
- If the decorated function has a docstring, that lists the arguments, the docstring is parsed and compared with the type hints. Because the type hints are checked at runtime, the docstring is also checked at runtime. It is checked, that the type annotations matches exactly the arguments, types and return values in the docstring. Currently, only docstrings in the [Google Format](https://google.github.io/styleguide/pyguide.html) are supported.
`@pedantic` raises an `AssertionError` if one of the following happend:
  - Not all arguments the function are documented in the docstring.
  - There are arguments documented in the doc string, that are not taken by the function.
  - The return value is not documented.
  - A return value is documented, but the function does not return anything.
  - The type annotations in function don't match the documented types in the docstring.

### @pedantic_require_docstring
It's like `@pedantic`, but it additionally forces developers to create docstrings. It raises an `AssertionError`, if there is no docstring.

### @pedantic_class
The `pedantic` decorator is only for methods. But the `@pedantic_class` decorator is it's counterpart for classes. That means by only changing one line of code you can make your class pedantic:
```python
@pedantic_class
class MyClass:
    def __init__(self, a: int) -> None:
        self.a = a

    def calc(self, b: int) -> int:
        return self.a - b

    def print(self, s: str) -> None:
        print(f'{self.a} and {s}')

m = MyClass(a=5)
m.calc(b=42)
m.print(s='Hi')
```

### @validate_args
With the `@validate_args` decorator you can do contract checking *outside* of functions. Just pass a validator in, for example:
```python
@validate_args(lambda x: (x > 42, f'Each arg should be > 42, but it was {x}.'))
def some_calculation(a, b, c):
    return a + b + c

some_calculation(30, 40, 50)  # this leads to an error
some_calculation(43, 45, 50)  # this is okay
```
There are some shortcuts included for often used validations:
- `@require_not_none` ensures that each argument is not `None`
- `@require_not_empty_strings` ensures that each passed argument is a non_empty string, so passind `"   "` will raise an `AssertionError`.

## The small decorators:
### @overrides
```python
from pedantic.method_decorators import overrides


class Parent:
    def instance_method(self):
        pass


class Child(Parent):
    @overrides(Parent)
    def instance_method(self):
        print('hi')
```
Together with the [Abstract Base Class](https://docs.python.org/3/library/abc.html) from the standard library, you can write things like that:

```python
from abc import ABC, abstractmethod
from pedantic.method_decorators import overrides


class Parent(ABC):

    @abstractmethod
    def instance_method(self):
        pass


class Child(Parent):

    @overrides(Parent)
    def instance_method(self):
        print('hi')
```

### @deprecated
This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted when the function is used.
```python
@deprecated
def oudated_calculation():
    # perform some stuff
```

### @unimplemented
For documentation purposes. Throw `NotImplementedException` if the function is called.
```python
@unimplemented
def new_operation():
    pass
```

### @needs_refactoring
Of course, you refactor immediately if you see something ugly.
However, if you don't have the time for a big refactoring use this decorator at least.
A warning is raised everytime the decorated function is called.
```python
@needs_refactoring
def almost_messy_operation():
    pass
```

### @dirty
A decorator for preventing from execution and therefore from causing damage.
If the function gets called, a `TooDirtyException` is raised.
```python
@dirty
def messy_operation():
    # messy code goes here
```

### @require_kwargs
Checks that each passed argument is a keyword argument and raises an `AssertionError` if any positional arguments are passed.
```python
@require_kwargs
    def some_calculation(a, b, c):
        return a + b + c
some_calculation(5, 4, 3)       # this will lead to an AssertionError
some_calculation(a=5, b=4, c=3) # this is okay
```

### @timer
Prints out how long the execution of the function takes in seconds.
```python
@timer
def some_calculation():
    # perform possible long taking calculation here
```

### @count_calls
Prints how often the method is called during program execution.
```python
@count_calls
def some_calculation():
    print('hello world')
```

### @trace
Prints the passed arguments and the return value on each function call.
```python
@trace
def some_calculation(a, b):
    return a + b
```

# Installation guide
## Option 1: installing with pip from [Pypi](https://pypi.org/)
Run `pip install pedantic`.

## Option 2: Installing with pip and git
0. Install [Git](https://git-scm.com/downloads) if you don't have it already.
1. Run `pip install git+https://github.com/LostInDarkMath/pedantic-python-decorators.git@master`
2. In your Python file write `from pedantic import pedantic, pedantic_class` or whatever decorator you want to use.
3. Use it like mentioned above. Happy coding!

## Option 3:Offline installation using wheel
1. Download the [latest release here](https://github.com/LostInDarkMath/PythonHelpers/releases/latest) by clicking on `pedantic-python-decorators-x.y.z-py-none-any.whl`.
2. Execute `pip install pedantic-python-decorators-x.y.z-py3-none-any.whl` where `x.y.z` needs to be the correct version.

# Dependencies
Outside the Python standard library, the followings dependencies are used:
- [Docstring-Parser](https://github.com/rr-/docstring_parser) (Version 0.7.2, requires Python 3.6)

Created with Python 3.8.5. [It works with Python 3.6 or newer.](https://travis-ci.com/github/LostInDarkMath/PythonHelpers)

# Risks and Side Effects
The usage of decorators may affect the performance of your application. For this reason, it would highly recommend you to disable the decorators during deployment. Best practice would be to integrate this in a automated depoly chain:
```
[CI runs tests] => [Remove decorators] => [deploy cleaned code]
```
