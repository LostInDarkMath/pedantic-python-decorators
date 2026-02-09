import os.path
import types
import typing
from dataclasses import dataclass
from datetime import datetime, date
from functools import wraps, partial
from io import BytesIO, StringIO
from typing import List, Tuple, Callable, Any, Optional, Union, Dict, Set, FrozenSet, NewType, TypeVar, Sequence, \
    AbstractSet, Iterator, NamedTuple, Collection, Type, Generator, Generic, BinaryIO, TextIO, Iterable, Container, \
    NoReturn, ClassVar, Literal
from enum import Enum, IntEnum

import pytest

from pedantic import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException, PedanticException, PedanticCallWithArgsException, \
    PedanticTypeVarMismatchException
from pedantic.decorators.fn_deco_pedantic import pedantic

TEST_FILE = 'test.txt'


class Parent:
    pass


class Child(Parent):
    def method(self, a: int):
        pass


def test_no_kwargs():
    @pedantic
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        calc(42, 40, 38)
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        calc(42, m=40, i=38)
    calc(n=42, m=40, i=38)


def test_nested_type_hints_1():
    @pedantic
    def calc(n: int) -> List[List[float]]:
        return [0.0 * n]

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)


def test_nested_type_hints_1_corrected():
    @pedantic
    def calc(n: int) -> List[List[float]]:
        return [[0.0 * n]]

    calc(n=42)


def test_nested_type_hints_2():
    """Problem here: int != float"""
    @pedantic
    def calc(n: int) -> List[Tuple[float, str]]:
        return [(n, str(n))]

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)


def test_nested_type_hints_2_corrected():
    @pedantic
    def calc(n: int) -> List[Tuple[int, str]]:
        return [(n, str(n))]

    @pedantic
    def calc_2(n: float) -> List[Tuple[float, str]]:
        return [(n, str(n))]

    calc(n=42)
    calc_2(n=42.0)


def test_nested_type_hints_3():
    """Problem here: inner function actually returns Tuple[int, str]"""
    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[float, str]:
            return n * x, str(y)
        return f

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)(x=3, y=3.14)


def test_nested_type_hints_3_corrected():
    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[int, str]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[int, str]:
            return n * x, str(y)

        return f

    calc(n=42)(x=3, y=3.14)


def test_nested_type_hints_4():
    """Problem here: return type is actually float"""
    @pedantic
    def calc(n: List[List[float]]) -> int:
        return n[0][0]

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=[[42.0]])


def test_nested_type_hints_corrected():
    @pedantic
    def calc(n: List[List[float]]) -> int:
        return int(n[0][0])

    calc(n=[[42.0]])


def test_nested_type_hints_5():
    """Problem here: Tuple[float, str] != Tuple[float, float]"""

    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[float, float]:
            return n * float(x), y
        return f

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)


def test_nested_type_hints_5_corrected():
    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[float, float]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[float, float]:
            return n * float(x), y
        return f

    calc(n=42)


def test_missing_type_hint_1():
    """Problem here: type hint for n missed"""
    @pedantic
    def calc(n) -> float:
        return 42.0 * n

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)


def test_missing_type_hint_1_corrected():
    @pedantic
    def calc(n: int) -> float:
        return 42.0 * n

    calc(n=42)


def test_missing_type_hint_2():
    """Problem here: Return type annotation missed"""
    @pedantic
    def calc(n: int):
        return 'Hi' + str(n)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42)


def test_missing_type_hint_2_corrected():
    @pedantic
    def calc(n: int) -> str:
        return 'Hi' + str(n)

    calc(n=42)


def test_missing_type_hint_3():
    """Problem here: type hint for i missed"""
    @pedantic
    def calc(n: int, m: int, i) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=38)


def test_missing_type_hint_3_corrected():
    @pedantic
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    calc(n=42, m=40, i=38)


def test_all_ok_2():
    @pedantic
    def calc(n: int, m: int, i: int) -> str:
        return str(n + m + i)

    calc(n=42, m=40, i=38)


def test_all_ok_3():
    @pedantic
    def calc(n: int, m: int, i: int) -> None:
        str(n + m + i)

    calc(n=42, m=40, i=38)


def test_all_ok_4():
    @pedantic
    def calc(n: int) -> List[List[int]]:
        return [[n]]

    calc(n=42)


def test_all_ok_5():
    @pedantic
    def calc(n: int) -> List[Tuple[float, str]]:
        return [(float(n), str(n))]

    calc(n=42)


def test_all_ok_6():
    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[float, str]:
            return n * float(x), str(y)
        return f

    calc(n=42)(x=72, y=3.14)


def test_all_ok_7():
    @pedantic
    def calc(n: List[List[float]]) -> Any:
        return n[0][0]

    calc(n=[[42.0]])


def test_all_ok_8():
    @pedantic
    def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
        @pedantic
        def f(x: int, y: float) -> Tuple[float, str]:
            return n * float(x), str(y)

        return f

    calc(n=42)(x=3, y=3.14)


def test_wrong_type_hint_1():
    """Problem here: str != int"""
    @pedantic
    def calc(n: int, m: int, i: int) -> str:
        return n + m + i

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=38)


def test_wrong_type_hint_1_corrected():
    @pedantic
    def calc(n: int, m: int, i: int) -> str:
        return str(n + m + i)

    calc(n=42, m=40, i=38)


def test_wrong_type_hint_2():
    """Problem here: str != int"""
    @pedantic
    def calc(n: int, m: int, i: str) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=38)


def test_wrong_type_hint_2_corrected():
    @pedantic
    def calc(n: int, m: int, i: str) -> int:
        return n + m + int(i)

    calc(n=42, m=40, i='38')


def test_wrong_type_hint_3():
    """Problem here: None != int"""
    @pedantic
    def calc(n: int, m: int, i: int) -> None:
        return n + m + i

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=38)


def test_wrong_type_hint_corrected():
    @pedantic
    def calc(n: int, m: int, i: int) -> None:
        print(n + m + i)

    calc(n=42, m=40, i=38)


def test_wrong_type_hint_4():
    """Problem here: None != int"""
    @pedantic
    def calc(n: int, m: int, i: int) -> int:
        print(n + m + i)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=38)


def test_wrong_type_hint_4_corrected():
    @pedantic
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    calc(n=42, m=40, i=38)


def test_none_1():
    """Problem here: None is not accepted"""
    @pedantic
    def calc(n: int, m: int, i: int) -> int:
        return n + m + i

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=None)


def test_none_2():
    @pedantic
    def calc(n: int, m: int, i: Optional[int]) -> int:
        return n + m + i if i is not None else n + m

    calc(n=42, m=40, i=None)


