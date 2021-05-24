import unittest

from pedantic.models.decorated_function import DecoratedFunction


class TestDecoratedFunction(unittest.TestCase):
    def test_static_method(self):
        def f_1():
            pass

        deco_f = DecoratedFunction(f_1)
        self.assertFalse(deco_f.is_static_method)

        class MyClass:
            def f_1(self):
                pass

            @staticmethod
            def f_2():
                pass

            @classmethod
            def f_3(cls):
                pass

        deco_f_1 = DecoratedFunction(MyClass.f_1)
        deco_f_2 = DecoratedFunction(MyClass.f_2)
        deco_f_3 = DecoratedFunction(MyClass.f_3)

        self.assertFalse(deco_f_1.is_static_method)
        self.assertTrue(deco_f_2.is_static_method)
        self.assertFalse(deco_f_3.is_static_method)

    def test_function_wants_args(self):
        def f_1(*args, **kwargs):
            pass

        def f_2(a, b, *args, **kwargs):
            pass

        def f_3(a, b, *args):
            pass

        def f_4(*args):
            pass

        def f_5():
            pass

        self.assertTrue(DecoratedFunction(f_1).wants_args)
        self.assertTrue(DecoratedFunction(f_2).wants_args)
        self.assertTrue(DecoratedFunction(f_3).wants_args)
        self.assertTrue(DecoratedFunction(f_4).wants_args)
        self.assertFalse(DecoratedFunction(f_5).wants_args)

        class MyClass:
            def f(self):
                pass

            @staticmethod
            def g():
                pass

        self.assertFalse(DecoratedFunction(MyClass.f).wants_args)
        self.assertFalse(DecoratedFunction(MyClass.g).wants_args)

    def test_is_property_setter(self):
        def f_1():
            pass

        self.assertFalse(DecoratedFunction(f_1).is_property_setter)

        class MyClass:
            _h = 42

            def f_1(self):
                pass

            @staticmethod
            def f_2():
                pass

        self.assertFalse(DecoratedFunction(MyClass.f_1).is_property_setter)
        self.assertFalse(DecoratedFunction(MyClass.f_2).is_property_setter)

    def test_wants_kwargs(self):
        def f_1(*args, **kwargs):
            pass

        def f_2(a, b, *args, **kwargs):
            pass

        def f_3(a, b, *args):
            pass

        def f_4(*args):
            pass

        def f_5():
            pass

        def f_6(a, b, c):
            pass

        self.assertFalse(DecoratedFunction(f_1).should_have_kwargs)
        self.assertFalse(DecoratedFunction(f_2).should_have_kwargs)
        self.assertFalse(DecoratedFunction(f_3).should_have_kwargs)
        self.assertFalse(DecoratedFunction(f_4).should_have_kwargs)
        self.assertTrue(DecoratedFunction(f_5).should_have_kwargs)
        self.assertTrue(DecoratedFunction(f_6).should_have_kwargs)

        class A:
            def f(self):
                pass

            @staticmethod
            def g():
                pass

            def __compare__(self, other):
                pass

        self.assertTrue(DecoratedFunction(A.f).should_have_kwargs)
        self.assertTrue(DecoratedFunction(A.g).should_have_kwargs)
        self.assertFalse(DecoratedFunction(A.__compare__).should_have_kwargs)

    def test_instance_method(self):
        def h():
            pass

        self.assertFalse(DecoratedFunction(h).is_instance_method)

        class A:
            def f(self):
                pass

            @staticmethod
            def g():
                pass

        self.assertTrue(DecoratedFunction(A.f).is_instance_method)
        self.assertFalse(DecoratedFunction(A.g).is_instance_method)

    def test_num_decorators(self):
        def decorator(f):
            return f

        def f_1():
            pass

        @decorator
        def f_2():
            pass

        @decorator
        @decorator
        def f_3():
            pass

        @decorator
        @decorator
        @decorator
        def f_4():
            pass

        self.assertEqual(DecoratedFunction(f_1).num_of_decorators, 0)
        self.assertEqual(DecoratedFunction(f_2).num_of_decorators, 1)
        self.assertEqual(DecoratedFunction(f_3).num_of_decorators, 2)
        self.assertEqual(DecoratedFunction(f_4).num_of_decorators, 3)
