import unittest
from typing import List, Tuple, Callable, Any, Optional, Union

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

    def test_nested_type_hints_corrected(self):
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
            def f(x: int, y: float) -> Tuple[float, str]:
                return n * float(x), str(y)
            return f

    def test_all_ok_7(self):
        @pedantic
        def calc(n: List[List[float]]) -> Any:
            return n[0][0]

        calc(n=[[42.0]])
        self.assertTrue(True)

    def test_all_ok_8(self):
        @pedantic
        def calc(n: int) -> Callable[[int, float], Tuple[float, str]]:
            @pedantic
            def f(x: int, y: float) -> Tuple[float, str]:
                return n * float(x), str(y)

            return f

        calc(n=42)(x=3, y=3.14)

    def test_sloppy_type_hints_1(self):
        @pedantic
        def calc(ls: list) -> int:
            return len(ls)

        calc(ls=[1, 2, 3])
        calc(ls=[1.11, 2.0, 3.0])
        calc(ls=['1', '2', '3'])
        calc(ls=[10.5, '2', (3, 4, 5)])

    def test_sloppy_type_hints_2(self):
        """Problem here: tuple != list"""
        @pedantic
        def calc(ls: list) -> int:
            return len(ls)

        with self.assertRaises(expected_exception=AssertionError):
            calc(ls=(1, 2, 3))

    def test_sloppy_type_hints_2_corrected(self):
        """Problem here: tuple != list"""
        @pedantic
        def calc(ls: tuple) -> int:
            return len(ls)

        calc(ls=(1, 2, 3))

    def test_sloppy_type_hints_3(self):
        """Problem here: str != int"""
        @pedantic
        def calc(ls: list) -> int:
            return str(len(ls))

        with self.assertRaises(expected_exception=AssertionError):
            calc(ls=[1, 2, 3])

    def test_sloppy_type_hints_3_corrected(self):
        @pedantic
        def calc(ls: list) -> str:
            return str(len(ls))

        calc(ls=[1, 2, 3])

    def test_sloppy_type_hints_4(self):
        @pedantic
        def calc(ls: list) -> dict:
            return {i: ls[i] for i in range(0, len(ls))}

        calc(ls=[1, 2, 3])
        calc(ls=[1.11, 2.0, 3.0])
        calc(ls=['1', '2', '3'])
        calc(ls=[10.5, '2', (3, 4, 5)])

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
            n + m + i

        calc(n=42, m=40, i=38)

    def test_wrong_type_hint_4(self):
        """Problem here: None != int"""
        @pedantic
        def calc(n: int, m: int, i: int) -> int:
            n + m + i

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

    def test_instance_method_4(self):
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
        """Problem here: inner function needs to use @pedantic"""
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

    def test_lambda_4_almost_corrected(self):
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


if __name__ == '__main__':
    # run a specific unit test
    test = TestDecoratorRequireKwargsAndTypeCheck()
    test.test_callable_without_args()