def test_none_3():
    @pedantic
    def calc(n: int, m: int, i: Union[int, None]) -> int:
        return n + m + i if i is not None else n + m

    calc(n=42, m=40, i=None)


def test_none_4():
    """Problem here: function may return None"""
    @pedantic
    def calc(n: int, m: int, i: Union[int, None]) -> int:
        return n + m + i if i is not None else None

    calc(n=42, m=40, i=42)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(n=42, m=40, i=None)


def test_none_5():
    @pedantic
    def calc(n: int, m: int, i: Union[int, None]) -> Optional[int]:
        return n + m + i if i is not None else None

    calc(n=42, m=40, i=None)


def test_inheritance_1():
    class MyClassA:
        pass

    class MyClassB(MyClassA):
        pass

    @pedantic
    def calc(a: MyClassA) -> str:
        return str(a)

    calc(a=MyClassA())
    calc(a=MyClassB())


def test_inheritance_2():
    """Problem here: A is not a subtype of B"""
    class MyClassA:
        pass

    class MyClassB(MyClassA):
        pass

    @pedantic
    def calc(a: MyClassB) -> str:
        return str(a)

    calc(a=MyClassB())
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(a=MyClassA())


def test_instance_method_1():
    class MyClassA:
        @pedantic
        def calc(self, i: int) -> str:
            return str(i)

    a = MyClassA()
    a.calc(i=42)


def test_instance_method_2():
    """Problem here: 'i' has no type annotation"""
    class MyClassA:
        @pedantic
        def calc(self, i) -> str:
            return str(i)

    a = MyClassA()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        a.calc(i=42)


def test_instance_method_2_corrected():
    class MyClassA:
        @pedantic
        def calc(self, i: int) -> str:
            return str(i)

    a = MyClassA()
    a.calc(i=42)


def test_instance_method_int_is_not_float():
    class MyClassA:
        @pedantic
        def calc(self, i: float) -> str:
            return str(i)

    a = MyClassA()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        a.calc(i=42)


def test_instance_method_3_corrected():
    class MyClassA:
        @pedantic
        def calc(self, i: float) -> str:
            return str(i)

    a = MyClassA()
    a.calc(i=42.0)


def test_instance_method_no_kwargs():
    class MyClassA:
        @pedantic
        def calc(self, i: int) -> str:
            return str(i)

    a = MyClassA()
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        a.calc(42)


def test_instance_method_5():
    """Problem here: instance methods is not called with kwargs"""
    class MyClassA:
        @pedantic
        def calc(self, i: int) -> str:
            return str(i)

    a = MyClassA()
    a.calc(i=42)


def test_lambda_1():
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        return lambda x: str(x * i)

    calc(i=42.0)(10.0)


def test_lambda_3():
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        def res(x: float) -> str:
            return str(x * i)
        return res

    calc(i=42.0)(10.0)


def test_lambda_int_is_not_float():
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        def res(x: int) -> str:
            return str(x * i)
        return res

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=42.0)(x=10)


def test_lambda_4_almost_corrected():
    """Problem here: float != str"""
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        @pedantic
        def res(x: int) -> str:
            return str(x * i)
        return res

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=42.0)(x=10)


def test_lambda_4_almost_corrected_2():
    @pedantic
    def calc(i: float) -> Callable[[int], str]:
        @pedantic
        def res(x: int) -> str:
            return str(x * i)
        return res

    calc(i=42.0)(x=10)


def test_lambda_5():
    """Problem here: float != int"""
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        @pedantic
        def res(x: float) -> str:
            return str(x * i)
        return res

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=42.0)(x=10)


def test_lambda_corrected():
    @pedantic
    def calc(i: float) -> Callable[[float], str]:
        @pedantic
        def res(x: float) -> str:
            return str(x * i)

        return res

    calc(i=42.0)(x=10.0)


def test_tuple_without_type_args():
    @pedantic
    def calc(i: Tuple) -> str:
        return str(i)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=(42.0, 43, 'hi'))


def test_tuple_without_args_corrected():
    @pedantic
    def calc(i: Tuple[Any, ...]) -> str:
        return str(i)

    calc(i=(42.0, 43, 'hi'))


def test_callable_without_type_args():
    @pedantic
    def calc(i: Callable) -> str:
        return str(i(' you'))

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=lambda x: (42.0, 43, 'hi', x))


def test_callable_without_args_correct_with_lambdas():
    @pedantic
    def calc(i: Callable[[Any], Tuple[Any, ...]]) -> str:
        return str(i(x=' you'))

    calc(i=lambda x: (42.0, 43, 'hi', x))


def test_callable_without_args_corrected():
    @pedantic
    def calc(i: Callable[[Any], Tuple[Any, ...]]) -> str:
        return str(i(x=' you'))

    @pedantic
    def arg(x: Any) -> Tuple[Any, ...]:
        return 42.0, 43, 'hi', x
    calc(i=arg)


def test_list_without_args():
    @pedantic
    def calc(i: List) -> Any:
        return [i]

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(i=[42.0, 43, 'hi'])


def test_list_without_args_corrected():
    @pedantic
    def calc(i: List[Any]) -> List[List[Any]]:
        return [i]

    calc(i=[42.0, 43, 'hi'])


def test_ellipsis_in_callable_1():
    @pedantic
    def calc(i: Callable[..., int]) -> int:
        return i()

    @pedantic
    def call() -> int:
        return 42

    calc(i=call)


def test_ellipsis_in_callable_2():
    @pedantic
    def calc(i: Callable[..., int]) -> int:
        return i(x=3.14, y=5)

    @pedantic
    def call(x: float, y: int) -> int:
        return 42

    calc(i=call)


def test_ellipsis_in_callable_3():
    """Problem here: call to "call" misses one argument"""
    @pedantic
    def calc(i: Callable[..., int]) -> int:
        return i(x=3.14)

    @pedantic
    def call(x: float, y: int) -> int:
        return 42

    with pytest.raises(expected_exception=PedanticException):
        calc(i=call)


def test_optional_args_1():
    @pedantic
    def calc(a: int, b: int = 42) -> int:
        return a + b

    calc(a=2)


def test_optional_args_2():
    @pedantic
    def calc(a: int = 3, b: int = 42, c: float = 5.0) -> float:
        return a + b + c

    calc()
    calc(a=1)
    calc(b=1)
    calc(c=1.0)
    calc(a=1, b=1)
    calc(a=1, c=1.0)
    calc(b=1, c=1.0)
    calc(a=1, b=1, c=1.0)


