"""This file was taken from: https://github.com/agronholm/typeguard/blob/master/tests/test_typeguard.py"""
import types
from functools import wraps, lru_cache
from io import StringIO, BytesIO
from unittest.mock import Mock, MagicMock
from typing import (
    Any, Callable, Dict, List, Set, Tuple, Union, TypeVar, Sequence, NamedTuple, Iterable,
    Container, Generic, BinaryIO, TextIO, Generator, Iterator, AbstractSet, Type, Optional)

import pytest
from typing_extensions import NoReturn, Protocol, Literal, TypedDict, runtime_checkable

from pedantic import pedantic_class
from pedantic.exceptions import PedanticTypeCheckException
from pedantic.decorators.fn_deco_pedantic import pedantic

try:
    from typing import Collection
except ImportError:
    # Python 3.6.0+
    Collection = None


TBound = TypeVar('TBound', bound='Parent')
TConstrained = TypeVar('TConstrained', 'Parent', 'Child')
JSONType = Union[str, int, float, bool, None, List['JSONType'], Dict[str, 'JSONType']]

DummyDict = TypedDict('DummyDict', {'x': int}, total=False)
issue_42059 = pytest.mark.xfail(bool(DummyDict.__required_keys__),
                                reason='Fails due to upstream bug BPO-42059')
del DummyDict


class Parent:
    pass


class Child(Parent):
    def method(self, a: int):
        pass


class StaticProtocol(Protocol):
    def meth(self) -> None:
        ...


@runtime_checkable
class RuntimeProtocol(Protocol):
    def meth(self) -> None:
        ...


@pytest.fixture(params=[Mock, MagicMock], ids=['mock', 'magicmock'])
def mock_class(request):
    return request.param


