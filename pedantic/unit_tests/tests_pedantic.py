import unittest
from typing import List, Tuple, Callable, Any, Optional, Union, Dict, Set, FrozenSet, NewType, TypeVar, Sequence
from enum import Enum

# local file imports
from pedantic.method_decorators import pedantic


class TestDecoratorRequireKwargsAndTypeCheck(unittest.TestCase):

    def test_no_kwargs_1(self):
        """Problem here: function is not called with keyword arguments"""
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(42, 40, 38)

    def test_no_kwargs_2(self):
        """Problem here: function is not called with keyword arguments"""
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(42, m=40, i=38)

    def test_no_kwargs_1_2_corrected(self):
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        calc(n=42, m=40, i=38)

    def test_nested_type_hints_1(self):
        """Problem here: actual return type doesn't match return type annotation"""
        @pedantic
        def calc(n: int) -> List[List[float]]:
            return [0.0 * n]

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(n=42, m=40, i=None)

    def test_none_5(self):
        @pedantic
        def calc(n: int, m: int, i: Union[int, None]) -> Optional[int]:
            return n + m + i if i is not None else None

        calc(n=42, m=40, i=None)

    def test_inheritance_1(self):
        class A:
            pass

        class B(A):
            pass

        @pedantic
        def calc(a: A) -> str:
            return str(a)

        calc(a=A())
        calc(a=B())

    def test_inheritance_2(self):
        """Problem here: A is not a subtype of B"""
        class A:
            pass

        class B(A):
            pass

        @pedantic
        def calc(a: B) -> str:
            return str(a)

        calc(a=B())
        with self.assertRaises(expected_exception=AssertionError):
            calc(a=A())

    def test_instance_method_1(self):
        class A:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = A()
        a.calc(i=42)

    def test_instance_method_2(self):
        """Problem here: 'i' has no type annotation"""
        class A:
            @pedantic
            def calc(self, i) -> str:
                return str(i)

        a = A()
        with self.assertRaises(expected_exception=AssertionError):
            a.calc(i=42)

    def test_instance_method_2_corrected(self):
        class A:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = A()
        a.calc(i=42)

    def test_instance_method_3(self):
        """Problem here: float != int"""
        class A:
            @pedantic
            def calc(self, i: float) -> str:
                return str(i)

        a = A()
        with self.assertRaises(expected_exception=AssertionError):
            a.calc(i=42)

    def test_instance_method_3_corrected(self):
        class A:
            @pedantic
            def calc(self, i: float) -> str:
                return str(i)

        a = A()
        a.calc(i=42.0)

    def test_instance_method_4(self):
        """Problem here: instance methods is not called with kwargs"""
        class A:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = A()
        with self.assertRaises(expected_exception=AssertionError):
            a.calc(42)

    def test_instance_method_5(self):
        """Problem here: instance methods is not called with kwargs"""
        class A:
            @pedantic
            def calc(self, i: int) -> str:
                return str(i)

        a = A()
        a.calc(i=42)

    def test_lambda_1(self):
        """Lambda expressions cannot be typed hinted. So this leads to an error."""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            return lambda x: str(x * i)

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=42.0)(10.0)

    def test_lambda_2(self):
        """Even this is not expected by the type checker. Only test_lambda_3 has the 'correct' syntax"""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            res: Callable[[float], str] = lambda x: str(x * i)
            return res

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=42.0)(10.0)

    def test_lambda_3(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            def res(x: float) -> str:
                return str(x * i)
            return res

        calc(i=42.0)(10.0)

    def test_lambda_4(self):
        """Problem here: inner function: int != float"""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            def res(x: int) -> str:
                return str(x * i)
            return res

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=42.0)(x=10)

    def test_lambda_4_almost_corrected(self):
        """Problem here: float != str"""
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            @pedantic
            def res(x: int) -> str:
                return str(x * i)
            return res

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=42.0)(x=10)

    def test_lambda_corrected(self):
        @pedantic
        def calc(i: float) -> Callable[[float], str]:
            @pedantic
            def res(x: float) -> str:
                return str(x * i)

            return res

        calc(i=42.0)(x=10.0)

    def test_tuple_without_args(self):
        """Problem here: Tuple has no type arguments"""
        @pedantic
        def calc(i: Tuple) -> str:
            return str(i)

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=(42.0, 43, 'hi'))

    def test_tuple_without_args_corrected(self):
        @pedantic
        def calc(i: Tuple[Any, ...]) -> str:
            return str(i)

        calc(i=(42.0, 43, 'hi'))

    def test_callable_without_args(self):
        """Problem here: Callable has no type arguments"""
        @pedantic
        def calc(i: Callable) -> str:
            return str(i(' you'))

        with self.assertRaises(expected_exception=AssertionError):
            calc(i=lambda x: (42.0, 43, 'hi', x))

    def test_callable_without_args_almost_corrected(self):
        """Problem here: lambda expressions cannot be type hinted. So don't use it"""
        @pedantic
        def calc(i: Callable[[Any], Tuple[Any, ...]]) -> str:
            return str(i(x=' you'))

        with self.assertRaises(expected_exception=AssertionError):
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
        """Problem here: List has no type arguments"""
        @pedantic
        def calc(i: List) -> Any:
            return [i]

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(d={42: 3.14})

    def test_optional_args_6(self):
        """"Problem here: str != int"""
        @pedantic
        def calc(d: int = 42) -> int:
            return int(d)

        calc(d=99999)
        with self.assertRaises(expected_exception=AssertionError):
            calc(d='999999')

    def test_enum_1(self):
        """Problem here: Type hint for a should be MyEnum instead of MyEnum.GAMMA"""
        class MyEnum(Enum):
            ALPHA = 'startEvent'
            BETA = 'task'
            GAMMA = 'sequenceFlow'

        class MyClass:
            @pedantic
            def operation(self, a: MyEnum.GAMMA) -> None:
                print(a)

        m = MyClass()
        with self.assertRaises(expected_exception=AssertionError):
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
        """Problem here: use typing.Dict instead of dict"""
        @pedantic
        def operation(d: dict) -> int:
            return len(d.keys())

        with self.assertRaises(expected_exception=AssertionError):
            operation(d={1: 1, 2: 2})

    def test_sloppy_types_dict_almost_corrected(self):
        """Problem here: typing.Dict misses type arguments"""
        @pedantic
        def operation(d: Dict) -> int:
            return len(d.keys())

        with self.assertRaises(expected_exception=AssertionError):
            operation(d={1: 1, 2: 2})

    def test_sloppy_types_dict_corrected(self):
        @pedantic
        def operation(d: Dict[int, int]) -> int:
            return len(d.keys())

        operation(d={1: 1, 2: 2})

    def test_sloppy_types_list(self):
        """Problem here: use typing.List instead of list"""
        @pedantic
        def operation(d: list) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=[1, 2, 3, 4])

    def test_sloppy_types_list_almost_corrected(self):
        """Problem here: typing.List misses type argument"""
        @pedantic
        def operation(d: List) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=[1, 2, 3, 4])

    def test_sloppy_types_list_corrected(self):
        @pedantic
        def operation(d: List[int]) -> int:
            return len(d)

        operation(d=[1, 2, 3, 4])

    def test_sloppy_types_tuple(self):
        """Problem here: use typing.Tuple instead of tuple"""
        @pedantic
        def operation(d: tuple) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=(1, 2, 3))

    def test_sloppy_types_tuple_almost_corrected(self):
        """Problem here: typing.Tuple misses type arguments"""
        @pedantic
        def operation(d: Tuple) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=(1, 2, 3))

    def test_sloppy_types_tuple_corrected(self):
        @pedantic
        def operation(d: Tuple[int, int, int]) -> int:
            return len(d)

        operation(d=(1, 2, 3))

    def test_sloppy_types_set(self):
        """Problem here: use typing.Set instead of set"""
        @pedantic
        def operation(d: set) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d={1, 2, 3})

    def test_sloppy_types_set_almost_corrected(self):
        """Problem here: typing.Set misses type argument"""
        @pedantic
        def operation(d: Set) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d={1, 2, 3})

    def test_sloppy_types_set_corrected(self):
        @pedantic
        def operation(d: Set[int]) -> int:
            return len(d)

        operation(d={1, 2, 3})

    def test_sloppy_types_frozenset(self):
        """Problem here: use typing.FrozenSet instead of frozenset"""
        @pedantic
        def operation(d: frozenset) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=frozenset({1, 2, 3}))

    def test_sloppy_types_frozenset_almost_corrected(self):
        """Problem here: typing.FrozenSet misses type argument"""
        @pedantic
        def operation(d: FrozenSet) -> int:
            return len(d)

        with self.assertRaises(expected_exception=AssertionError):
            operation(d=frozenset({1, 2, 3}))

    def test_sloppy_types_frozenset_corrected(self):
        @pedantic
        def operation(d: FrozenSet[int]) -> int:
            return len(d)

        operation(d=frozenset({1, 2, 3}))

    def test_type_list(self):
        """Problem here: tuple != list"""
        @pedantic
        def calc(ls: List[Any]) -> int:
            return len(ls)

        with self.assertRaises(expected_exception=AssertionError):
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
        with self.assertRaises(expected_exception=AssertionError):
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

        with self.assertRaises(expected_exception=AssertionError):
            first(ls=[1, 2, 3])

    def test_type_var_wrong_sequence(self):
        T = TypeVar('T')

        @pedantic
        def first(ls: Sequence[T]) -> T:
            return str(ls[0])

        with self.assertRaises(expected_exception=AssertionError):
            first(ls=[1, 2, 3])


if __name__ == '__main__':
    test = TestDecoratorRequireKwargsAndTypeCheck()
    test.test_type_var_wrong()
