from abc import ABC
from dataclasses import dataclass, FrozenInstanceError
from typing import List, Dict, Set, Tuple, Awaitable, Callable, Generic, TypeVar, Optional

import pytest

from pedantic.decorators.cls_deco_frozen_dataclass import frozen_dataclass, frozen_type_safe_dataclass
from pedantic.exceptions import PedanticTypeCheckException


@frozen_dataclass
class Foo:
    a: int
    b: str
    c: bool


@frozen_type_safe_dataclass
class B:
    v: Set[int]


@frozen_type_safe_dataclass
class A:
    foo: List[int]
    bar: Dict[str, str]
    values: Tuple[B, B]


def test_equals_and_hash():
    a = Foo(a=6, b='hi', c=True)
    b = Foo(a=6, b='hi', c=True)
    c = Foo(a=7, b='hi', c=True)

    assert a == b
    assert hash(a) == hash(b)

    assert a != c
    assert hash(a) != hash(c)


def test_copy_with():
    foo = Foo(a=6, b='hi', c=True)

    copy_1 = foo.copy_with()
    assert foo == copy_1

    copy_2 = foo.copy_with(a=42)
    assert foo != copy_2
    assert copy_2.a == 42
    assert foo.b == copy_2.b
    assert foo.c == copy_2.c

    copy_3 = foo.copy_with(b='Hello')
    assert foo != copy_3
    assert foo.a == copy_3.a
    assert copy_3.b == 'Hello'
    assert copy_3.c == foo.c

    copy_4 = foo.copy_with(c=False)
    assert foo != copy_4
    assert foo.a == copy_4.a
    assert foo.b == copy_4.b
    assert copy_4.c is False

    copy_5 = foo.copy_with(a=676676, b='new', c=False)
    assert foo != copy_5
    assert copy_5.a == 676676
    assert copy_5.b == 'new'
    assert copy_5.c is False

def test_validate_types():
    foo = Foo(a=6, b='hi', c=True)
    foo.validate_types()

    bar = Foo(a=6.6, b='hi', c=True)

    with pytest.raises(expected_exception=PedanticTypeCheckException) as err:
        bar.validate_types()

    expected = 'In dataclass "Foo" in field "a": Type hint is incorrect: Argument 6.6 of type <class \'float\'> ' \
               'does not match expected type <class \'int\'>.'
    assert err.value.args[0] == expected


def test_frozen_dataclass_above_dataclass():
    # This is the same behavior like
    # >>> @dataclass(frozen=True)
    # ... @dataclass
    # ... class C:
    # ...     foo: int

    @frozen_dataclass
    @dataclass
    class A:
        foo: int

    with pytest.raises(expected_exception=TypeError):
        A()

    with pytest.raises(expected_exception=FrozenInstanceError):
        A(foo=3)


def test_frozen_dataclass_below_dataclass():
    @dataclass
    @frozen_dataclass
    class A:
        foo: int

    with pytest.raises(expected_exception=TypeError):
        A()

    a = A(foo=3)

    with pytest.raises(expected_exception=FrozenInstanceError):
        a.foo = 4

    b = a.copy_with(foo=4)
    assert b.foo == 4


def test_frozen_typesafe_dataclass_with_post_init():
    b = 3

    @frozen_dataclass(type_safe=True)
    class A:
        foo: int

        def __post_init__(self) -> None:
            nonlocal b
            b = 33

    with pytest.raises(expected_exception=PedanticTypeCheckException) as err:
        A(foo=42.7)

    assert err.value.args[0] == ('In dataclass "A" in field "foo": Type hint is incorrect: Argument 42.7 of type'
                         ' <class \'float\'> does not match expected type <class \'int\'>.')

    # we check that the __post_init__ method is executed
    assert b == 33


def test_frozen_typesafe_dataclass_without_post_init():
    @frozen_dataclass(type_safe=True)
    class A:
        foo: int

    with pytest.raises(expected_exception=PedanticTypeCheckException) as err:
        A(foo=42.7)

    assert err.value.args[0] == ('In dataclass "A" in field "foo": Type hint is incorrect: Argument 42.7 of type '
                         '<class \'float\'> does not match expected type <class \'int\'>.')


def test_frozen_dataclass_with_empty_braces():
    @frozen_dataclass()
    class A:
        foo: int

    a = A(foo=42)
    assert a.foo == 42


def test_frozen_dataclass_no_braces():
    @frozen_dataclass
    class A:
        foo: int

    a = A(foo=42)
    assert a.foo == 42


def test_frozen_dataclass_order():
    @frozen_dataclass(order=True)
    class A:
        foo: int
        bar: int

    a = A(foo=42, bar=43)
    b = A(foo=42, bar=42)
    c = A(foo=41, bar=44)
    d = A(foo=44, bar=0)
    assert b < a
    assert c < b
    assert a < d