def test_optional_args_3():
    """Problem here: optional argument c: 5 is not a float"""
    @pedantic
    def calc(a: int = 3, b: int = 42, c: float = 5) -> float:
        return a + b + c

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc()


def test_optional_args_3_corrected():
    @pedantic
    def calc(a: int = 3, b: int = 42, c: float = 5.0) -> float:
        return a + b + c

    calc()


def test_optional_args_4():
    class MyClass:
        @pedantic
        def foo(self, a: int, b: Optional[int] = 1) -> int:
            return a + b

    my_class = MyClass()
    my_class.foo(a=10)


def test_optional_args_5():
    @pedantic
    def calc(d: Optional[Dict[int, int]] = None) -> Optional[int]:
        if d is None:
            return None
        return sum(d.keys())

    calc(d=None)
    calc()
    calc(d={42: 3})

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(d={42: 3.14})


def test_optional_args_6():
    """"Problem here: str != int"""
    @pedantic
    def calc(d: int = 42) -> int:
        return int(d)

    calc(d=99999)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(d='999999')


def test_enum_1():
    """Problem here: Type hint for 'a' should be MyEnum instead of MyEnum.GAMMA"""
    class MyEnum(Enum):
        ALPHA = 'startEvent'
        BETA = 'task'
        GAMMA = 'sequenceFlow'

    class MyClass:
        @pedantic
        def operation(self, a: MyEnum.GAMMA) -> None:
            print(a)

    m = MyClass()
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        m.operation(a=MyEnum.GAMMA)


def test_enum_1_corrected():
    class MyEnum(Enum):
        ALPHA = 'startEvent'
        BETA = 'task'
        GAMMA = 'sequenceFlow'

    @pedantic
    def operation(a: MyEnum) -> None:
        print(a)

    operation(a=MyEnum.GAMMA)


def test_sloppy_types_dict():
    @pedantic
    def operation(d: dict) -> int:
        return len(d.keys())

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d={1: 1, 2: 2})


def test_sloppy_types_dict_almost_corrected_no_type_args():
    @pedantic
    def operation(d: Dict) -> int:
        return len(d.keys())

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d={1: 1, 2: 2})


def test_sloppy_types_dict_corrected():
    @pedantic
    def operation(d: Dict[int, int]) -> int:
        return len(d.keys())

    operation(d={1: 1, 2: 2})


def test_sloppy_types_list():
    @pedantic
    def operation(d: list) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=[1, 2, 3, 4])


def test_sloppy_types_list_almost_corrected_no_type_args():
    @pedantic
    def operation(d: List) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=[1, 2, 3, 4])


def test_sloppy_types_list_corrected():
    @pedantic
    def operation(d: List[int]) -> int:
        return len(d)

    operation(d=[1, 2, 3, 4])


def test_sloppy_types_tuple():
    @pedantic
    def operation(d: tuple) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=(1, 2, 3))


def test_sloppy_types_tuple_almost_corrected_no_type_args():
    @pedantic
    def operation(d: Tuple) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=(1, 2, 3))


def test_sloppy_types_tuple_corrected():
    @pedantic
    def operation(d: Tuple[int, int, int]) -> int:
        return len(d)

    operation(d=(1, 2, 3))


def test_sloppy_types_set():
    @pedantic
    def operation(d: set) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d={1, 2, 3})


def test_sloppy_types_set_almost_corrected_to_type_args():
    @pedantic
    def operation(d: Set) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d={1, 2, 3})


def test_sloppy_types_set_corrected():
    @pedantic
    def operation(d: Set[int]) -> int:
        return len(d)

    operation(d={1, 2, 3})


def test_sloppy_types_frozenset():
    @pedantic
    def operation(d: frozenset) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=frozenset({1, 2, 3}))


def test_sloppy_types_frozenset_almost_corrected_no_type_args():
    @pedantic
    def operation(d: FrozenSet) -> int:
        return len(d)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        operation(d=frozenset({1, 2, 3}))


def test_sloppy_types_frozenset_corrected():
    @pedantic
    def operation(d: FrozenSet[int]) -> int:
        return len(d)

    operation(d=frozenset({1, 2, 3}))


def test_type_list_but_got_tuple():
    @pedantic
    def calc(ls: List[Any]) -> int:
        return len(ls)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        calc(ls=(1, 2, 3))


def test_type_list_corrected():
    @pedantic
    def calc(ls: Tuple[Any, ...]) -> int:
        return len(ls)

    calc(ls=(1, 2, 3))


def test_any():
    @pedantic
    def calc(ls: List[Any]) -> Dict[int, Any]:
        return {i: ls[i] for i in range(0, len(ls))}

    calc(ls=[1, 2, 3])
    calc(ls=[1.11, 2.0, 3.0])
    calc(ls=['1', '2', '3'])
    calc(ls=[10.5, '2', (3, 4, 5)])


def test_aliases():
    Vector = List[float]

    @pedantic
    def scale(scalar: float, vector: Vector) -> Vector:
        return [scalar * num for num in vector]

    scale(scalar=2.0, vector=[1.0, -4.2, 5.4])


def test_new_type():
    UserId = NewType('UserId', int)

    @pedantic
    def get_user_name(user_id: UserId) -> str:
        return str(user_id)

    some_id = UserId(524313)
    get_user_name(user_id=some_id)

    # the following would be desirable but impossible to check at runtime:
    # with pytest.raises(expected_exception=AssertionError):
    #     get_user_name(user_id=-1)


def test_list_of_new_type():
    UserId = NewType('UserId', int)

    @pedantic
    def get_user_name(user_ids: List[UserId]) -> str:
        return str(user_ids)

    get_user_name(user_ids=[UserId(524313), UserId(42)])
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        get_user_name(user_ids=[UserId(524313), UserId(42), 430.0])


def test_callable_no_args():
    @pedantic
    def f(g: Callable[[], str]) -> str:
        return g()

    @pedantic
    def greetings() -> str:
        return 'hello world'

    f(g=greetings)


def test_type_var():
    T = TypeVar('T')

    @pedantic
    def first(ls: List[T]) -> T:
        return ls[0]

    first(ls=[1, 2, 3])


def test_type_var_wrong():
    T = TypeVar('T')

    @pedantic
    def first(ls: List[T]) -> T:
        return str(ls[0])

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        first(ls=[1, 2, 3])


def test_type_var_wrong_sequence():
    T = TypeVar('T')

    @pedantic
    def first(ls: Sequence[T]) -> T:
        return str(ls[0])

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        first(ls=[1, 2, 3])


def test_double_pedantic():
    @pedantic
    @pedantic
    def f(x: int, y: float) -> Tuple[float, str]:
        return float(x), str(y)

    f(x=5, y=3.14)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        f(x=5.0, y=3.14)
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        f(5, 3.14)


