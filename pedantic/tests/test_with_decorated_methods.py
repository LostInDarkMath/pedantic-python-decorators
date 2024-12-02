import unittest
from functools import wraps

from pedantic import DecoratorType, create_decorator, WithDecoratedMethods


class Decorators(DecoratorType):
    FOO = '_foo'
    BAR = '_bar'


foo = create_decorator(decorator_type=Decorators.FOO)
bar = create_decorator(decorator_type=Decorators.BAR)


class TestWithDecoratedMethods(unittest.TestCase):
    def test_with_decorated_methods_sync(self):
        class MyClass(WithDecoratedMethods[Decorators]):
            @foo(42)
            def m1(self) -> None:
                print('bar')

            @foo(value=43)
            def m2(self) -> None:
                print('bar')

            @bar(value=44)
            def m3(self) -> None:
                print('bar')

        instance = MyClass()
        expected = {
            Decorators.FOO: {
                instance.m1: 42,
                instance.m2: 43,
            },
            Decorators.BAR: {
                instance.m3: 44,
            }
        }
        assert instance.get_decorated_functions() == expected

    def test_with_decorated_methods_async(self):
        class MyClass(WithDecoratedMethods[Decorators]):
            @foo(42)
            async def m1(self) -> None:
                print('bar')

            @foo(value=43)
            async def m2(self) -> None:
                print('bar')

            @bar(value=44)
            async def m3(self) -> None:
                print('bar')

        instance = MyClass()
        expected = {
            Decorators.FOO: {
                instance.m1: 42,
                instance.m2: 43,
            },
            Decorators.BAR: {
                instance.m3: 44,
            }
        }
        assert instance.get_decorated_functions() == expected


    def test_with_custom_transformation(self):
        def my_transformation(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                f(*args, **kwargs)
                return 4422  # we add a return value

            return wrapper

        my_decorator = create_decorator(decorator_type=Decorators.BAR, transformation=my_transformation)

        class MyClass(WithDecoratedMethods[Decorators]):
            @my_decorator(42)
            def m1(self) -> int:
                return 1

        instance = MyClass()
        expected = {
            Decorators.BAR: {
                instance.m1: 42,
            },
            Decorators.FOO: {},
        }
        assert instance.get_decorated_functions() == expected

        assert instance.m1() == 4422  # check that transformation was applied
