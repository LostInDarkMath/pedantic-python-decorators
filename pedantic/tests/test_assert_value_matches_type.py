import sys
import unittest
from abc import ABC
from dataclasses import dataclass
from typing import Callable, Awaitable, Coroutine, Any, Union, Optional, Generic, TypeVar

from pedantic.exceptions import PedanticTypeCheckException
from pedantic.type_checking_logic.check_types import assert_value_matches_type


@dataclass
class Foo:
    value: int


class TestAssertValueMatchesType(unittest.TestCase):
    def test_callable(self):
        def _cb(foo: Foo) -> str:
            return str(foo.value)

        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., str],
            err='',
            type_vars={},
        )

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., int],
                err='',
                type_vars={},
            )

    def test_callable_return_type_none(self):
        def _cb(foo: Foo) -> None:
            return print(foo)

        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., None],
            err='',
            type_vars={},
        )

    def test_callable_awaitable(self):
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

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., Awaitable[int]],
                err='',
                type_vars={},
            )

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., str],
                err='',
                type_vars={},
            )

    def test_callable_coroutine(self):
        async def _cb(foo: Foo) -> str:
            return str(foo.value)

        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Coroutine[None, None, str]],
            err='',
            type_vars={},
        )

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., Coroutine[None, None, int]],
                err='',
                type_vars={},
            )

    def test_callable_awaitable_with_none_return_type(self):
        async def _cb(foo: Foo) -> None:
            print(foo)

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

    def test_callable_with_old_union_type_hint(self):
        async def _cb(machine_id: str) -> Union[int, None]:
            return 42

        assert_value_matches_type(
            value=_cb,
            type_=Callable[..., Awaitable[Union[int, None]]],
            err='',
            type_vars={},
        )

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., Awaitable[int]],
                err='',
                type_vars={},
            )

    def test_callable_with_new_union_type_hint(self):
        if sys.version_info < (3, 10):
            return

        async def _cb(machine_id: str) -> int | None:
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

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            assert_value_matches_type(
                value=_cb,
                type_=Callable[..., Awaitable[int]],
                err='',
                type_vars={},
            )

    def test_forward_ref_inheritance(self):
        T = TypeVar('T')

        class State(Generic[T], ABC):
            pass

        class StateMachine(Generic[T], ABC):
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