def test_args_kwargs():
    @pedantic
    def some_method(a: int = 0, b: float = 0.0) -> float:
        return a * b

    @pedantic
    def wrapper_method(*args: Union[int, float], **kwargs: Union[int, float]) -> float:
        return some_method(*args, **kwargs)

    some_method()
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        some_method(3, 3.0)
    some_method(a=3, b=3.0)
    wrapper_method()
    with pytest.raises(expected_exception=PedanticCallWithArgsException):
        wrapper_method(3, 3.0)
    wrapper_method(a=3, b=3.0)


def test_args_kwargs_no_type_hint():
    @pedantic
    def method_no_type_hint(*args, **kwargs) -> None:
        print(args)
        print(kwargs)

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        method_no_type_hint(a=3, b=3.0)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        method_no_type_hint()


def test_args_kwargs_wrong_type_hint():
    """See: https://www.python.org/dev/peps/pep-0484/#arbitrary-argument-lists-and-default-argument-values"""
    @pedantic
    def wrapper_method(*args: str, **kwargs: str) -> None:
        print(args)
        print(kwargs)

    wrapper_method()
    wrapper_method('hi', 'you', ':)')
    wrapper_method(a='hi', b='you', c=':)')
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        wrapper_method('hi', 'you', ':)', 7)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        wrapper_method(3, 3.0)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        wrapper_method(a=3, b=3.0)


def test_additional_kwargs():
    @pedantic
    def some_method(a: int, b: float = 0.0, **kwargs: int) -> float:
        return sum([a, b])

    some_method(a=5)
    some_method(a=5, b=0.1)
    some_method(a=5, b=0.1, c=4)
    some_method(a=5, b=0.1, c=4, d=5, e=6)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_method(a=5, b=0.1, c=4, d=5.0, e=6)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_method(a=5.0, b=0.1, c=4, d=5, e=6)
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        some_method(a=5, b=0, c=4, d=5, e=6)


def test_args_kwargs_different_types():
    @pedantic
    def foo(*args: str, **kwds: int) -> None:
        print(args)
        print(kwds)

    foo('a', 'b', 'c')
    foo(x=1, y=2)
    foo('', z=0)


def test_pedantic_on_class():
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        @pedantic
        class MyClass:
            pass
        MyClass()


def test_is_subtype_tuple():
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        @pedantic
        def foo() -> Callable[[Tuple[float, str]], Tuple[int]]:
            def bar(a: Tuple[float]) -> Tuple[int]:
                return len(a[1]) + int(a[0]),
            return bar
        foo()


def test_is_subtype_tuple_corrected():
    @pedantic
    def foo() -> Callable[[Tuple[float, str]], Tuple[int]]:
        def bar(a: Tuple[float, str]) -> Tuple[int]:
            return len(a[1]) + int(a[0]),
        return bar
    foo()


def test_forward_ref():
    class Conversation:
        pass

    @pedantic
    def get_conversations() -> List['Conversation']:
        return [Conversation(), Conversation()]

    get_conversations()


def test_alternative_list_type_hint():
    @pedantic
    def _is_digit_in_int(digit: [int], num: int) -> bool:
        num_str = str(num)
        for i in num_str:
            if int(i) == digit:
                return True
        return False

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        _is_digit_in_int(digit=4, num=42)


def test_callable_with_union_return():
    class MyClass:
        pass

    @pedantic
    def admin_required(func: Callable[..., Union[str, MyClass]]) -> Callable[..., Union[str, MyClass]]:
        @wraps(func)
        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated_function

    @admin_required
    @pedantic
    def get_server_info() -> str:
        return 'info'

    get_server_info()


def test_pedantic():
    @pedantic
    def foo(a: int, b: str) -> str:
        return 'abc'

    assert foo(a=4, b='abc') == 'abc'


def test_pedantic_always():
    @pedantic
    def foo(a: int, b: str) -> str:
        return 'abc'

    assert foo(a=4, b='abc') == 'abc'


def test_pedantic_arguments_fail():
    @pedantic
    def foo(a: int, b: str) -> str:
        return 'abc'

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        foo(a=4, b=5)


def test_pedantic_return_type_fail():
    @pedantic
    def foo(a: int, b: str) -> str:
        return 6

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        foo(a=4, b='abc')


def test_return_type_none():
    @pedantic
    def foo() -> None:
        return 'a'
    with pytest.raises(expected_exception=PedanticTypeCheckException):
        foo()


def test_marco():
    @pedantic_class
    class A:
        def __init__(self, val: int) -> None:
            self.val = val

        def __eq__(self, other: 'A') -> bool:  # other: A and all subclasses
            return self.val == other.val

    @pedantic_class
    class B(A):
        def __init__(self, val: int) -> None:
            super().__init__(val=val)

    @pedantic_class
    class C(A):
        def __init__(self, val: int) -> None:
            super().__init__(val=val)

    a = A(val=42)
    b = B(val=42)
    c = C(val=42)

    assert a == b  # works
    assert a == c  # works
    assert b == c  # error


def test_date_datetime():
    @pedantic
    def foo(a: datetime, b: date) -> None:
        pass

    foo(a=datetime(1995, 2, 5), b=date(1987, 8, 7))
    foo(a=datetime(1995, 2, 5), b=datetime(1987, 8, 7))

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        foo(a=date(1995, 2, 5), b=date(1987, 8, 7))


def test_any_type():
    @pedantic
    def foo(a: Any) -> None:
        pass

    foo(a='aa')


def test_callable_exact_arg_count():
    @pedantic
    def foo(a: Callable[[int, str], int]) -> None:
        pass

    def some_callable(x: int, y: str) -> int:
        pass

    foo(a=some_callable)


def test_callable_bad_type():
    @pedantic
    def foo(a: Callable[..., int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_callable_too_few_arguments():
    @pedantic
    def foo(a: Callable[[int, str], int]) -> None:
        pass

    def some_callable(x: int) -> int:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=some_callable)


def test_callable_mandatory_kwonlyargs():
    @pedantic
    def foo(a: Callable[[int, str], int]) -> None:
        pass

    def some_callable(x: int, y: str, *, z: float, bar: str) -> int:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=some_callable)


def test_callable_class():
    """
    Test that passing a class as a callable does not count the "self" argument "a"gainst the
    ones declared in the Callable specification.

    """
    @pedantic
    def foo(a: Callable[[int, str], Any]) -> None:
        pass

    class SomeClass:
        def __init__(self, x: int, y: str):
            pass

    foo(a=SomeClass)


