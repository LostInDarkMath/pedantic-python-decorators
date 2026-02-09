from typing import TypeVar, Generic, List, Type

import pytest

from pedantic import GenericMixin

A = TypeVar('A')
E = TypeVar('E')
S = TypeVar('S')
T = TypeVar('T')
U = TypeVar('U')


def test_single_type_var():
    class Foo(Generic[T], GenericMixin):
        value: T

    foo = Foo[str]()
    assert foo.type_var == str
    assert foo.type_vars == {T: str}

    invalid = Foo()

    with pytest.raises(expected_exception=AssertionError) as err:
        invalid.type_var

    assert f'You need to instantiate this class with type parameters! Example: Foo[int]()' in err.value.args[0]


def test_multiple_type_vars():
    class Foo(Generic[T, U], GenericMixin):
        value: T
        values: List[U]

    foo = Foo[str, int]()

    with pytest.raises(expected_exception=AssertionError) as err:
       foo.type_var

    assert 'You have multiple type parameters. Please use "type_vars" instead of "type_var".' in err.value.args[0]

    assert foo.type_vars == {T: str, U: int}

    invalid = Foo()

    with pytest.raises(expected_exception=AssertionError) as err:
        invalid.type_var

    assert 'You need to instantiate this class with type parameters! Example: Foo[int]()' in err.value.args[0]


def test_non_generic_class():
    class Foo(GenericMixin):
        value: int

    invalid = Foo()

    with pytest.raises(expected_exception=AssertionError) as err:
        invalid.type_var

    assert err.value.args[0] == 'Foo is not a generic class. To make it generic, declare it like: class Foo(Generic[T], GenericMixin):...'


def test_call_type_var_in_constructor():
    class Foo(Generic[T], GenericMixin):
        def __init__(self) -> None:
            self.x = self.type_var()

    with pytest.raises(expected_exception=AssertionError) as err:
        Foo[str]()

    assert 'make sure that you do not call this in the __init__() method' in err.value.args[0]


def test_subclass_set_type_variable():
    class Gen(Generic[T], GenericMixin):
        def __init__(self, value: T) -> None:
            self.value = value

        def get_type(self) -> dict[TypeVar, Type]:
            return self.type_vars

    class MyClass(Gen[int]):
        pass

    bar = Gen[int](value=4)
    assert bar.get_type() == {T: int}

    foo = MyClass(value=4)
    assert foo.get_type() == {T: int}


def test_subclass_with_multiple_parents():
    class Gen(Generic[T], GenericMixin):
        def __init__(self, value: T) -> None:
            self.value = value

        def get_type(self) -> dict[TypeVar, Type]:
            return self.type_vars

    class MyMixin:
        value = 42

    class MyClass(MyMixin, Gen[int]):
        pass

    bar = Gen[int](value=4)
    assert bar.get_type() == {T: int}

    foo = MyClass(value=4)
    assert foo.get_type() == {T: int}


def test_resolved_type_var_inheritance():
    class Foo(Generic[T]): ...

    class Bar(Foo[int], Generic[U], GenericMixin): ...

    bar = Bar[str]()
    assert bar.type_vars == {T: int, U: str}

def test_resolved_type_var_inheritance_2():
    class Foo(Generic[T], GenericMixin): ...

    class Bar(Foo[int], Generic[U]): ...

    bar = Bar[str]()
    assert bar.type_vars == {T: int, U: str}

def test_very_complex_inheritance():
    class Foo(Generic[E], GenericMixin): ...
    class Bar(Foo[int], Generic[S]): ...
    class Baz(Foo[int]): ...
    class Deep(Baz): ...
    class Deeper(Baz, Generic[T]): ...

    foo = Foo[str]()
    actual = foo.type_vars
    assert actual == {E: str}

    bar = Bar[str]()
    actual = bar.type_vars
    assert actual == {E: int, S: str}

    baz = Baz()
    actual = baz.type_vars
    assert actual == {E: int}

    deep = Deep()
    actual = deep.type_vars
    assert actual == {E: int}

    deeper = Deeper[bool]()
    actual = deeper.type_vars
    assert actual == {E: int, T: bool}

    with pytest.raises(expected_exception=AssertionError) as err:
        Foo().type_vars

    assert 'You need to instantiate this class with type parameters! Example: Foo[int]()' in err.value.args[0]


def test_substitution_lookup_hits():
    class Base(Generic[A], GenericMixin): ...
    class Mid(Base[A], Generic[A]): ...
    class Final(Mid[int]): ...

    obj = Final()
    actual = obj.type_vars
    assert actual == {A: int}
