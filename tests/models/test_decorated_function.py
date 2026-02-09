from pedantic.models.decorated_function import DecoratedFunction


def test_static_method():
    def f_1(): pass

    deco_f = DecoratedFunction(f_1)
    assert deco_f.is_static_method is False

    class MyClass:
        def f_1(self): pass

        @staticmethod
        def f_2(): pass

        @classmethod
        def f_3(cls): pass

    deco_f_1 = DecoratedFunction(MyClass.f_1)
    deco_f_2 = DecoratedFunction(MyClass.f_2)
    deco_f_3 = DecoratedFunction(MyClass.f_3)

    assert deco_f_1.is_static_method is False
    assert deco_f_2.is_static_method is True
    assert deco_f_3.is_static_method is False


def test_function_wants_args():
    def f_1(*args, **kwargs): pass

    def f_2(a, b, *args, **kwargs): pass

    def f_3(a, b, *args): pass

    def f_4(*args): pass

    def f_5(): pass

    assert DecoratedFunction(f_1).wants_args is True
    assert DecoratedFunction(f_2).wants_args is True
    assert DecoratedFunction(f_3).wants_args is True
    assert DecoratedFunction(f_4).wants_args is True
    assert DecoratedFunction(f_5).wants_args is False

    class MyClass:
        def f(self): pass

        @staticmethod
        def g(): pass

    assert DecoratedFunction(MyClass.f).wants_args is False
    assert DecoratedFunction(MyClass.g).wants_args is False


def test_is_property_setter():
    def f_1(): pass

    assert DecoratedFunction(f_1).is_property_setter is False

    class MyClass:
        _h = 42

        def f_1(self): pass

        @staticmethod
        def f_2(): pass

    assert DecoratedFunction(MyClass.f_1).is_property_setter is False
    assert DecoratedFunction(MyClass.f_2).is_property_setter is False


def test_wants_kwargs():
    def f_1(*args, **kwargs): pass

    def f_2(a, b, *args, **kwargs): pass

    def f_3(a, b, *args): pass

    def f_4(*args): pass

    def f_5(): pass

    def f_6(a, b, c): pass

    assert DecoratedFunction(f_1).should_have_kwargs is False
    assert DecoratedFunction(f_2).should_have_kwargs is False
    assert DecoratedFunction(f_3).should_have_kwargs is False
    assert DecoratedFunction(f_4).should_have_kwargs is False
    assert DecoratedFunction(f_5).should_have_kwargs is True
    assert DecoratedFunction(f_6).should_have_kwargs is True

    class A:
        def f(self): pass

        @staticmethod
        def g(): pass

        def __compare__(self, other): pass

    assert DecoratedFunction(A.f).should_have_kwargs is True
    assert DecoratedFunction(A.g).should_have_kwargs is True
    assert DecoratedFunction(A.__compare__).should_have_kwargs is False


def test_instance_method():
    def h(): pass

    assert DecoratedFunction(h).is_instance_method is False

    class A:
        def f(self): pass

        @staticmethod
        def g(): pass

    assert DecoratedFunction(A.f).is_instance_method is True
    assert DecoratedFunction(A.g).is_instance_method is False


def test_num_decorators():
    def decorator(f):
        return f

    def f_1(): pass

    @decorator
    def f_2(): pass

    @decorator
    @decorator
    def f_3(): pass

    @decorator
    @decorator
    @decorator
    def f_4():
        pass

    assert DecoratedFunction(f_1).num_of_decorators == 0
    assert DecoratedFunction(f_2).num_of_decorators == 1
    assert DecoratedFunction(f_3).num_of_decorators == 2
    assert DecoratedFunction(f_4).num_of_decorators == 3