class TestCheckArgumentTypes:
    def test_any_type(self):
        @pedantic
        def foo(a: Any) -> None:
            pass

        foo(a='aa')

    def test_callable_exact_arg_count(self):
        @pedantic
        def foo(a: Callable[[int, str], int]) -> None:
            pass

        def some_callable(x: int, y: str) -> int:
            pass

        foo(a=some_callable)

    def test_callable_bad_type(self):
        @pedantic
        def foo(a: Callable[..., int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_callable_too_few_arguments(self):
        @pedantic
        def foo(a: Callable[[int, str], int]) -> None:
            pass

        def some_callable(x: int) -> int:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=some_callable)

    def test_callable_too_many_arguments(self):
        @pedantic
        def foo(a: Callable[[int, str], int]) -> None:
            pass

        def some_callable(x: int, y: str, z: float) -> int:
            pass

        exc = pytest.raises(PedanticTypeCheckException, foo, a=some_callable)

    def test_callable_mandatory_kwonlyargs(self):
        @pedantic
        def foo(a: Callable[[int, str], int]) -> None:
            pass

        def some_callable(x: int, y: str, *, z: float, bar: str) -> int:
            pass

        exc = pytest.raises(PedanticTypeCheckException, foo, a=some_callable)

    def test_callable_class(self):
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

    def test_callable_plain(self):
        @pedantic
        def foo(a: Callable[..., Any]) -> None:
            pass

        def callback(a):
            pass

        foo(a=callback)


    def test_callable_bound_method(self):
        """
        Test that passing a bound method as a callable does not count the "self" argument "a"gainst
        the ones declared in the Callable specification.

        """
        @pedantic
        def foo(callback: Callable[[int], Any]) -> None:
            pass

        foo(callback=Child().method)

    def test_callable_defaults(self):
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

    def test_callable_builtin(self):
        @pedantic
        def foo(callback: types.BuiltinFunctionType) -> None:
            pass

        foo(callback=[].append)

    def test_dict_bad_type(self):
        @pedantic
        def foo(a: Dict[str, int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_dict_bad_key_type(self):
        @pedantic
        def foo(a: Dict[str, int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a={1: 2})

    def test_dict_bad_value_type(self):
        @pedantic
        def foo(a: Dict[str, int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a={'x': 'a'})

    def test_list_bad_type(self):
        @pedantic
        def foo(a: List[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_list_bad_element(self):
        @pedantic
        def foo(a: List[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=[1, 2, 'bb'])

    def test_sequence_bad_type(self):
        @pedantic
        def foo(a: Sequence[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_sequence_bad_element(self):
        @pedantic
        def foo(a: Sequence[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=[1, 2, 'bb'])

    def test_abstractset_custom_type(self):
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

    def test_abstractset_bad_type(self):
        @pedantic
        def foo(a: AbstractSet[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_set_bad_type(self):
        @pedantic
        def foo(a: Set[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_abstractset_bad_element(self):
        @pedantic
        def foo(a: AbstractSet[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a={1, 2, 'bb'})

    def test_set_bad_element(self):
        @pedantic
        def foo(a: Set[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a={1, 2, 'bb'})

    def test_tuple_bad_type(self):
        @pedantic
        def foo(a: Tuple[int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=5)

    def test_tuple_too_many_elements(self):
        @pedantic
        def foo(a: Tuple[int, str]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=(1, 'aa', 2))

    def test_tuple_too_few_elements(self):
        @pedantic
        def foo(a: Tuple[int, str]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=(1,))

    def test_tuple_bad_element(self):
        @pedantic
        def foo(a: Tuple[int, str]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=(1, 2))

    def test_tuple_ellipsis_bad_element(self):
        @pedantic
        def foo(a: Tuple[int, ...]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=(1, 2, 'blah'))

    def test_namedtuple(self):
        Employee = NamedTuple('Employee', [('name', str), ('id', int)])

        @pedantic
        def foo(bar: Employee) -> None:
            pass

        foo(bar=Employee('bob', 1))

    def test_namedtuple_type_mismatch(self):
        Employee = NamedTuple('Employee', [('name', str), ('id', int)])

        @pedantic
        def foo(bar: Employee) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, bar=('bob', 1))

    def test_namedtuple_wrong_field_type(self):
        Employee = NamedTuple('Employee', [('name', str), ('id', int)])

        @pedantic
        def foo(bar: Employee) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, bar=Employee(2, 1))

    @pytest.mark.parametrize('value', [6, 'aa'])
    def test_union(self, value):
        @pedantic
        def foo(a: Union[str, int]) -> None:
            pass

        foo(a=value)

    def test_union_typing_type(self):
        @pedantic
        def foo(a: Union[str, Collection]) -> None:
            pass

        with pytest.raises(PedanticTypeCheckException):
            foo(a=1)

    @pytest.mark.parametrize('value', [6.5, b'aa'])
    def test_union_fail(self, value):
        @pedantic
        def foo(a: Union[str, int]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=value)

    @pytest.mark.parametrize('values', [
        {'a': 6, 'b': 7},
        {'a': 'aa', 'b' : "bb"}
    ], ids=['int', 'str'])
    def test_type_var_constraints(self, values):
        T = TypeVar('T', int, str)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        foo(**values)

    def test_type_var_constraints_fail_typing_type(self):
        T = TypeVar('T', int, Collection)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        with pytest.raises(PedanticTypeCheckException):
            foo(a='aa', b='bb')

    def test_typevar_constraints_fail(self):
        T = TypeVar('T', int, str)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=2.5, b='aa')

    def test_typevar_bound(self):
        T = TypeVar('T', bound=Parent)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        foo(a=Child(), b=Child())

    def test_type_var_bound_fail(self):
        T = TypeVar('T', bound=Child)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=Parent(), b=Parent())

    def test_type_var_invariant_fail(self):
        T = TypeVar('T', int, str)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=2, b=3.6)

    def test_type_var_covariant(self):
        T = TypeVar('T', covariant=True)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        foo(a=Parent(), b=Child())

    def test_type_var_covariant_fail(self):
        T = TypeVar('T', covariant=True)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=Child(), b=Parent())

    def test_type_var_contravariant(self):
        T = TypeVar('T', contravariant=True)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        foo(a=Child(), b=Parent())

    def test_type_var_contravariant_fail(self):
        T = TypeVar('T', contravariant=True)

        @pedantic
        def foo(a: T, b: T) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=Parent(), b=Child())

    @pytest.mark.skipif(Type is List, reason='typing.Type could not be imported')
    def test_class_bad_subclass(self):
        @pedantic
        def foo(a: Type[Child]) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=Parent)

    def test_class_any(self):
        @pedantic
        def foo(a: Type[Any]) -> None:
            pass

        foo(a=str)

    def test_wrapped_function(self):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper

        @pedantic
        @decorator
        def foo(a: 'Child') -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=Parent())

    def test_mismatching_default_type(self):
        @pedantic
        def foo(a: str = 1) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo)

    def test_implicit_default_none(self):
        """
        Test that if the default value is ``None``, a ``None`` argument can be passed.

        """
        @pedantic
        def foo(a: Optional[str] = None) -> None:
            pass

        foo()

    def test_generator(self):
        """Test that argument type checking works in a generator function too."""
        @pedantic
        def generate(a: int) -> Generator[int]:
            yield a
            yield a + 1

        gen = generate(1)
        next(gen)

    def test_wrapped_generator_no_return_type_annotation(self):
        """Test that return type checking works in a generator function too."""
        @pedantic
        def generate(a: int) -> Generator[int]:
            yield a
            yield a + 1

        gen = generate(a=1)
        next(gen)

    def test_varargs(self):
        @pedantic
        def foo(*args: int) -> None:
            pass

        foo(1, 2)

    def test_varargs_fail(self):
        @pedantic
        def foo(*args: int) -> None:
            pass

        exc = pytest.raises(PedanticTypeCheckException, foo, 1, 'a')

    def test_kwargs(self):
        @pedantic
        def foo(**kwargs: int) -> None:
            pass

        foo(a=1, b=2)

    def test_kwargs_fail(self):
        @pedantic
        def foo(**kwargs: int) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=1, b='a')

    def test_generic(self):
        T_Foo = TypeVar('T_Foo')

        class FooGeneric(Generic[T_Foo]):
            pass

        @pedantic
        def foo(a: FooGeneric[str]) -> None:
            pass

        foo(a=FooGeneric[str]())

    def test_newtype(self):
        try:
            from typing import NewType
        except ImportError:
            pytest.skip('Skipping newtype test since no NewType in current typing library')

        myint = NewType("myint", int)

        @pedantic
        def foo(a: myint) -> int:
            return 42

        assert foo(a=1) == 42
        pytest.raises(PedanticTypeCheckException, foo, a="a")

    @pytest.mark.skipif(Collection is None, reason='typing.Collection is not available')
    def test_collection(self):
        @pedantic
        def foo(a: Collection) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=True)

    def test_binary_io(self):
        @pedantic
        def foo(a: BinaryIO) -> None:
            pass

        foo(a=BytesIO())

    def test_text_io(self):
        @pedantic
        def foo(a: TextIO) -> None:
            pass

        foo(a=StringIO())

    def test_binary_io_fail(self):
        @pedantic
        def foo(a: TextIO) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=BytesIO())

    def test_text_io_fail(self):
        @pedantic
        def foo(a: BinaryIO) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, a=StringIO())

    def test_binary_io_real_file(self, tmpdir):
        @pedantic
        def foo(a: BinaryIO) -> None:
            pass

        with tmpdir.join('testfile').open('wb') as f:
            foo(a=f)

    def test_text_io_real_file(self, tmpdir):
        @pedantic
        def foo(a: TextIO) -> None:
            pass

        with tmpdir.join('testfile').open('w') as f:
            foo(a=f)

    def test_recursive_type(self):
        @pedantic
        def foo(arg: JSONType) -> None:
            pass

        foo(arg={'a': [1, 2, 3]})
        pytest.raises(PedanticTypeCheckException, foo, arg={'a': (1, 2, 3)})


class TestPedantic:
    def test_pedantic(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        assert foo(a=4, b='abc') == 'abc'

    def test_pedantic_always(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        assert foo(a=4, b='abc') == 'abc'

    def test_pedantic_arguments_fail(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 'abc'

        pytest.raises(PedanticTypeCheckException, foo, a=4, b=5)

    def test_pedantic_return_type_fail(self):
        @pedantic
        def foo(a: int, b: str) -> str:
            return 6

        pytest.raises(PedanticTypeCheckException, foo, a=4, b='abc')

    def test_pedantic_return_type_var_fail(self):
        T = TypeVar('T', int, float)

        @pedantic
        def foo(a: T, b: T) -> T:
            return 'a'

        pytest.raises(PedanticTypeCheckException, foo, a=4, b=2)

    def test_return_type_none(self):
        """Check that a declared return type of None is respected."""
        @pedantic
        def foo() -> None:
            return 'a'

        pytest.raises(PedanticTypeCheckException, foo)

    def test_return_type_magicmock(self, mock_class):
        @pedantic
        def foo() -> str:
            return mock_class()

        foo()

    @pytest.mark.parametrize('typehint', [
        Callable[..., int],
        Callable
    ], ids=['parametrized', 'unparametrized'])
    def test_callable(self, typehint):
        @pedantic
        def foo(a: typehint):
            pass

        def some_callable() -> int:
            pass

        foo(a=some_callable)

    @pytest.mark.parametrize('typehint', [
        List[int],
        List,
        list,
    ], ids=['parametrized', 'unparametrized', 'plain'])
    def test_list(self, typehint):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=[1, 2])

    @pytest.mark.parametrize('typehint', [
        Dict[str, int],
        Dict,
        dict
    ], ids=['parametrized', 'unparametrized', 'plain'])
    def test_dict(self, typehint):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a={'x': 2})

    @pytest.mark.parametrize('typehint, value', [
        (Dict, {'x': 2, 6: 4}),
        (List, ['x', 6]),
        (Sequence, ['x', 6]),
        (Set, {'x', 6}),
        (AbstractSet, {'x', 6}),
        (Tuple, ('x', 6)),
    ], ids=['dict', 'list', 'sequence', 'set', 'abstractset', 'tuple'])
    def test_unparametrized_types_mixed_values(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    @pytest.mark.parametrize('typehint', [
        Sequence[str],
        Sequence
    ], ids=['parametrized', 'unparametrized'])
    @pytest.mark.parametrize('value', [('a', 'b'), ['a', 'b'], 'abc'],
                             ids=['tuple', 'list', 'str'])
    def test_sequence(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    @pytest.mark.parametrize('typehint', [
        Iterable[str],
        Iterable
    ], ids=['parametrized', 'unparametrized'])
    @pytest.mark.parametrize('value', [('a', 'b'), ['a', 'b'], 'abc'],
                             ids=['tuple', 'list', 'str'])
    def test_iterable(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    @pytest.mark.parametrize('typehint', [
        Container[str],
        Container
    ], ids=['parametrized', 'unparametrized'])
    @pytest.mark.parametrize('value', [('a', 'b'), ['a', 'b'], 'abc'],
                             ids=['tuple', 'list', 'str'])
    def test_container(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    @pytest.mark.parametrize('typehint', [
        AbstractSet[int],
        AbstractSet,
        Set[int],
        Set,
        set
    ], ids=['abstract_parametrized', 'abstract', 'parametrized', 'unparametrized', 'plain'])
    @pytest.mark.parametrize('value', [set(), {6}])
    def test_set(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    @pytest.mark.parametrize('typehint', [
        Tuple[int, int],
        Tuple[int, ...],
        Tuple,
        tuple
    ], ids=['parametrized', 'ellipsis', 'unparametrized', 'plain'])
    def test_tuple(self, typehint):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=(1, 2))

    def test_empty_tuple(self):
        @pedantic
        def foo(a: Tuple[()]):
            pass

        foo(a=())

    @pytest.mark.skipif(Type is List, reason='typing.Type could not be imported')
    @pytest.mark.parametrize('typehint', [
        Type[Parent],
        Type[TypeVar('UnboundType')],  # noqa: F821
        Type[TypeVar('BoundType', bound=Parent)],  # noqa: F821
        Type,
        type
    ], ids=['parametrized', 'unbound-typevar', 'bound-typevar', 'unparametrized', 'plain'])
    def test_class(self, typehint):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=Child)

    @pytest.mark.skipif(Type is List, reason='typing.Type could not be imported')
    def test_class_not_a_class(self):
        @pedantic
        def foo(a: Type[dict]):
            pass

        exc = pytest.raises(TypeError, foo, 1)
        exc.match('type of argument "a" must be a type; got int instead')

    @pytest.mark.parametrize('typehint, value', [
        (complex, complex(1, 5)),
        (complex, 1.0),
        (complex, 1),
        (float, 1.0),
        (float, 1)
    ], ids=['complex-complex', 'complex-float', 'complex-int', 'float-float', 'float-int'])
    def test_numbers(self, typehint, value):
        @pedantic
        def foo(a: typehint):
            pass

        foo(a=value)

    def test_coroutine_correct_return_type(self):
        @pedantic
        async def foo() -> str:
            return 'foo'

        coro = foo()
        pytest.raises(StopIteration, coro.send, None)

    def test_coroutine_wrong_return_type(self):
        @pedantic
        async def foo() -> str:
            return 1

        coro = foo()
        pytest.raises(TypeError, coro.send, None).\
            match('type of the return value must be str; got int instead')

    def test_bytearray_bytes(self):
        """Test that a bytearray is accepted where bytes are expected."""
        @pedantic
        def foo(x: bytes) -> None:
            pass

        foo(x=bytearray([1]))

    def test_class_decorator(self):
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

        pytest.raises(PedanticTypeCheckException, Foo.staticmethod)
        pytest.raises(PedanticTypeCheckException, Foo.classmethod)
        pytest.raises(PedanticTypeCheckException, Foo().method)

    @pytest.mark.parametrize('annotation', [
        Generator[int, str, List[str]],
        Generator,
        Iterable[int],
        Iterable,
        Iterator[int],
        Iterator
    ], ids=['generator', 'bare_generator', 'iterable', 'bare_iterable', 'iterator',
            'bare_iterator'])
    def test_generator(self, annotation):
        @pedantic
        def genfunc() -> annotation:
            val1 = yield 2
            val2 = yield 3
            val3 = yield 4
            return [val1, val2, val3]

        gen = genfunc()
        with pytest.raises(StopIteration) as exc:
            value = next(gen)
            while True:
                value = gen.send(str(value))
                assert isinstance(value, int)

        assert exc.value.value == ['2', '3', '4']

    @pytest.mark.parametrize('annotation', [
        Generator[int, str, None],
        Iterable[int],
        Iterator[int]
    ], ids=['generator', 'iterable', 'iterator'])
    def test_generator_bad_yield(self, annotation):
        @pedantic
        def genfunc() -> annotation:
            yield 'foo'

        gen = genfunc()
        with pytest.raises(PedanticTypeCheckException):
            next(gen)

    def test_generator_bad_send(self):
        @pedantic
        def genfunc() -> Generator[int, str, None]:
            yield 1
            yield 2

        gen = genfunc()
        next(gen)
        with pytest.raises(PedanticTypeCheckException):
            gen.send(2)

    def test_generator_bad_return(self):
        @pedantic
        def genfunc() -> Generator[int, str, str]:
            yield 1
            return 6

        gen = genfunc()
        next(gen)
        with pytest.raises(PedanticTypeCheckException):
            gen.send('foo')

    def test_return_generator(self):
        @pedantic
        def genfunc() -> Generator[int, None, None]:
            yield 1

        @pedantic
        def foo() -> Generator[int, None, None]:
            return genfunc()

        foo()

    def test_builtin_decorator(self):
        @pedantic
        @lru_cache()
        def func(x: int) -> None:
            pass

        func(3)
        func(3)
        pytest.raises(PedanticTypeCheckException, func, 'foo')

        # Make sure that @lru_cache is still being used
        cache_info = func.__wrapped__.cache_info()
        assert cache_info.hits == 1

    def test_local_class(self):
        @pedantic_class
        class LocalClass:
            class Inner:
                pass

            def create_inner(self) -> 'Inner':
                return self.Inner()

        retval = LocalClass().create_inner()
        assert isinstance(retval, LocalClass.Inner)

    def test_local_class_async(self):
        @pedantic_class
        class LocalClass:
            class Inner:
                pass

            async def create_inner(self) -> 'Inner':
                return self.Inner()

        coro = LocalClass().create_inner()
        exc = pytest.raises(StopIteration, coro.send, None)
        retval = exc.value.value
        assert isinstance(retval, LocalClass.Inner)

    def test_callable_nonmember(self):
        class CallableClass:
            def __call__(self):
                pass

        @pedantic_class
        class LocalClass:
            some_callable = CallableClass()

    def test_inherited_class_method(self):
        @pedantic_class
        class Parent:
            @classmethod
            def foo(cls, x: str) -> str:
                return cls.__name__

        @pedantic_class
        class Child(Parent):
            pass

        assert Child.foo('bar') == 'Child'
        pytest.raises(PedanticTypeCheckException, Child.foo, 1)

    def test_decorator_factory_no_annotations(self):
        class CallableClass:
            def __call__(self):
                pass

        def decorator_factory():
            def decorator(f):
                cmd = CallableClass()
                return cmd

            return decorator

        with pytest.warns(UserWarning):
            @pedantic
            @decorator_factory()
            def foo():
                pass

    @pytest.mark.parametrize('annotation', [TBound, TConstrained], ids=['bound', 'constrained'])
    def test_type_var_forward_ref(self, annotation):
        @pedantic
        def func(x: annotation) -> None:
            pass

        func(Parent())
        func(Child())
        pytest.raises(TypeError, func, x='foo')

    @pytest.mark.parametrize('protocol_cls', [RuntimeProtocol, StaticProtocol])
    def test_protocol(self, protocol_cls):
        @pedantic
        def foo(arg: protocol_cls) -> None:
            pass

        class Foo:
            def meth(self) -> None:
                pass

        foo(arg=Foo())

    def test_protocol_fail(self):
        @pedantic
        def foo(arg: RuntimeProtocol) -> None:
            pass

        pytest.raises(PedanticTypeCheckException, foo, arg=object())

    def test_noreturn(self):
        @pedantic
        def foo() -> NoReturn:
            pass

        pytest.raises(PedanticTypeCheckException, foo)

    def test_recursive_type(self):
        @pedantic
        def foo(arg: JSONType) -> None:
            pass

        foo({'a': [1, 2, 3]})
        pytest.raises(PedanticTypeCheckException, foo, arg={'a': (1, 2, 3)})

    def test_literal(self):
        from http import HTTPStatus

        @pedantic
        def foo(a: Literal[1, True, 'x', b'y', HTTPStatus.ACCEPTED]):
            pass

        foo(HTTPStatus.ACCEPTED)
        pytest.raises(PedanticTypeCheckException, foo, a=4)

    def test_literal_union(self):
        @pedantic
        def foo(a: Union[str, Literal[1, 6, 8]]):
            pass

        foo(a=6)
        pytest.raises(PedanticTypeCheckException, foo, a=4)

    def test_literal_nested(self):
        @pedantic
        def foo(a: Literal[1, Literal['x', 'a', Literal['z']], 6, 8]):
            pass

        foo(a='z')
        pytest.raises(PedanticTypeCheckException, foo, a=4)

    def test_literal_illegal_value(self):
        @pedantic
        def foo(a: Literal[1, 1.1]):
            pass

        pytest.raises(TypeError, foo, a=4)

    @pytest.mark.parametrize('value, total, error_re', [
        pytest.param({'x': 6, 'y': 'foo'}, True, None, id='correct'),
        pytest.param({'y': 'foo'}, True, r'required key\(s\) \("x"\) missing from argument "arg"',
                     id='missing_x'),
        pytest.param({'x': 6, 'y': 3}, True,
                     'type of dict item "y" for argument "arg" must be str; got int instead',
                     id='wrong_y'),
        pytest.param({'x': 6}, True, r'required key\(s\) \("y"\) missing from argument "arg"',
                     id='missing_y_error'),
        pytest.param({'x': 6}, False, None, id='missing_y_ok', marks=[issue_42059]),
        pytest.param({'x': 'abc'}, False,
                     'type of dict item "x" for argument "arg" must be int; got str instead',
                     id='wrong_x', marks=[issue_42059]),
        pytest.param({'x': 6, 'foo': 'abc'}, False, r'extra key\(s\) \("foo"\) in argument "arg"',
                     id='unknown_key')
    ])
    def test_typed_dict(self, value, total, error_re):
        DummyDict = TypedDict('DummyDict', {'x': int, 'y': str}, total=total)

        @pedantic
        def foo(arg: DummyDict):
            pass

        if error_re:
            pytest.raises(TypeError, foo, arg=value)
        else:
            foo(arg=value)
