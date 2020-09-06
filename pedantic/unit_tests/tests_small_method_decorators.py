import unittest
import warnings

# local file imports
from pedantic.custom_exceptions import TooDirtyException, NotImplementedException
from pedantic.method_decorators import overrides, deprecated, needs_refactoring, dirty, timer, count_calls, \
    unimplemented, validate_args, require_not_none, require_not_empty_strings, trace, trace_if_returns, \
    does_same_as_function


class TestSmallDecoratorMethods(unittest.TestCase):

    def test_overrides(self):
        """Problem here: parent has no such method"""
        class A:
            pass

        with self.assertRaises(expected_exception=AssertionError):
            class B(A):
                @overrides(A)
                def operation(self):
                    return 42

    def test_overrides_corrected(self):
        class A:
            def operation(self):
                pass

        class B(A):
            @overrides(A)
            def operation(self):
                return 42

        b = B()
        b.operation()

    def test_overrides_static_method(self):
        class A:
            @staticmethod
            def operation():
                pass

        class B(A):
            @staticmethod
            @overrides(A)
            def operation():
                return 42

        b = B()
        self.assertEqual(b.operation(), 42)
        self.assertEqual(B.operation(), 42)

    def test_deprecated_1(self):
        @deprecated
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "deprecated" in str(w[-1].message)

    def test_deprecated_2(self):
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert not len(w) == 1

    def test_needs_refactoring_1(self):
        @needs_refactoring
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "refactoring" in str(w[-1].message)

    def test_needs_refactoring_2(self):
        def old_method(i: int) -> str:
            return str(i)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_method(42)
            assert not len(w) == 1

    def test_dirty(self):
        @dirty
        def dirt(i: int) -> str:
            return str(i)

        with self.assertRaises(expected_exception=TooDirtyException):
            dirt(42)

    def test_unimplemented(self):
        @unimplemented
        def dirt(i: int) -> str:
            return str(i)

        with self.assertRaises(expected_exception=NotImplementedException):
            dirt(42)

    def test_timer(self):
        @timer
        def operation(i: int) -> str:
            return str(i)

        operation(42)

    def test_count_calls(self):
        @count_calls
        def operation(i: int) -> str:
            return str(i)

        operation(42)

    def test_validate_args(self):
        @validate_args(lambda x: (x > 42, f'Each arg should be > 42, but it was {x}.'))
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation(43, 45, 50)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(30, 40, 50)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(c=30, a=40, b=50)

    def test_validate_args_instance_method(self):
        class MyClass:
            @validate_args(lambda x: (x > 0, f'Argument should be greater then 0, but it was {x}.'))
            def some_calculation(self, x: int) -> int:
                return x

        m = MyClass()
        m.some_calculation(1)
        m.some_calculation(42)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(0)
        with self.assertRaises(expected_exception=AssertionError):
            m.some_calculation(-42)

    def test_require_not_none(self):
        @require_not_none
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation(43, 0, -50)
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation(30, None, 50)

    def test_require_not_empty_strings(self):
        @require_not_empty_strings
        def some_calculation(a, b, c):
            return a + b + c

        some_calculation('Hello', 'My', 'World   !')
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation('Hello', '   ', 'World')
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation('Hello', 4, 'World')
        with self.assertRaises(expected_exception=AssertionError):
            some_calculation('Hello', '4', None)

    def test_trace(self):
        def some_method(x, y):
            return x + y
        traced_method = trace(some_method)
        self.assertEqual(some_method(42, 99), traced_method(42, 99))

    def test_trace_if_returns(self):
        def some_method(x, y):
            return x + y
        traced_method = trace_if_returns(100)(some_method)
        self.assertEqual(some_method(42, 99), traced_method(42, 99))
        self.assertEqual(some_method(42, 58), traced_method(42, 58))

    def test_does_same_as_function(self):
        def some_method(x, y, z):
            return x * (y + z)

        @does_same_as_function(some_method)
        def other_method(x, y, z):
            return x * y + x * z

        other_method(1, 2, 3)
        other_method(4, 5, 6)

    def test_does_same_as_function_wrong(self):
        def some_method(x, y, z):
            return x * (y + z)

        @does_same_as_function(some_method)
        def other_method(x, y, z):
            return x * y + z

        other_method(0, 2, 0)
        with self.assertRaises(expected_exception=AssertionError):
            other_method(4, 5, 6)