def test_callable_plain():
    @pedantic
    def foo(a: Callable[..., Any]) -> None:
        pass

    def callback(a):
        pass

    foo(a=callback)


def test_callable_bound_method():
    @pedantic
    def foo(callback: Callable[[int], Any]) -> None:
        pass

    foo(callback=Child().method)


def test_callable_defaults():
    """
    Test that a callable having "too many" arguments don't raise an error if the extra
    arguments have default values.

    """
    @pedantic
    def foo(callback: Callable[[int, str], Any]) -> None:
        pass

    def some_callable(x: int, y: str, z: float = 1.2) -> int:
        pass

    foo(callback=some_callable)


def test_callable_builtin():
    @pedantic
    def foo(callback: types.BuiltinFunctionType) -> None:
        pass

    foo(callback=[].append)


def test_dict_bad_type():
    @pedantic
    def foo(a: Dict[str, int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_dict_bad_key_type():
    @pedantic
    def foo(a: Dict[str, int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a={1: 2})


def test_dict_bad_value_type():
    @pedantic
    def foo(a: Dict[str, int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a={'x': 'a'})


def test_list_bad_type():
    @pedantic
    def foo(a: List[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_list_bad_element():
    @pedantic
    def foo(a: List[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=[1, 2, 'bb'])


def test_sequence_bad_type():
    @pedantic
    def foo(a: Sequence[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_sequence_bad_element():
    @pedantic
    def foo(a: Sequence[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=[1, 2, 'bb'])


def test_abstractset_custom_type():
    T = TypeVar('T')

    @pedantic_class
    class DummySet(AbstractSet[T]):
        def __contains__(self, x: object) -> bool:
            return x == 1

        def __len__(self) -> T:
            return 1

        def __iter__(self) -> Iterator[T]:
            yield 1

    @pedantic
    def foo(a: AbstractSet[int]) -> None:
        pass

    foo(a=DummySet[int]())


def test_abstractset_bad_type():
    @pedantic
    def foo(a: AbstractSet[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_set_bad_type():
    @pedantic
    def foo(a: Set[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_abstractset_bad_element():
    @pedantic
    def foo(a: AbstractSet[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a={1, 2, 'bb'})


def test_set_bad_element():
    @pedantic
    def foo(a: Set[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a={1, 2, 'bb'})


def test_tuple_bad_type():
    @pedantic
    def foo(a: Tuple[int]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=5)


def test_tuple_too_many_elements():
    @pedantic
    def foo(a: Tuple[int, str]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=(1, 'aa', 2))


def test_tuple_too_few_elements():
    @pedantic
    def foo(a: Tuple[int, str]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=(1,))


def test_tuple_bad_element():
    @pedantic
    def foo(a: Tuple[int, str]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=(1, 2))


def test_tuple_ellipsis_bad_element():
    @pedantic
    def foo(a: Tuple[int, ...]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=(1, 2, 'blah'))


def test_namedtuple():
    Employee = NamedTuple('Employee', [('name', str), ('id', int)])

    @pedantic
    def foo(bar: Employee) -> None:
        print(bar)

    foo(bar=Employee('bob', 1))


def test_namedtuple_key_mismatch():
    Employee1 = NamedTuple('Employee', [('name', str), ('id', int)])
    Employee2 = NamedTuple('Employee', [('firstname', str), ('id', int)])

    @pedantic
    def foo(bar: Employee1) -> None:
        print(bar)

    with pytest.raises(PedanticTypeCheckException):
        foo(bar=Employee2('bob', 1))


def test_namedtuple_type_mismatch():
    Employee = NamedTuple('Employee', [('name', str), ('id', int)])

    @pedantic
    def foo(bar: Employee) -> None:
        print(bar)

    with pytest.raises(PedanticTypeCheckException):
        foo(bar=('bob', 1))


def test_namedtuple_huge_type_mismatch():
    Employee = NamedTuple('Employee', [('name', str), ('id', int)])

    @pedantic
    def foo(bar: int) -> None:
        print(bar)

    with pytest.raises(PedanticTypeCheckException):
        foo(bar=foo(bar=Employee('bob', 1)))


def test_namedtuple_wrong_field_type():
    Employee = NamedTuple('Employee', [('name', str), ('id', int)])

    @pedantic
    def foo(bar: Employee) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(bar=Employee(2, 1))


def test_union():
    @pedantic
    def foo(a: Union[str, int]) -> None:
        pass

    for value in [6, 'xa']:
        foo(a=value)


def test_union_new_syntax():
    @pedantic
    def foo(a: str | int) -> None:
        pass

    for value in [6, 'xa']:
        foo(a=value)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1.7)


def test_union_typing_type():
    @pedantic
    def foo(a: Union[str, Collection]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1)


def test_union_fail():
    @pedantic
    def foo(a: Union[str, int]) -> None:
        pass

    for value in [5.6, b'xa']:
        with pytest.raises(PedanticTypeCheckException):
            foo(a=value)


def test_type_var_constraints():
    T = TypeVar('T', int, str)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    for values in [
        {'a': 6, 'b': 7},
        {'a': 'aa', 'b': "bb"},
    ]:
        foo(**values)


def test_type_var_constraints_fail_typing_type():
    T = TypeVar('T', int, Collection)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a='aa', b='bb')


def test_typevar_constraints_fail():
    T = TypeVar('T', int, str)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=2.5, b='aa')


def test_typevar_bound():
    T = TypeVar('T', bound=Parent)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    foo(a=Child(), b=Child())


def test_type_var_bound_fail():
    T = TypeVar('T', bound=Child)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=Parent(), b=Parent())


def test_type_var_invariant_fail():
    T = TypeVar('T', int, str)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=2, b=3.6)


def test_type_var_covariant():
    T = TypeVar('T', covariant=True)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    foo(a=Parent(), b=Child())


def test_type_var_covariant_fail():
    T = TypeVar('T', covariant=True)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeVarMismatchException):
        foo(a=Child(), b=Parent())


def test_type_var_contravariant():
    T = TypeVar('T', contravariant=True)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    foo(a=Child(), b=Parent())


def test_type_var_contravariant_fail():
    T = TypeVar('T', contravariant=True)

    @pedantic
    def foo(a: T, b: T) -> None:
        pass

    with pytest.raises(PedanticTypeVarMismatchException):
        foo(a=Parent(), b=Child())


def test_class_bad_subclass():
    @pedantic
    def foo(a: Type[Child]) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=Parent)


def test_class_any():
    @pedantic
    def foo(a: Type[Any]) -> None:
        pass

    foo(a=str)


def test_wrapped_function():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @pedantic
    @decorator
    def foo(a: 'Child') -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=Parent())


def test_mismatching_default_type():
    @pedantic
    def foo(a: str = 1) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo()


def test_implicit_default_none():
    """
    Test that if the default value is ``None``, a ``None`` argument can be passed.

    """
    @pedantic
    def foo(a: Optional[str] = None) -> None:
        pass

    foo()


def test_generator_simple():
    """Test that argument type checking works in a generator function too."""
    @pedantic
    def generate(a: int) -> Generator[int, int, None]:
        yield a
        yield a + 1

    gen = generate(a=1)
    next(gen)


def test_wrapped_generator_no_return_type_annotation():
    """Test that return type checking works in a generator function too."""
    @pedantic
    def generate(a: int) -> Generator[int, int, None]:
        yield a
        yield a + 1

    gen = generate(a=1)
    next(gen)


def test_varargs():
    @pedantic
    def foo(*args: int) -> None:
        pass

    foo(1, 2)


def test_varargs_fail():
    @pedantic
    def foo(*args: int) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(1, 'a')


def test_kwargs():
    @pedantic
    def foo(**kwargs: int) -> None:
        pass

    foo(a=1, b=2)


def test_kwargs_fail():
    @pedantic
    def foo(**kwargs: int) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1, b='a')


def test_generic():
    T_Foo = TypeVar('T_Foo')

    class FooGeneric(Generic[T_Foo]):
        pass

    @pedantic
    def foo(a: FooGeneric[str]) -> None:
        print(a)

    foo(a=FooGeneric[str]())


def test_newtype():
    myint = NewType("myint", int)

    @pedantic
    def foo(a: myint) -> int:
        return 42

    assert foo(a=1) == 42

    with pytest.raises(PedanticTypeCheckException):
        foo(a="a")


def test_collection():
    @pedantic
    def foo(a: Collection) -> None:
        pass

    with pytest.raises(PedanticTypeCheckException):
        foo(a=True)


def test_binary_io():
    @pedantic
    def foo(a: BinaryIO) -> None:
        print(a)

    foo(a=BytesIO())


def test_text_io():
    @pedantic
    def foo(a: TextIO) -> None:
        print(a)

    foo(a=StringIO())


def test_binary_io_fail():
    @pedantic
    def foo(a: TextIO) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=BytesIO())


def test_text_io_fail():
    @pedantic
    def foo(a: BinaryIO) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=StringIO())


def test_binary_io_real_file():
    @pedantic
    def foo(a: BinaryIO) -> None:
        print(a)

    with open(file=TEST_FILE, mode='wb') as f:
        foo(a=f)

    os.remove(TEST_FILE)


def test_text_io_real_file():
    @pedantic
    def foo(a: TextIO) -> None:
        print(a)

    with open(file=TEST_FILE, mode='w') as f:
        foo(a=f)

    os.remove(TEST_FILE)


def test_pedantic_return_type_var_fail():
    T = TypeVar('T', int, float)

    @pedantic
    def foo(a: T, b: T) -> T:
        return 'a'

    with pytest.raises(PedanticTypeCheckException):
        foo(a=4, b=2)


def test_callable():
    @pedantic
    def foo_1(a: Callable[..., int]) -> None:
        print(a)

    @pedantic
    def foo_2(a: Callable) -> None:
        print(a)

    def some_callable() -> int:
        return 4

    foo_1(a=some_callable)

    with pytest.raises(PedanticTypeCheckException):
        foo_2(a=some_callable)


def test_list():
    @pedantic
    def foo_1(a: List[int]) -> None:
        print(a)

    @pedantic
    def foo_2(a: List) -> None:
        print(a)

    @pedantic
    def foo_3(a: list) -> None:
        print(a)

    @pedantic
    def foo_4(a: list[int]) -> None:
        print(a)

    foo_1(a=[1, 2])

    with pytest.raises(PedanticTypeCheckException):
        foo_2(a=[1, 2])

    with pytest.raises(PedanticTypeCheckException):
        foo_3(a=[1, 2])

    foo_4(a=[1, 2])


def test_dict():
    @pedantic
    def foo_1(a: Dict[str, int]) -> None:
        print(a)

    @pedantic
    def foo_2(a: Dict) -> None:
        print(a)

    @pedantic
    def foo_3(a: dict) -> None:
        print(a)

    @pedantic
    def foo_4(a: dict[str, int]) -> None:
        print(a)

    foo_1(a={'x': 2})

    with pytest.raises(PedanticTypeCheckException):
        foo_2(a={'x': 2})

    with pytest.raises(PedanticTypeCheckException):
        foo_3(a={'x': 2})

    foo_4(a={'x': 2})


def test_sequence():
    @pedantic
    def foo(a: Sequence[str]) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        foo(a=value)


def test_sequence_no_type_args():
    @pedantic
    def foo(a: Sequence) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        with pytest.raises(PedanticTypeCheckException):
            foo(a=value)


def test_iterable():
    @pedantic
    def foo(a: Iterable[str]) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        foo(a=value)


def test_iterable_no_type_args():
    @pedantic
    def foo(a: Iterable) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        with pytest.raises(PedanticTypeCheckException):
            foo(a=value)


def test_container():
    @pedantic
    def foo(a: Container[str]) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        foo(a=value)


def test_container_no_type_args():
    @pedantic
    def foo(a: Container) -> None:
        print(a)

    for value in [('a', 'b'), ['a', 'b'], 'abc']:
        with pytest.raises(PedanticTypeCheckException):
            foo(a=value)


def test_set():
    @pedantic
    def foo_1(a: AbstractSet[int]) -> None:
        print(a)

    @pedantic
    def foo_2(a: Set[int]) -> None:
        print(a)

    for value in [set(), {6}]:
        foo_1(a=value)
        foo_2(a=value)


def test_set_no_type_args():
    @pedantic
    def foo_1(a: AbstractSet) -> None:
        print(a)

    @pedantic
    def foo_2(a: Set) -> None:
        print(a)

    @pedantic
    def foo_3(a: set) -> None:
        print(a)

    for value in [set(), {6}]:
        with pytest.raises(PedanticTypeCheckException):
            foo_1(a=value)

        with pytest.raises(PedanticTypeCheckException):
            foo_2(a=value)

        with pytest.raises(PedanticTypeCheckException):
            foo_3(a=value)


def test_tuple():
    @pedantic
    def foo_1(a: Tuple[int, int]) -> None:
        print(a)

    @pedantic
    def foo_2(a: Tuple[int, ...]) -> None:
        print(a)

    foo_1(a=(1, 2))
    foo_2(a=(1, 2))


def test_tuple_no_type_args():
    @pedantic
    def foo_1(a: Tuple) -> None:
        print(a)

    @pedantic
    def foo_2(a: tuple) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo_1(a=(1, 2))

    with pytest.raises(PedanticTypeCheckException):
        foo_2(a=(1, 2))


def test_empty_tuple():
    @pedantic
    def foo(a: Tuple[()]) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=())


def test_class():
    @pedantic
    def foo_1(a: Type[Parent]) -> None:
        print(a)

    @pedantic
    def foo_2(a: Type[TypeVar('UnboundType')]) -> None:
        print(a)

    @pedantic
    def foo_3(a: Type[TypeVar('BoundType', bound=Parent)]) -> None:
        print(a)

    foo_1(a=Child)
    foo_2(a=Child)
    foo_3(a=Child)


def test_class_no_type_vars():
    @pedantic
    def foo_1(a: Type) -> None:
        print(a)

    @pedantic
    def foo_2(a: type) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo_1(a=Child)

    with pytest.raises(PedanticTypeCheckException):
        foo_2(a=Child)


def test_class_not_a_class():
    @pedantic
    def foo(a: Type[Parent]) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1)


def test_complex():
    @pedantic
    def foo(a: complex) -> None:
        print(a)

    foo(a=complex(1, 5))

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1.0)


def test_float():
    @pedantic
    def foo(a: float) -> None:
        print(a)

    foo(a=1.5)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=1)


def test_coroutine_correct_return_type():
    @pedantic
    async def foo() -> str:
        return 'foo'

    coro = foo()

    with pytest.raises(StopIteration):
        coro.send(None)


def test_coroutine_wrong_return_type():
    @pedantic
    async def foo() -> str:
        return 1

    coro = foo()

    with pytest.raises(PedanticTypeCheckException):
        coro.send(None)


def test_bytearray_bytes():
    @pedantic
    def foo(x: bytearray) -> None:
        pass

    foo(x=bytearray([1]))


def test_class_decorator():
    @pedantic_class
    class Foo:
        @staticmethod
        def staticmethod() -> int:
            return 'foo'

        @classmethod
        def classmethod(cls) -> int:
            return 'foo'

        def method(self) -> int:
            return 'foo'

    with pytest.raises(PedanticTypeCheckException):
        Foo.staticmethod()

    with pytest.raises(PedanticTypeCheckException):
        Foo.classmethod()

    with pytest.raises(PedanticTypeCheckException):
        Foo().method()


def test_generator():
    @pedantic
    def genfunc() -> Generator[int, str, List[str]]:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    gen = genfunc()

    with pytest.raises(StopIteration):
        value = next(gen)
        while True:
            value = gen.send(str(value))
            assert isinstance(value, int)


def test_generator_no_type_args():
    @pedantic
    def genfunc() -> Generator:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    with pytest.raises(PedanticTypeCheckException):
        genfunc()


def test_iterator():
    @pedantic
    def genfunc() -> Iterator[int]:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    gen = genfunc()

    with pytest.raises(PedanticTypeCheckException):
        value = next(gen)
        while True:
            value = gen.send(str(value))
            assert isinstance(value, int)


def test_iterator_no_type_args():
    @pedantic
    def genfunc() -> Iterator:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    with pytest.raises(PedanticTypeCheckException):
        genfunc()


def test_iterable_advanced():
    @pedantic
    def genfunc() -> Iterable[int]:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    gen = genfunc()

    with pytest.raises(PedanticTypeCheckException):
        value = next(gen)
        while True:
            value = gen.send(str(value))
            assert isinstance(value, int)


def test_iterable_advanced_no_type_args():
    @pedantic
    def genfunc() -> Iterable:
        val1 = yield 2
        val2 = yield 3
        val3 = yield 4
        return [val1, val2, val3]

    with pytest.raises(PedanticTypeCheckException):
        genfunc()


def test_generator_bad_yield():
    @pedantic
    def genfunc_1() -> Generator[int, str, None]:
        yield 'foo'

    @pedantic
    def genfunc_2() -> Iterable[int]:
        yield 'foo'

    @pedantic
    def genfunc_3() -> Iterator[int]:
        yield 'foo'

    gen = genfunc_1()

    with pytest.raises(PedanticTypeCheckException):
        next(gen)

    gen = genfunc_2()

    with pytest.raises(PedanticTypeCheckException):
        next(gen)

    gen = genfunc_3()

    with pytest.raises(PedanticTypeCheckException):
        next(gen)


def test_generator_bad_send():
    @pedantic
    def genfunc() -> Generator[int, str, None]:
        yield 1
        yield 2

    gen = genfunc()
    next(gen)

    with pytest.raises(PedanticTypeCheckException):
        gen.send(2)


def test_generator_bad_return():
    @pedantic
    def genfunc() -> Generator[int, str, str]:
        yield 1
        return 6

    gen = genfunc()
    next(gen)

    with pytest.raises(PedanticTypeCheckException):
        gen.send('foo')


def test_return_generator():
    @pedantic
    def genfunc() -> Generator[int, None, None]:
        yield 1

    @pedantic
    def foo() -> Generator[int, None, None]:
        return genfunc()

    foo()


def test_local_class():
    @pedantic_class
    class LocalClass:
        class Inner:
            pass

        def create_inner(self) -> 'Inner':
            return self.Inner()

    retval = LocalClass().create_inner()
    assert isinstance(retval, LocalClass.Inner)


def test_local_class_async():
    @pedantic_class
    class LocalClass:
        class Inner:
            pass

        async def create_inner(self) -> 'Inner':
            return self.Inner()

    coro = LocalClass().create_inner()

    with pytest.raises(StopIteration):
        coro.send(None)


def test_callable_nonmember():
    class CallableClass:
        def __call__(self):
            pass

    @pedantic_class
    class LocalClass:
        some_callable = CallableClass()


def test_inherited_class_method():
    @pedantic_class
    class Parent:
        @classmethod
        def foo(cls, x: str) -> str:
            return cls.__name__

    @pedantic_class
    class Child(Parent):
        pass

    assert Child.foo(x='bar') == 'Parent'

    with pytest.raises(PedanticTypeCheckException):
        Child.foo(x=1)


def test_type_var_forward_ref_bound():
    TBound = TypeVar('TBound', bound='Parent')

    @pedantic
    def func(x: TBound) -> None:
        pass

    func(x=Parent())

    with pytest.raises(PedanticTypeCheckException):
        func(x='foo')


def test_noreturn():
    @pedantic
    def foo() -> NoReturn:
        pass

    @pedantic
    def bar() -> NoReturn:
        raise ZeroDivisionError('bar')

    with pytest.raises(expected_exception=ZeroDivisionError):
        bar()

    with pytest.raises(PedanticTypeCheckException):
        foo()


def test_literal():
    @pedantic
    def foo(a: Literal[1, True, 'x', b'y', 404]) -> None:
        print(a)

    foo(a=404)
    foo(a=True)
    foo(a='x')

    with pytest.raises(PedanticTypeCheckException):
        foo(a=4)


def test_literal_union():
    @pedantic
    def foo(a: Union[str, Literal[1, 6, 8]]) -> None:
        print(a)

    foo(a=6)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=4)


