from collections.abc import Generator, Iterable, Iterator
from typing import Any, TypeVar

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.type_checking_logic.check_types import assert_value_matches_type, get_base_generic, get_type_arguments


class GeneratorWrapper:
    """A wrapper around a generators that handles type checking."""

    def __init__(self, wrapped: Generator, expected_type: Any, err_msg: str, type_vars: dict[TypeVar, Any]) -> None:  # noqa: D107
        self._generator = wrapped
        self._err = err_msg
        self._yield_type = None
        self._send_type = None
        self._return_type = None
        self._type_vars = type_vars
        self._initialized = False

        self._set_and_check_return_types(expected_return_type=expected_type)

    def __iter__(self) -> 'GeneratorWrapper':
        return self

    def __next__(self) -> Any:
        return self.send(obj=None)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._generator, name)

    def throw(self, *args: Any) -> Any:
        """Raise an exception in the generator."""
        return self._generator.throw(*args)

    def close(self) -> None:
        """Close the generator."""
        self._generator.close()

    def send(self, obj: Any) -> Any:
        """Send a value into the generator and check types."""

        if self._initialized:
            assert_value_matches_type(value=obj, type_=self._send_type, type_vars=self._type_vars, err=self._err)
        else:
            self._initialized = True

        try:
            returned_value = self._generator.send(obj)
        except StopIteration as ex:
            assert_value_matches_type(value=ex.value,
                                      type_=self._return_type,
                                      type_vars=self._type_vars,
                                      err=self._err)
            raise

        assert_value_matches_type(value=returned_value,
                                  type_=self._yield_type,
                                  type_vars=self._type_vars,
                                  err=self._err)
        return returned_value

    def _set_and_check_return_types(self, expected_return_type: Any) -> Any:
        base_generic = get_base_generic(cls=expected_return_type)

        if base_generic not in [Generator, Iterable, Iterator]:
            raise PedanticTypeCheckException(
                f'{self._err}Generator should have type annotation "typing.Generator[]", "typing.Iterator[]" or '
                f'"typing.Iterable[]". Got "{expected_return_type}" instead.')

        result = get_type_arguments(expected_return_type)

        if len(result) == 1:
            self._yield_type = result[0]
        elif len(result) == 3:  # noqa: PLR2004
            self._yield_type = result[0]
            self._send_type = result[1]
            self._return_type = result[2]
        else:
            raise PedanticTypeCheckException(f'{self._err}Generator should have a type argument. Got: {result}')
        return result[0]
