import unittest

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
                42: instance.m1,
                43: instance.m2,
            },
            Decorators.BAR: {
                44: instance.m3,
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
                42: instance.m1,
                43: instance.m2,
            },
            Decorators.BAR: {
                44: instance.m3,
            }
        }
        assert instance.get_decorated_functions() == expected