def test_literal_illegal_value():
    @pedantic
    def foo(a: Literal[1, 1.1]) -> None:
        print(a)

    with pytest.raises(PedanticTypeCheckException):
        foo(a=4)


def test_enum():
    with pytest.raises(PedanticTypeCheckException):
        @pedantic_class
        class MyEnum(Enum):
            A = 'a'


def test_enum_aggregate():
    T = TypeVar('T', bound=IntEnum)

    @pedantic_class
    class EnumAggregate(Generic[T]):
        enum: ClassVar[Type[T]]

        def __init__(self, value: Union[int, str, List[T]]) -> None:
            assert len(self.enum) < 10

            if value == '':
                raise ValueError(f'Parameter "value" cannot be empty!')

            if isinstance(value, list):
                self._value = ''.join([str(x.value) for x in value])
            else:
                self._value = str(value)

            self._value = ''.join(sorted(self._value))  # sort characters in string
            self.to_list()  # check if is valid

        def __contains__(self, item: T) -> bool:
            return item in self.to_list()

        def __eq__(self, other: Union['EnumAggregate', str]) -> bool:
            if isinstance(other, str):
                return self._value == other

            return self._value == other._value

        def __str__(self) -> str:
            return self._value

        def to_list(self) -> List[T]:
            return [self.enum(int(character)) for character in self._value]

        @property
        def value(self) -> str:
            return self._value

        @classmethod
        def all(cls) -> str:
            return ''.join([str(x.value) for x in cls.enum])

    class Gender(IntEnum):
        MALE = 1
        FEMALE = 2
        DIVERS = 3

    @pedantic_class
    class Genders(EnumAggregate[Gender]):
        enum = Gender

    Genders(value=12)

    with pytest.raises(PedanticTypeCheckException):
        Genders(value=Child())