def test_frozen_type_safe_dataclass_copy_with_check():
    @frozen_type_safe_dataclass
    class A:
        foo: int
        bar: bool

    a = A(foo=42, bar=False)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        a.copy_with(foo=1.1)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        a.copy_with(bar=11)

    a.copy_with(foo=11, bar=True)


def test_copy_with_is_shallow():
    a = A(foo=[1, 2], bar={'hello': 'world'}, values=(B(v={4, 5}), B(v={6})))
    shallow = a.copy_with()

    # manipulation
    shallow.bar['hello'] = 'pedantic'
    shallow.foo.append(3)

    assert a.foo == [1, 2, 3]
    assert shallow.foo == [1, 2, 3]
    assert a.bar['hello'] == 'pedantic'
    assert shallow.bar['hello'] == 'pedantic'


def test_copy_with_and_deep_copy_with():
    a = A(foo=[1, 2], bar={'hello': 'world'}, values=(B(v={4, 5}), B(v={6})))
    deep = a.deep_copy_with()

    # manipulation
    deep.bar['hello'] = 'pedantic'
    deep.foo.append(3)

    assert a.foo == [1, 2]
    assert deep.foo == [1, 2, 3]
    assert a.bar['hello'] == 'world'
    assert deep.bar['hello'] == 'pedantic'


def test_frozen_dataclass_inheritance_override_post_init():
    i = 1

    @frozen_type_safe_dataclass
    class A:
        bar: int

        def __post_init__(self):
            nonlocal i
            i += 1
            print('hello a')

    @frozen_type_safe_dataclass
    class B(A):
        foo: int

        def __post_init__(self):
            nonlocal i
            i *= 10
            print('hello b')

    A(bar=3)
    assert i == 2

    b = B(bar=3, foo=42)
    assert i == 20  # post init of A was not called
    assert b.bar == 3
    assert b.foo == 42

    a = b.copy_with()
    assert a == b
    assert i == 200


def test_frozen_dataclass_inheritance_not_override_post_init():
    i = 1

    @frozen_type_safe_dataclass
    class A:
        bar: int

        def __post_init__(self):
            nonlocal i
            i += 1
            print('hello a')

    @frozen_type_safe_dataclass
    class B(A):
        foo: int

    A(bar=3)
    assert i == 2

    b = B(bar=3, foo=42)
    assert i == 3  # post init of A was called
    assert b.bar == 3
    assert b.foo == 42

    a = b.copy_with()
    assert a == b
    assert i == 4


def test_type_safe_frozen_dataclass_with_awaitable():
    @frozen_type_safe_dataclass
    class A:
        f: Callable[..., Awaitable[int]]

    async def _cb() -> int:
        return 42

    async def _cb_2() -> str:
        return '42'

    A(f=_cb)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        A(f=_cb_2)


def test_type_safe_frozen_dataclass_with_forward_ref():
    T = TypeVar('T')

    class State(Generic[T], ABC):
        pass

    class StateMachine(Generic[T], ABC):
        pass

    @frozen_type_safe_dataclass
    class StateChangeResult:
        new_state: Optional['MachineState']

    class MachineState(State['MachineStateMachine']):
        pass

    class OfflineMachineState(MachineState):
        pass

    class OnlineMachineState:
        pass

    class MachineStateMachine(StateMachine[MachineState]):
        pass

    s = StateChangeResult(new_state=OfflineMachineState())

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        StateChangeResult(new_state=OnlineMachineState())

    s.validate_types()


def test_forward_ref_to_itself():
    """ Regression test for https://github.com/LostInDarkMath/pedantic-python-decorators/issues/72 """

    @frozen_type_safe_dataclass
    class Comment:
        replies: List['Comment']

    comment = Comment(replies=[Comment(replies=[])])
    comment.copy_with(replies=[Comment(replies=[])])
    comment.validate_types()


def test_forward_ref_to_itself_while_class_not_in_scope():
    """ Regression test for https://github.com/LostInDarkMath/pedantic-python-decorators/issues/72 """

    def _scope():
        @frozen_type_safe_dataclass
        class Comment:
            replies: List['Comment']

        def _make(replies=None):
            return Comment(replies=replies or [])

        return _make

    make = _scope()

    comment = make(replies=[make(replies=[])])
    comment.copy_with(replies=[make(replies=[])])
    comment.validate_types()


def test_slots_work_with_equals():
    @frozen_dataclass(slots=True)
    class Foo:
        a: int

    o = Foo(a=0)
    assert o == o.copy_with()
