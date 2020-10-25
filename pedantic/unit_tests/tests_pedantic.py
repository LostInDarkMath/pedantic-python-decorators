import unittest
from functools import wraps
from typing import List, Tuple, Callable, Any, Optional, Union, Dict, Set, FrozenSet, NewType, TypeVar, Sequence
from enum import Enum

from pedantic.exceptions import PedanticTypeCheckException, PedanticException, PedanticCallWithArgsException, \
    PedanticTypeVarMismatchException
from pedantic.method_decorators import pedantic


class TestDecoratorRequireKwargsAndTypeCheck(unittest.TestCase):
    def test_no_kwargs(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            calc(42, 40, 38)
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            calc(42, m=40, i=38)
        calc(n=42, m=40, i=38)

    def test_nested_type_hints_1(self):
        @pedantic
        def calc(n: int) -> List[List[float]]:
            return [0.0 * n]

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)

    def test_nested_type_hints_1_corrected(self):
        @pedantic
        def calc(n: int) -> List[List[float]]:
            return [[0.0 * n]]

        calc(n=42)

    def test_nested_type_hints_2(self):
        """Problem here: int != float"""
        @pedantic
        def calc(n: int) -> List[Tuple[float, str]]:
            return [(n, str(n))]

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)

    def test_nested_type_hints_2_corrected(self):
        @pedantic
        def calc(n: int) -> List[Tuple[int, str]]:
            return [(n, str(n))]

        @pedantic
        def calc_2(n: float) -> List[Tuple[float, str]]:
            return [(n, str(n))]

        calc(n=42)
        calc_2(n=42.0)

    def test_nested_type_hints_3(self):
        """Problem here: inner function actually returns Tuple[int, str]"""
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, str]:
                return n * x, str(y)
            return f

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)(x=3, y=3.14)

    def test_nested_type_hints_3_corrected(self):
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[int, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[int, str]:
                return n * x, str(y)

            return f

        calc(n=42)(x=3, y=3.14)

    def test_nested_type_hints_4(self):
        """Problem here: return type is actually float"""
        @pedantic
        def calc(n: List[List[float]]) -> int:
            return n[0][0]

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=[[42.0]])

    def test_nested_type_hints_corrected(self):
        @pedantic
        def calc(n: List[List[float]]) -> int:
            return int(n[0][0])

        calc(n=[[42.0]])

    def test_nested_type_hints_5(self):
        """Problem here: Tuple[float, str] != Tuple[float, float]"""

        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, float]:
                return n * float(x), y
            return f

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)

    def test_nested_type_hints_5_corrected(self):
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, float]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, float]:
                return n * float(x), y
            return f

        calc(n=42)

    def test_missing_type_hint_1(self):
        """Problem here: type hint for n missed"""
        @pedantic
        def calc(n) -> float:
            return 42.0 * n

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)

    def test_missing_type_hint_1_corrected(self):
        @pedantic
        def calc(n: int) -> float:
            return 42.0 * n

        calc(n=42)

    def test_missing_type_hint_2(self):
        """Problem here: Return type annotation missed"""
        @pedantic
        def calc(n: int):
            return 'Hi' + str(n)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42)

    def test_missing_type_hint_2_corrected(self):
        @pedantic
        def calc(n: int) -> str:
            return 'Hi' + str(n)

        calc(n=42)

    def test_missing_type_hint_3(self):
        """Problem here: type hint for i missed"""
        @pedantic
        def calc(n: int, m: int, i) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=38)

    def test_missing_type_hint_3_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        calc(n=42, m=40, i=38)

    def test_all_ok_2(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> str:
            return str(n + m + i)

        calc(n=42, m=40, i=38)

    def test_all_ok_3(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> None:
            str(n + m + i)

        calc(n=42, m=40, i=38)

    def test_all_ok_4(self):
        @pedantic
        def calc(n: int) -> List[List[int]]:
            return [[n]]

        calc(n=42)

    def test_all_ok_5(self):
        @pedantic
        def calc(n: int) -> List[Tuple[float, str]]:
            return [(float(n), str(n))]

        calc(n=42)

    def test_all_ok_6(self):
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, str]:
                return n * float(x), str(y)
            return f

        calc(n=42)(x=72, y=3.14)

    def test_all_ok_7(self):
        @pedantic
        def calc(n: List[List[float]]) -> Any:
            return n[0][0]

        calc(n=[[42.0]])

    def test_all_ok_8(self):
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, str]:
                return n * float(x), str(y)

            return f

        calc(n=42)(x=3, y=3.14)

    def test_wrong_type_hint_1(self):
        """Problem here: str != int"""
        @pedantic
        def calc(n: int, m: int, i: int) -> str:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=38)

    def test_wrong_type_hint_1_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> str:
            return str(n + m + i)

        calc(n=42, m=40, i=38)

    def test_wrong_type_hint_2(self):
        """Problem here: str != int"""
        @pedantic
        def calc(n: int, m: int, i: str) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=38)

    def test_wrong_type_hint_2_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: str) -> int:
            return n + m + int(i)

        calc(n=42, m=40, i='38')

    def test_wrong_type_hint_3(self):
        """Problem here: None != int"""
        @pedantic
        def calc(n: int, m: int, i: int) -> None:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=38)

    def test_wrong_type_hint_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> None:
            print(n + m + i)

        calc(n=42, m=40, i=38)

    def test_wrong_type_hint_4(self):
        """Problem here: None != int"""
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            print(n + m + i)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=38)

    def test_wrong_type_hint_4_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        calc(n=42, m=40, i=38)

    def test_none_1(self):
        """Problem here: None is not accepted"""
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=None)

    def test_none_2(self):
        @pedantic
        def calc(n: int, m: int, i: Optional[int]) -> int:
            return n + m + i if i is not None else n + m

        calc(n=42, m=40, i=None)

    def test_none_3(self):
        @pedantic
        def calc(n: int, m: int, i: Union[int, None]) -> int:
            return n + m + i if i is not None else n + m

        calc(n=42, m=40, i=None)

    def test_none_4(self):
        """Problem here: function may return None"""
        @pedantic
        def calc(n: int, m: int, i: Union[int, None]) -> int:
            return n + m + i if i is not None else None

        calc(n=42, m=40, i=42)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(n=42, m=40, i=None)

    def test_none_5(self):
        @pedantic
        def calc(n: int, m: int, i: Union[int, None]) -> Optional[int]:
            return n + m + i if i is not None else None

        calc(n=42, m=40, i=None)

    def test_inheritance_1(self):
        class MyClassA:
            pass

        class MyClassB(MyClassA):
            pass

        @pedantic
        def calc(a: MyClassA) -> str:
            return str(a)

        calc(a=MyClassA())
        calc(a=MyClassB())

    def test_inheritance_2(self):
        """Problem here: A is not a subtype of B"""
        class MyClassA:
            pass

        class MyClassB(MyClassA):
            pass

        @pedantic
        def calc(a: MyClassB) -> str:
            return str(a)

        calc(a=MyClassB())
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(a=MyClassA())

    def test_instance_method_1(self):
        class MyClassA:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = MyClassA()
        a.calc(i=42)

    def test_instance_method_2(self):
        """Problem here: 'i' has no type annotation"""
        class MyClassA:
            @pedantic
            def calc(self, i) -> str:
                return str(i)

        a = MyClassA()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            a.calc(i=42)

    def test_instance_method_2_corrected(self):
        class MyClassA:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = MyClassA()
        a.calc(i=42)

    def test_instance_method_int_is_not_float(self):
        class MyClassA:
            @pedantic
            def calc(self, i: float) -> str:
                return str(i)

        a = MyClassA()
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            a.calc(i=42)

    def test_instance_method_3_corrected(self):
        class MyClassA:
            @pedantic
            def calc(self, i: float) -> str:
                return str(i)

        a = MyClassA()
        a.calc(i=42.0)

    def test_instance_method_no_kwargs(self):
        class MyClassA:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = MyClassA()
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            a.calc(42)

    def test_instance_method_5(self):
        """Problem here: instance methods is not called with kwargs"""
        class MyClassA:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = MyClassA()
        a.calc(i=42)

    def test_lambda_1(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            return lambda x: str(x * i)

        calc(i=42.0)(10.0)

    def test_lambda_3(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            def res(x: float) -> str:
                return str(x * i)
            return res

        calc(i=42.0)(10.0)

    def test_lambda_int_is_not_float(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            def res(x: int) -> str:
                return str(x * i)
            return res

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=42.0)(x=10)

    def test_lambda_4_almost_corrected(self):
        """Problem here: float != str"""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            @pedantic
            def res(x: int) -> str:
                return str(x * i)
            return res

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=42.0)(x=10)

    def test_lambda_4_almost_corrected_2(self):
        @pedantic
        def calc(i: float) -> Callable[[int], str]:
            @pedantic
            def res(x: int) -> str:
                return str(x * i)
            return res

        calc(i=42.0)(x=10)

    def test_lambda_5(self):
        """Problem here: float != int"""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            @pedantic
            def res(x: float) -> str:
                return str(x * i)
            return res

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=42.0)(x=10)

    def test_lambda_corrected(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            @pedantic
            def res(x: float) -> str:
                return str(x * i)

            return res

        calc(i=42.0)(x=10.0)

    def test_tuple_without_type_args(self):
        @pedantic
        def calc(i: Tuple) -> str:
            return str(i)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=(42.0, 43, 'hi'))

    def test_tuple_without_args_corrected(self):
        @pedantic
        def calc(i: Tuple[Any, ...]) -> str:
            return str(i)

        calc(i=(42.0, 43, 'hi'))

    def test_callable_without_type_args(self):
        @pedantic
        def calc(i: Callable) -> str:
            return str(i(' you'))

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=lambda x: (42.0, 43, 'hi', x))

    def test_callable_without_args_correct_with_lambdas(self):
        @pedantic
        def calc(i: Callable[[Any], Tuple[Any, ...]]) -> str:
            return str(i(x=' you'))

        calc(i=lambda x: (42.0, 43, 'hi', x))

    def test_callable_without_args_corrected(self):
        @pedantic
        def calc(i: Callable[[Any], Tuple[Any, ...]]) -> str:
            return str(i(x=' you'))

        @pedantic
        def arg(x: Any) -> Tuple[Any, ...]:
            return 42.0, 43, 'hi', x
        calc(i=arg)

    def test_list_without_args(self):
        @pedantic
        def calc(i: List) -> Any:
            return [i]

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(i=[42.0, 43, 'hi'])

    def test_list_without_args_corrected(self):
        @pedantic
        def calc(i: List[Any]) -> List[List[Any]]:
            return [i]

        calc(i=[42.0, 43, 'hi'])

    def test_ellipsis_in_callable_1(self):
        @pedantic
        def calc(i: Callable[..., int]) -> int:
            return i()

        @pedantic
        def call() -> int:
            return 42

        calc(i=call)

    def test_ellipsis_in_callable_2(self):
        @pedantic
        def calc(i: Callable[..., int]) -> int:
            return i(x=3.14, y=5)

        @pedantic
        def call(x: float, y: int) -> int:
            return 42

        calc(i=call)

    def test_ellipsis_in_callable_3(self):
        """Problem here: call to "call" misses one argument"""
        @pedantic
        def calc(i: Callable[..., int]) -> int:
            return i(x=3.14)

        @pedantic
        def call(x: float, y: int) -> int:
            return 42

        with self.assertRaises(expected_exception=PedanticException):
            calc(i=call)

    def test_optional_args_1(self):
        @pedantic
        def calc(a: int, b: int = 42) -> int:
            return a + b

        calc(a=2)

    def test_optional_args_2(self):
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

    def test_optional_args_3(self):
        """Problem here: optional argument c: 5 is not a float"""
        @pedantic
        def calc(a: int = 3, b: int = 42, c: float = 5) -> float:
            return a + b + c

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc()

    def test_optional_args_3_corrected(self):
        @pedantic
        def calc(a: int = 3, b: int = 42, c: float = 5.0) -> float:
            return a + b + c

        calc()

    def test_optional_args_4(self):
        class MyClass:
            @pedantic
            def foo(self, a: int, b: Optional[int] = 1) -> int:
                return a + b

        my_class = MyClass()
        my_class.foo(a=10)

    def test_optional_args_5(self):
        @pedantic
        def calc(d: Optional[Dict[int, int]] = None) -> Optional[int]:
            if d is None:
                return None
            return sum(d.keys())

        calc(d=None)
        calc()
        calc(d={42: 3})

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(d={42: 3.14})

    def test_optional_args_6(self):
        """"Problem here: str != int"""
        @pedantic
        def calc(d: int = 42) -> int:
            return int(d)

        calc(d=99999)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(d='999999')

    def test_enum_1(self):
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
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.operation(a=MyEnum.GAMMA)

    def test_enum_1_corrected(self):
        class MyEnum(Enum):
            ALPHA = 'startEvent'
            BETA = 'task'
            GAMMA = 'sequenceFlow'

        @pedantic
        def operation(a: MyEnum) -> None:
            print(a)

        operation(a=MyEnum.GAMMA)

    def test_sloppy_types_dict(self):
        @pedantic
        def operation(d: dict) -> int:
            return len(d.keys())

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d={1: 1, 2: 2})

    def test_sloppy_types_dict_almost_corrected_no_type_args(self):
        @pedantic
        def operation(d: Dict) -> int:
            return len(d.keys())

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d={1: 1, 2: 2})

    def test_sloppy_types_dict_corrected(self):
        @pedantic
        def operation(d: Dict[int, int]) -> int:
            return len(d.keys())

        operation(d={1: 1, 2: 2})

    def test_sloppy_types_list(self):
        @pedantic
        def operation(d: list) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=[1, 2, 3, 4])

    def test_sloppy_types_list_almost_corrected_no_type_args(self):
        @pedantic
        def operation(d: List) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=[1, 2, 3, 4])

    def test_sloppy_types_list_corrected(self):
        @pedantic
        def operation(d: List[int]) -> int:
            return len(d)

        operation(d=[1, 2, 3, 4])

    def test_sloppy_types_tuple(self):
        @pedantic
        def operation(d: tuple) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=(1, 2, 3))

    def test_sloppy_types_tuple_almost_corrected_no_type_args(self):
        @pedantic
        def operation(d: Tuple) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=(1, 2, 3))

    def test_sloppy_types_tuple_corrected(self):
        @pedantic
        def operation(d: Tuple[int, int, int]) -> int:
            return len(d)

        operation(d=(1, 2, 3))

    def test_sloppy_types_set(self):
        @pedantic
        def operation(d: set) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d={1, 2, 3})

    def test_sloppy_types_set_almost_corrected_to_type_args(self):
        @pedantic
        def operation(d: Set) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d={1, 2, 3})

    def test_sloppy_types_set_corrected(self):
        @pedantic
        def operation(d: Set[int]) -> int:
            return len(d)

        operation(d={1, 2, 3})

    def test_sloppy_types_frozenset(self):
        @pedantic
        def operation(d: frozenset) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=frozenset({1, 2, 3}))

    def test_sloppy_types_frozenset_almost_corrected_no_type_args(self):
        @pedantic
        def operation(d: FrozenSet) -> int:
            return len(d)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            operation(d=frozenset({1, 2, 3}))

    def test_sloppy_types_frozenset_corrected(self):
        @pedantic
        def operation(d: FrozenSet[int]) -> int:
            return len(d)

        operation(d=frozenset({1, 2, 3}))

    def test_type_list_but_got_tuple(self):
        @pedantic
        def calc(ls: List[Any]) -> int:
            return len(ls)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            calc(ls=(1, 2, 3))

    def test_type_list_corrected(self):
        @pedantic
        def calc(ls: Tuple[Any, ...]) -> int:
            return len(ls)

        calc(ls=(1, 2, 3))

    def test_any(self):
        @pedantic
        def calc(ls: List[Any]) -> Dict[int, Any]:
            return {i: ls[i] for i in range(0, len(ls))}

        calc(ls=[1, 2, 3])
        calc(ls=[1.11, 2.0, 3.0])
        calc(ls=['1', '2', '3'])
        calc(ls=[10.5, '2', (3, 4, 5)])

    def test_aliases(self):
        Vector = List[float]

        @pedantic
        def scale(scalar: float, vector: Vector) -> Vector:
            return [scalar * num for num in vector]

        scale(scalar=2.0, vector=[1.0, -4.2, 5.4])

    def test_new_type(self):
        UserId = NewType('UserId', int)

        @pedantic
        def get_user_name(user_id: UserId) -> str:
            return str(user_id)

        some_id = UserId(524313)
        get_user_name(user_id=some_id)

        # the following would be desirable but impossible to check at runtime:
        # with self.assertRaises(expected_exception=AssertionError):
        #     get_user_name(user_id=-1)

    def test_list_of_new_type(self):
        UserId = NewType('UserId', int)

        @pedantic
        def get_user_name(user_ids: List[UserId]) -> str:
            return str(user_ids)

        get_user_name(user_ids=[UserId(524313), UserId(42)])
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            get_user_name(user_ids=[UserId(524313), UserId(42), 430.0])

    def test_callable_no_args(self):
        @pedantic
        def f(g: Callable[[], str]) -> str:
            return g()

        @pedantic
        def greetings() -> str:
            return 'hello world'

        f(g=greetings)

    def test_type_var(self):
        T = TypeVar('T')

        @pedantic
        def first(ls: List[T]) -> T:
            return ls[0]

        first(ls=[1, 2, 3])

    def test_type_var_wrong(self):
        T = TypeVar('T')

        @pedantic
        def first(ls: List[T]) -> T:
            return str(ls[0])

        with self.assertRaises(expected_exception=PedanticTypeVarMismatchException):
            first(ls=[1, 2, 3])

    def test_type_var_wrong_sequence(self):
        T = TypeVar('T')

        @pedantic
        def first(ls: Sequence[T]) -> T:
            return str(ls[0])

        with self.assertRaises(expected_exception=PedanticTypeVarMismatchException):
            first(ls=[1, 2, 3])

    def test_double_pedantic(self):
        @pedantic
        @pedantic
        def f(x: int, y: float) -> Tuple[float, str]:
            return float(x), str(y)

        f(x=5, y=3.14)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            f(x=5.0, y=3.14)
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            f(5, 3.14)

    def test_args_kwargs(self):
        @pedantic
        def some_method(a: int = 0, b: float = 0.0) -> float:
            return a * b

        @pedantic
        def wrapper_method(*args: Union[int, float], **kwargs: Union[int, float]) -> float:
            return some_method(*args, **kwargs)

        some_method()
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            some_method(3, 3.0)
        some_method(a=3, b=3.0)
        wrapper_method()
        with self.assertRaises(expected_exception=PedanticCallWithArgsException):
            wrapper_method(3, 3.0)
        wrapper_method(a=3, b=3.0)

    def test_args_kwargs_no_type_hint(self):
        @pedantic
        def method_no_type_hint(*args, **kwargs) -> None:
            print(args)
            print(kwargs)

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            method_no_type_hint(a=3, b=3.0)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            method_no_type_hint()

    def test_args_kwargs_wrong_type_hint(self):
        """See: https://www.python.org/dev/peps/pep-0484/#arbitrary-argument-lists-and-default-argument-values"""
        @pedantic
        def wrapper_method(*args: str, **kwargs: str) -> None:
            print(args)
            print(kwargs)

        wrapper_method()
        wrapper_method('hi', 'you', ':)')
        wrapper_method(a='hi', b='you', c=':)')
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            wrapper_method('hi', 'you', ':)', 7)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            wrapper_method(3, 3.0)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            wrapper_method(a=3, b=3.0)

    def test_additional_kwargs(self):
        @pedantic
        def some_method(a: int, b: float = 0.0, **kwargs: int) -> float:
            return sum([a, b])

        some_method(a=5)
        some_method(a=5, b=0.1)
        some_method(a=5, b=0.1, c=4)
        some_method(a=5, b=0.1, c=4, d=5, e=6)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_method(a=5, b=0.1, c=4, d=5.0, e=6)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_method(a=5.0, b=0.1, c=4, d=5, e=6)
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            some_method(a=5, b=0, c=4, d=5, e=6)

    def test_args_kwargs_different_types(self):
        @pedantic
        def foo(*args: str, **kwds: int) -> None:
            print(args)
            print(kwds)

        foo('a', 'b', 'c')
        foo(x=1, y=2)
        foo('', z=0)

    def test_pedantic_on_class(self):
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            @pedantic
            class MyClass:
                pass
            MyClass()

    def test_is_subtype_tuple(self):
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            @pedantic
            def foo() -> Callable[[Tuple[float, str]], Tuple[int]]:
                def bar(a: Tuple[float]) -> Tuple[int]:
                    return len(a[1]) + int(a[0]),
                return bar
            foo()

    def test_is_subtype_tuple_corrected(self):
        @pedantic
        def foo() -> Callable[[Tuple[float, str]], Tuple[int]]:
            def bar(a: Tuple[float, str]) -> Tuple[int]:
                return len(a[1]) + int(a[0]),
            return bar
        foo()

    def test_forward_ref(self):
        class Conversation:
            pass

        @pedantic
        def get_conversations() -> List['Conversation']:
            return [Conversation(), Conversation()]

        get_conversations()

    def test_alternative_list_type_hint(self):
        @pedantic
        def _is_digit_in_int(digit: [int], num: int) -> bool:
            num_str = str(num)
            for i in num_str:
                if int(i) == digit:
                    return True
            return False

        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            _is_digit_in_int(digit=4, num=42)

    def test_callable_with_union_return(self):
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