def test_primitive_list_dict_tuple():
    @pedantic
    def f(x: list[dict[int, tuple[float, str]]]) -> list[Any]:
        return x

    f(x=[{3: (3.24, 'hi')}])

    for value in [
        [{3, (3, 'hi')}],
        [{3: (3, 'hi')}],
        [{3: (3.24, 3)}],
        [{3: (3.24, 'hi')}, {0}],
    ]:
        with pytest.raises(PedanticTypeCheckException):
            f(x=value)


def test_dataclass_protocol():
    class IsDataclass(typing.Protocol):
        __dataclass_fields__: ClassVar[Dict]

    @dataclass
    class Foo:
        v: int

    @pedantic
    def foo(x: IsDataclass) -> IsDataclass:
        return x

    foo(x=Foo(v=42))


def test_dataclass_protocol_in_type():
    class IsDataclass(typing.Protocol):
        __dataclass_fields__: ClassVar[Dict]

    @dataclass
    class Foo:
        v: int

    @pedantic
    def foo(x: type[IsDataclass]) -> IsDataclass:
        return x

    assert foo(x=Foo) == Foo


def test_dataclass_protocol_in_type_with_union():
    class IsDataclass(typing.Protocol):
        __dataclass_fields__: ClassVar[Dict]

    @dataclass
    class Foo:
        v: int

    @pedantic
    def foo(x: type[None | bool | IsDataclass]) -> IsDataclass:
        return x

    assert foo(x=Foo) == Foo


