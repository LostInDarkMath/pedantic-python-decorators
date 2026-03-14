# ruff: noqa: UP006, UP007, UP035

from abc import ABC
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable, Coroutine, Generic, Optional, Tuple, TypeVar, Union

import pytest

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.type_checking_logic.check_types import assert_value_matches_type


@dataclass
class Foo:
    value: int


def test_callable():
    def _cb(foo: Foo) -> str:
        return str(foo.value)

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., str],
        err='',
        type_vars={},
    )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., int],
            err='',
            type_vars={},
        )

def test_callable_return_type_none():
    def _cb(_: Foo) -> None:
        return

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., None],
        err='',
        type_vars={},
    )

def test_callable_awaitable():
    async def _cb(foo: Foo) -> str:
        return str(foo.value)

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[str]],
        err='',
        type_vars={},
    )

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[Any]],
        err='',
        type_vars={},
    )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Awaitable[int]],
            err='',
            type_vars={},
        )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., str],
            err='',
            type_vars={},
        )


def test_callable_coroutine():
    async def _cb(foo: Foo) -> str:
        return str(foo.value)

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Coroutine[None, None, str]],
        err='',
        type_vars={},
    )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Coroutine[None, None, int]],
            err='',
            type_vars={},
        )


def test_callable_awaitable_with_none_return_type():
    async def _cb(foo: Foo) -> None: pass

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[None]],
        err='',
        type_vars={},
    )

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[Any]],
        err='',
        type_vars={},
    )


def test_callable_with_old_union_type_hint():
    async def _cb(_: str) -> Union[int, None]:
        return 42

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[Union[int, None]]],
        err='',
        type_vars={},
    )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Awaitable[int]],
            err='',
            type_vars={},
        )


def test_callable_with_new_union_type_hint():
    async def _cb(_: str) -> int | None:
        return 42

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[int | None]],
        err='',
        type_vars={},
    )

    assert_value_matches_type(
        value=_cb,
        type_=Callable[..., Awaitable[Any]],
        err='',
        type_vars={},
    )

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Awaitable[int]],
            err='',
            type_vars={},
        )


def test_forward_ref_inheritance():
    T = TypeVar('T')

    class State(ABC, Generic[T]):
        pass

    class StateMachine(ABC, Generic[T]):
        pass

    class MachineState(State['MachineStateMachine']):
        pass

    class OfflineMachineState(MachineState):
        pass

    class MachineStateMachine(StateMachine[MachineState]):
        pass

    assert_value_matches_type(
        value=OfflineMachineState(),
        type_=Optional['MachineState'],
        err='',
        type_vars={},
        context=locals(),
    )


def test_tuple_with_ellipsis():
    """Regression test for https://github.com/LostInDarkMath/pedantic-python-decorators/issues/75"""

    assert_value_matches_type(
        value=(1, 2.0, 'hello'),
        type_=Tuple[Any, ...],
        err='',
        type_vars={},
        context=locals(),
    )


def test_union_of_callable():
    """Regression test for https://github.com/LostInDarkMath/pedantic-python-decorators/issues/74"""

    assert_value_matches_type(
        value=datetime.now(tz=UTC),
        type_=Union[datetime, Callable[[], datetime]],
        err='',
        type_vars={},
        context=locals(),
    )
