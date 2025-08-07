# Changelog
## Pedantic 2.2.0
- migrated from `setup.py` to `pyproject.toml`

## Pedantic 2.1.11
- improve `GenericMixin` such that it also find bound type variables in parent classes

## Pedantic 2.1.10
- added type check support for `functools.partial`
- update dependencies

## Pedantic 2.1.9
- added Python 3.13 to CI

## Pedantic 2.1.8
- add more parameters to `transformation` in `create_decorator` to make it more flexible

## Pedantic 2.1.7
- add `transformation` parameter to `create_decorator` to make adding custom behavior easier

## Pedantic 2.1.6
- Remove `inspect.getsource()` call from `@overrides`

## Pedantic 2.1.5
- Close `multiprocess.connection.Connection` correctly in `@in_subprocess` decorator
- Updated dependencies
- added `retry_func()` function

## Pedantic 2.1.4
- improve implementation of `copy_with()`

## Pedantic 2.1.3
- bugfix `@pedantic` together with `typing.Protocol` 

## Pedantic 2.1.2
- bugfix `@pedantic` together with `typing.Protocol` 

## Pedantic 2.1.1
- make `@pedantic` work with `typing.Protocol` (at least do not raise a false-positive error)

## Pedantic 2.1.0
- add `retry` decorator
- update example in `README.md`

## Pedantic 2.0.2
- improve API of `WithDecoratedMethods.get_decorated_functions()` 

## Pedantic 2.0.1
- fix bug in `GenericMixin` that appears when using multiple inheritance 

## Pedantic 2.0.0
- add Mixin `WithDecoratedMethods` that makes it easy to find out which method is decorated with which specific parametrized decorator
- drop support for Python 3.9 and 3.10

## Pedantic 1.16.4
- fix `GenericMixin` bug that appears when using inheritance

## Pedantic 1.16.3
- improve error message for the case that you call `GenericMixin.type_var()` in the `__init__()` method.

## Pedantic 1.16.2
- [add conda-forge install instructions and version](https://github.com/LostInDarkMath/pedantic-python-decorators/pull/93)

## Pedantic 1.16.1
- bump `flask` and `werkzeug` to version `3.0.0`

## Pedantic 1.16.0
- allow type hints like `list[int], dict[str, float], ...`
- drop support for Python 3.8

## Pedantic 1.15.1
- [fix the `pedantic-x.y.z.tar.gz` file that is deployed to Pypi](https://github.com/LostInDarkMath/pedantic-python-decorators/issues/89)

## Pedantic 1.15.0
- added `@safe_contextmanager` and `@safe_async_contextmanager` decorators
- drop support for Python 3.7
- improve implementation of `@in_subprocess` decorator

## Pedantic 1.14.6
- [move Deserializable out of flask_parameters.py](https://github.com/LostInDarkMath/pedantic-python-decorators/issues/86)

## Pedantic 1.14.5
- fix issue that appears when using `slots=True` in the `frozen_dataclass` decorator

## Pedantic 1.14.4
- added release notes to GitHub releases (CI)

## Pedantic 1.14.3
- fix a typo in the docs [here](https://github.com/LostInDarkMath/pedantic-python-decorators/pull/79)

## Pedantic 1.14.2
- allow async functions for `@in_subprocess`
- use Pipe instead of Queue for subprocess communication

## Pedantic 1.14.1
- [Fix type checking bug with callables](https://github.com/LostInDarkMath/pedantic-python-decorators/issues/74)
- Fix deployment (CI)

## Pedantic 1.14.0
- Added support for Python 3.11:
  - `typing.Self`
  - `typing.Never`
  - `typing.LiteralString`
  - `typing.TypeVarTuple` is not supported yet, but it least it does not lead to errors ;)
- Fix type checking of `typing.NoReturn`
- Fix `@pedantic_class` behavior with `@classmethod`s
- Changed Ubuntu version in CI from 20 to 22
- Added arguments `slots` and `kw_only` to `frozen_dataclass`

## Pedantic 1.13.3
- [again: fixes a bug in the type-checking of `frozen_dataclass` and `frozen_type_safe_dataclass` in context of `ForwardRef`s](https://github.com/LostInDarkMath/pedantic-python-decorators/issues/72) 

## Pedantic 1.13.2
- [fixes a bug in the type-checking of `frozen_dataclass` and `frozen_type_safe_dataclass` in context of `ForwardRef`s](https://github.com/LostInDarkMath/pedantic-python-decorators/issues/72)

## Pedantic 1.13.1
- fix `ImportError` of optional `multiprocess` package
- fix typo in `README.md`
- added more test for `@in_subprocess` decorator
- improve resolving of `typing.ForwardRef`s

## Pedantic 1.13.0
- added `GenericMixin`
- added `@in_subprocess` decorator

## Pedantic 1.12.11
- bugfix in type checking logic 

## Pedantic 1.12.10
- fix tests

## Pedantic 1.12.9
- bugfix in type checking logic concerning `typing.Awaitable` and `typing.Coroutine` with return type `UnionType`

## Pedantic 1.12.8
- bugfix in type checking logic concerning `typing.Awaitable` and `typing.Coroutine` with return type `None`

## Pedantic 1.12.7
- fix test coverage

## Pedantic 1.12.6
- bugfix in type checking logic concerning `typing.Awaitable` and `typing.Coroutine`

## Pedantic 1.12.5
- fix type hints
- use `kw_only=True` in `frozen_dataclass` and `frozen_type_safe_dataclass`

## Pedantic 1.12.4
- fix inheritance bug in `frozen_dataclass` and `frozen_type_safe_dataclass`
- added more badges to `README.md`

## Pedantic 1.12.3
- Added method `deep_copy_with()` to dataclasses generated by `frozen_dataclass` and `frozen_type_safe_dataclass`
- Fix bug in `copy_with()` that occurred when using nested dataclasses

## Pedantic 1.12.2
- Added the `frozen_type_safe_dataclass` decorator
- Added parameters to `frozen_dataclass`:
  - `type_safe` with default `False`: If `True` it ensured that all fields have a value that matches the given data type at any time.
  - `order` with default `False`: If `True` the comparison methods are generated for the class.

## Pedantic 1.12.1
- Fix link in `README.md`
- update dependencies in `requirements.txt`
- fix some typos in docstrings and comments
- make some private methods public
- minor code cleanups

## Pedantic 1.12.0
- Add decorator `frozen_dataclass` which adds the methods `copy_with()` and `validate_types()` to the often used `dataclass(frozen=True)`. 

## Pedantic 1.11.4
- Added remarks to `README.md` concerning code compilation
- Exclude lines to fix test coverage

## Pedantic 1.11.3
- Fix `NameError: name 'Docstring' is not defined`
- Fix type hint of `raw_doc()`
- Fix `create_pdoc.sh`

## Pedantic 1.11.2
- Remove the dependency [docstring-parser](https://github.com/rr-/docstring_parser) dependency and make it optional

## Pedantic 1.11.1
- Bugfix in `IsUuid` validator: Now handle `None` and `int` values correctly.

## Pedantic 1.11.0
- Added `GenericDeserializer` and `Deserializable` as proposed in https://github.com/LostInDarkMath/pedantic-python-decorators/issues/55
- Added `validate_param()` instance method to `Validator`

## Pedantic 1.10.0
- **Breaking:** Drop support for Python 3.6.
- Make the `pedantic` decorator compatible with Python 3.10.
- Added changelog
- CI: drop Python 3.6 and add Python 3.10 and 3.11