def test_partial_function():
    @pedantic
    def f(a: int, b: int) -> int:
        return a + b

    g = pedantic(partial(f, a=1))

    assert f(a=2, b=3) == 5
    assert g(b=3) == 4

    with pytest.raises(PedanticTypeCheckException):
        f(a='2', b=3)

    with pytest.raises(PedanticTypeCheckException):
        g(b='2')


def test_typing_never():
    from typing import Never

    @pedantic
    def never_call_me(arg: Never) -> None:
        pass

    @pedantic
    def foo() -> Never:
        pass

    @pedantic
    def bar() -> Never:
        raise ZeroDivisionError('bar')

    with pytest.raises(expected_exception=ZeroDivisionError):
        bar()

    with pytest.raises(PedanticTypeCheckException):
        foo()

    with pytest.raises(expected_exception=PedanticTypeCheckException) as exc:
        never_call_me(arg='42')


def test_literal_string():
    from typing import LiteralString

    @pedantic
    def foo(s: LiteralString) -> None:
        pass

    foo(s='Hi')
    foo(s=2 * 'Hi')

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        foo(s=3)


def test_self_type():
    from typing import Self

    class Bar:
        pass

    @pedantic_class
    class Foo:
        def f(self) -> Self:
            return self

        @staticmethod
        def g() -> Self:
            return Foo()

        @classmethod
        def h(cls) -> Self:
            return cls()

        def f_2(self) -> Self:
            return Bar()

        @staticmethod
        def g_2() -> Self:
            return Bar()

        @classmethod
        def h_2(cls) -> Self:
            return Bar()

    f = Foo()
    assert f.f() == f
    f.g()
    f.h()
    Foo.g()
    Foo.h()

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        f.f_2()

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        f.g_2()

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        f.h_2()

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        Foo.g_2()

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        Foo.h_2()


def test_using_self_type_annotation_outside_class():
    from typing import Self

    @pedantic
    def f() -> Self:
        return 'hi'

    with pytest.raises(expected_exception=PedanticTypeCheckException):
        f()


def test_type_var_tuple():
    from typing import TypeVarTuple, Generic

    Ts = TypeVarTuple('Ts')

    @pedantic_class
    class Array(Generic[*Ts]):
        def __init__(self, *args: *Ts) -> None:
            self._values = args

    @pedantic
    def add_dimension(a: Array[*Ts], value: int) -> Array[int, *Ts]:
        return Array[int, *Ts](value, *a._values)

    array = Array[int, float](42, 3.4)
    array_2 = Array[bool, int, float, str](True, 4, 3.4, 'hi')
    extended_array = add_dimension(a=array, value=42)
    assert extended_array._values == (42, 42, 3.4)

    # this is too complicated at the moment
    # with pytest.raises(expected_exception=PedanticTypeCheckException):
    #     Array[int, float](4.2, 3.4)
