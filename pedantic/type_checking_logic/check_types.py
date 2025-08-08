"""Idea is taken from: https://stackoverflow.com/a/55504010/10975692"""
import inspect
import types
import typing
from io import BytesIO, StringIO, BufferedWriter, TextIOWrapper
from typing import Any, Dict, Iterable, ItemsView, Callable, Optional, Tuple, Mapping, TypeVar, NewType, \
    _ProtocolMeta
import collections

from pedantic.type_checking_logic.resolve_forward_ref import resolve_forward_ref
from pedantic.constants import TypeVar as TypeVar_, TYPE_VAR_SELF
from pedantic.exceptions import PedanticTypeCheckException, PedanticTypeVarMismatchException, PedanticException


def assert_value_matches_type(
        value: Any,
        type_: Any,
        err: str,
        type_vars: Dict[TypeVar_, Any],
        key: Optional[str] = None,
        msg: Optional[str] = None,
        context: Dict[str, Any] = None,
) -> None:
    if not _check_type(value=value, type_=type_, err=err, type_vars=type_vars, context=context):
        t = type(value)
        value = f'{key}={value}' if key is not None else str(value)

        if not msg:
            msg = f'{err}Type hint is incorrect: Argument {value} of type {t} does not match expected type {type_}.'

        raise PedanticTypeCheckException(msg)


def _check_type(value: Any, type_: Any, err: str, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import List, Union, Optional, Callable, Any
        >>> _check_type(5, int, '', {})
        True
        >>> _check_type(5, float, '', {})
        False
        >>> _check_type('hi', str, '', {})
        True
        >>> _check_type(None, str, '', {})
        False
        >>> _check_type(None, Any, '', {})
        True
        >>> _check_type(None, None, '', {})
        True
        >>> _check_type(5, Any, '', {})
        True
        >>> _check_type(3.1415, float, '', {})
        True
        >>> _check_type([1, 2, 3, 4], List[int], '', {})
        True
        >>> _check_type([1, 2, 3.0, 4], List[int], '', {})
        False
        >>> _check_type([1, 2, 3.0, 4], List[float], '', {})
        False
        >>> _check_type([1, 2, 3.0, 4], List[Union[float, int]], '', {})
        True
        >>> _check_type([[True, False], [False], [True], []], List[List[bool]], '', {})
        True
        >>> _check_type([[True, False, 1], [False], [True], []], List[List[bool]], '', {})
        False
        >>> _check_type(5, Union[int, float, bool], '', {})
        True
        >>> _check_type(5.0, Union[int, float, bool], '', {})
        True
        >>> _check_type(False, Union[int, float, bool], '', {})
        True
        >>> _check_type('5', Union[int, float, bool], '', {})
        False
        >>> def f(a: int, b: bool, c: str) -> float: pass
        >>> _check_type(f, Callable[[int, bool, str], float], '', {})
        True
        >>> _check_type(None, Optional[List[Dict[str, float]]], '', {})
        True
        >>> _check_type([{'a': 1.2, 'b': 3.4}], Optional[List[Dict[str, float]]], '', {})
        True
        >>> _check_type([{'a': 1.2, 'b': 3}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> _check_type({'a': 1.2, 'b': 3.4}, Optional[List[Dict[str, float]]], '', {})
        False
        >>> _check_type([{'a': 1.2, 7: 3.4}], Optional[List[Dict[str, float]]], '', {})
        False
        >>> class MyClass: pass
        >>> _check_type(MyClass(), 'MyClass', '', {})
        True
        >>> _check_type(MyClass(), 'MyClas', '', {})
        False
        >>> _check_type([1, 2, 3], list, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException:  Missing type arguments
        >>> _check_type((1, 2, 3), tuple, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException:  Missing type arguments
        >>> _check_type({1: 1.0, 2: 2.0, 3: 3.0}, dict, '', {})
        Traceback (most recent call last):
        ...
        pedantic.exceptions.PedanticTypeCheckException:  Missing type arguments
    """

    if type_ is None:
        return value == type_
    elif isinstance(type_, str):
        class_name = value.__class__.__name__
        base_class_name = value.__class__.__base__.__name__
        return class_name == type_ or base_class_name == type_

    try:
        return _is_instance(obj=value, type_=type_, type_vars=type_vars, context=context)
    except PedanticTypeCheckException as ex:
        raise PedanticTypeCheckException(f'{err} {ex}')
    except PedanticTypeVarMismatchException as ex:
        raise PedanticTypeVarMismatchException(f'{err} {ex}')
    except (AttributeError, Exception) as ex:
        raise PedanticTypeCheckException(
            f'{err}An error occurred during type hint checking. Value: {value} Annotation: '
            f'{type_} Mostly this is caused by an incorrect type annotation. Details: {ex} ')


def _is_instance(obj: Any, type_: Any, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    context = context or {}

    if not _has_required_type_arguments(type_):
        raise PedanticTypeCheckException(
            f'The type annotation "{type_}" misses some type arguments e.g. '
            f'"typing.Tuple[Any, ...]" or "typing.Callable[..., str]".')

    if type_.__module__ == 'typing':
        if _is_generic(type_):
            origin = get_base_generic(type_)
        else:
            origin = type_

        name = _get_name(origin)

        if name in _SPECIAL_INSTANCE_CHECKERS:
            validator = _SPECIAL_INSTANCE_CHECKERS[name]
            return validator(obj, type_, type_vars, context)

    if hasattr(types, 'UnionType') and isinstance(type_, types.UnionType):
        return _instancecheck_union(value=obj, type_=type_, type_vars=type_vars, context=context)

    if type_ == typing.BinaryIO:
        return isinstance(obj, (BytesIO, BufferedWriter))
    elif type_ == typing.TextIO:
        return isinstance(obj, (StringIO, TextIOWrapper))
    elif type_ == typing.NoReturn:
        return False  # we expect an Exception here, but got a value
    elif hasattr(typing, 'Never') and type_ == typing.Never:  # since Python 3.11
        return False  # we expect an Exception here, but got a value
    elif hasattr(typing, 'LiteralString') and type_ == typing.LiteralString:  # since Python 3.11
        return isinstance(obj, str)  # we cannot distinguish str and LiteralString at runtime
    elif hasattr(typing, 'Self') and type_ == typing.Self:  # since Python 3.11
        t = type_vars[TYPE_VAR_SELF]

        if t is None:
            return False  # the case if a function outside a class was type hinted with self

        return _is_instance(obj=obj, type_=t, type_vars=type_vars, context=context)

    if isinstance(type_, TypeVar):
        constraints = type_.__constraints__

        if len(constraints) > 0 and type(obj) not in constraints:
            return False

        if _is_forward_ref(type_=type_.__bound__):
            resolved = resolve_forward_ref(type_.__bound__.__forward_arg__, context=context)
            return _is_instance(obj=obj, type_=resolved, type_vars=type_vars, context=context)

        if type_.__bound__ is not None and not isinstance(obj, type_.__bound__):
            return False

        if type_ in type_vars:
            other = type_vars[type_]

            if type_.__contravariant__:
                if not _is_subtype(sub_type=other, super_type=obj.__class__):
                    raise PedanticTypeVarMismatchException(
                        f'For TypeVar {type_} exists a type conflict: value {obj} has type {type(obj)} but TypeVar {type_} '
                        f'was previously matched to type {other}')
            else:
                if not _is_instance(obj=obj, type_=other, type_vars=type_vars, context=context):
                    raise PedanticTypeVarMismatchException(
                        f'For TypeVar {type_} exists a type conflict: value {obj} has type {type(obj)} but TypeVar {type_} '
                        f'was previously matched to type {other}')

        type_vars[type_] = type(obj)
        return True

    if hasattr(typing, 'Unpack') and getattr(type_, '__origin__', None) == typing.Unpack:
        return True  # it's too hard to check that at the moment

    if _is_generic(type_):
        python_type = type_.__origin__

        if not isinstance(obj, python_type):
            return False

        base = get_base_generic(type_)
        type_args = get_type_arguments(cls=type_)

        if base in _ORIGIN_TYPE_CHECKERS:
            validator = _ORIGIN_TYPE_CHECKERS[base]
            return validator(obj, type_args, type_vars, context)

        assert base.__base__ == typing.Generic, f'Unknown base: {base}'
        return isinstance(obj, base)

    if _is_forward_ref(type_=type_):
        resolved = resolve_forward_ref(type_.__forward_arg__, context=context)
        return _is_instance(obj=obj, type_=resolved, type_vars=type_vars, context=context)

    if _is_type_new_type(type_):
        return isinstance(obj, type_.__supertype__)

    if hasattr(obj, '_asdict'):
        if hasattr(type_, '_field_types'):
            field_types = type_._field_types
        elif hasattr(type_, '__annotations__'):
            field_types = type_.__annotations__
        else:
            return False

        if not obj._asdict().keys() == field_types.keys():
            return False

        return all([_is_instance(obj=obj._asdict()[k], type_=v, type_vars=type_vars, context=context) for k, v in field_types.items()])

    if type_ in {list, set, dict, frozenset, tuple, type}:
        raise PedanticTypeCheckException('Missing type arguments')

    if isinstance(type_, types.GenericAlias):
        return _is_instance(obj=obj, type_=convert_to_typing_types(type_), type_vars=type_vars, context=context)

    try:
        return isinstance(obj, type_)
    except TypeError:
        if type(type_) == _ProtocolMeta:
            return True  # we do not check this

        raise


def _is_forward_ref(type_: Any) -> bool:
    return hasattr(typing, 'ForwardRef') and isinstance(type_, typing.ForwardRef) or \
            hasattr(typing, '_ForwardRef') and isinstance(type_, typing._ForwardRef)


def _is_type_new_type(type_: Any) -> bool:
    """
        >>> from typing import Tuple, Callable, Any, List, NewType
        >>> _is_type_new_type(int)
        False
        >>> UserId = NewType('UserId', int)
        >>> _is_type_new_type(UserId)
        True
    """

    if type(type_) == typing.NewType:
        return True

    return type_.__qualname__ == NewType('name', int).__qualname__  # arguments of NewType() are arbitrary here


def _get_name(cls: Any) -> str:
    """
        >>> from typing import Tuple, Callable, Any, List
        >>> _get_name(int)
        'int'
        >>> _get_name(Any)
        'Any'
        >>> _get_name(List)
        'List'
        >>> _get_name(List[int])
        'List'
        >>> _get_name(List[Any])
        'List'
        >>> _get_name(Tuple)
        'Tuple'
        >>> _get_name(Tuple[int, float])
        'Tuple'
        >>> _get_name(Tuple[Any, ...])
        'Tuple'
        >>> _get_name(Callable)
        'Callable'
    """
    if hasattr(cls, '_name'):
        return cls._name
    elif hasattr(cls, '__name__'):
        return cls.__name__
    else:
        return type(cls).__name__[1:]


def _is_generic(cls: Any) -> bool:
    """
        >>> from typing import  List, Callable, Any, Union
        >>> _is_generic(int)
        False
        >>> _is_generic(List)
        True
        >>> _is_generic(List[int])
        True
        >>> _is_generic(List[Any])
        True
        >>> _is_generic(List[List[int]])
        True
        >>> _is_generic(Any)
        False
        >>> _is_generic(Tuple)
        True
        >>> _is_generic(Tuple[Any, ...])
        True
        >>> _is_generic(Tuple[str, float, int])
        True
        >>> _is_generic(Callable)
        True
        >>> _is_generic(Callable[[int], int])
        True
        >>> _is_generic(Union)
        True
        >>> _is_generic(Union[int, float, str])
        True
        >>> _is_generic(Dict)
        True
        >>> _is_generic(Dict[str, str])
        True
    """

    if hasattr(typing, '_SpecialGenericAlias') and isinstance(cls, typing._SpecialGenericAlias):
        return True
    elif isinstance(cls, typing._GenericAlias):
        return True
    elif isinstance(cls, typing._SpecialForm):
        return cls not in {Any}

    return False


def _has_required_type_arguments(cls: Any) -> bool:
    """
        >>> from typing import List, Callable, Tuple, Any
        >>> _has_required_type_arguments(int)
        True
        >>> _has_required_type_arguments(List)
        False
        >>> _has_required_type_arguments(List[int])
        True
        >>> _has_required_type_arguments(List[List[int]])
        True
        >>> _has_required_type_arguments(Tuple)
        False
        >>> _has_required_type_arguments(Tuple[int])
        True
        >>> _has_required_type_arguments(Tuple[int, float, str])
        True
        >>> _has_required_type_arguments(Callable)
        False
        >>> _has_required_type_arguments(Callable[[int, float], Tuple[float, str]])
        True
        >>> _has_required_type_arguments(Callable[..., Any])
        True
        >>> _has_required_type_arguments(Callable[[typing.Any], Tuple[typing.Any, ...]],)
        True
    """

    base: str = _get_name(cls=cls)
    num_type_args = len(get_type_arguments(cls=cls))

    if base in NUM_OF_REQUIRED_TYPE_ARGS_EXACT:
        return NUM_OF_REQUIRED_TYPE_ARGS_EXACT[base] == num_type_args
    elif base in NUM_OF_REQUIRED_TYPE_ARGS_MIN:
        return NUM_OF_REQUIRED_TYPE_ARGS_MIN[base] <= num_type_args
    return True


def get_type_arguments(cls: Any) -> Tuple[Any, ...]:
    """ Works similar to typing.args()
        >>> from typing import Tuple, List, Union, Callable, Any, NewType, TypeVar, Optional, Awaitable, Coroutine
        >>> get_type_arguments(int)
        ()
        >>> get_type_arguments(List[float])
        (<class 'float'>,)
        >>> get_type_arguments(List[int])
        (<class 'int'>,)
        >>> UserId = NewType('UserId', int)
        >>> get_type_arguments(List[UserId])
        (pedantic.type_checking_logic.check_types.UserId,)
        >>> get_type_arguments(List)
        ()
        >>> T = TypeVar('T')
        >>> get_type_arguments(List[T])
        (~T,)
        >>> get_type_arguments(List[List[int]])
        (typing.List[int],)
        >>> get_type_arguments(List[List[List[int]]])
        (typing.List[typing.List[int]],)
        >>> get_type_arguments(List[Tuple[float, str]])
        (typing.Tuple[float, str],)
        >>> get_type_arguments(List[Tuple[Any, ...]])
        (typing.Tuple[typing.Any, ...],)
        >>> Union[bool, int, float]
        typing.Union[bool, int, float]
        >>> get_type_arguments(Union[str, float, int])
        (<class 'str'>, <class 'float'>, <class 'int'>)
        >>> get_type_arguments(Union[str, float, List[int], int])
        (<class 'str'>, <class 'float'>, typing.List[int], <class 'int'>)
        >>> get_type_arguments(Callable)
        ()
        >>> get_type_arguments(Callable[[int, float], Tuple[float, str]])
        ([<class 'int'>, <class 'float'>], typing.Tuple[float, str])
        >>> get_type_arguments(Callable[..., str])
        (Ellipsis, <class 'str'>)
        >>> get_type_arguments(Optional[int])
        (<class 'int'>, <class 'NoneType'>)
        >>> get_type_arguments(str | int)
        (<class 'str'>, <class 'int'>)
        >>> get_type_arguments(Awaitable[str])
        (<class 'str'>,)
        >>> get_type_arguments(Coroutine[int, bool, str])
        (<class 'int'>, <class 'bool'>, <class 'str'>)
    """

    result = ()

    if hasattr(cls, '__args__'):
        result = cls.__args__
        origin = get_base_generic(cls=cls)

        if origin != cls and \
                ((origin is Callable) or (origin is collections.abc.Callable)) and \
                result[0] is not Ellipsis:
            result = (list(result[:-1]), result[-1])

    result = result or ()

    if hasattr(types, 'UnionType') and isinstance(cls, types.UnionType):
        return result
    elif '[' in str(cls):
        return result

    return ()


def get_base_generic(cls: Any) -> Any:
    """
        >>> from typing import List, Union, Tuple, Callable, Dict, Set, Awaitable, Coroutine
        >>> get_base_generic(List)
        typing.List
        >>> get_base_generic(List[float])
        typing.List
        >>> get_base_generic(List[List[float]])
        typing.List
        >>> get_base_generic(List[Union[int, float]])
        typing.List
        >>> get_base_generic(Tuple)
        typing.Tuple
        >>> get_base_generic(Tuple[float, int])
        typing.Tuple
        >>> get_base_generic(Tuple[Union[int, float], str])
        typing.Tuple
        >>> get_base_generic(Callable[..., int])
        typing.Callable
        >>> get_base_generic(Callable[[Union[int, str], float], int])
        typing.Callable
        >>> get_base_generic(Dict)
        typing.Dict
        >>> get_base_generic(Dict[str, str])
        typing.Dict
        >>> get_base_generic(Union)
        typing.Union
        >>> get_base_generic(Union[float, int, str])
        typing.Union
        >>> get_base_generic(Set)
        typing.Set
        >>> get_base_generic(Set[int])
        typing.Set
        >>> get_base_generic(Awaitable[int])
        typing.Awaitable
        >>> get_base_generic(Coroutine[None, None, int])
        typing.Coroutine
    """

    origin = cls.__origin__ if hasattr(cls, '__origin__') else None
    name = cls._name if hasattr(cls, '_name') else None

    if name is not None:
        return getattr(typing, name)
    elif origin is not None:
        return origin
    return cls


def _is_subtype(sub_type: Any, super_type: Any, context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Any, List, Callable, Tuple, Union, Optional, Iterable
        >>> _is_subtype(float, float)
        True
        >>> _is_subtype(int, float)
        False
        >>> _is_subtype(float, int)
        False
        >>> _is_subtype(int, Any)
        True
        >>> _is_subtype(Any, int)
        False
        >>> _is_subtype(Any, Any)
        True
        >>> _is_subtype(Ellipsis, Ellipsis)
        True
        >>> _is_subtype(Tuple[float, str], Tuple[float, str])
        True
        >>> _is_subtype(Tuple[float], Tuple[float, str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[Any, ...])
        True
        >>> _is_subtype(Tuple[Any, ...], Tuple[float, str])
        False
        >>> _is_subtype(Tuple[float, str], Tuple[int, ...])
        False
        >>> _is_subtype(Tuple[int, str], Tuple[int, ...])
        True
        >>> _is_subtype(Tuple[int, ...], Tuple[int, str])
        False
        >>> _is_subtype(Tuple[float, str, bool, int], Tuple[Any, ...])
        True
        >>> _is_subtype(int, Union[int, float])
        True
        >>> _is_subtype(int, Union[str, float])
        False
        >>> _is_subtype(List[int], List[Union[int, float]])
        True
        >>> _is_subtype(List[Union[int, float]], List[int])
        Traceback (most recent call last):
        ...
        TypeError: issubclass() arg 1 must be a class
        >>> class Parent: pass
        >>> class Child(Parent): pass
        >>> _is_subtype(List[Child], List[Parent])
        True
        >>> _is_subtype(List[Parent], List[Child])
        False
        >>> _is_subtype(List[int], Iterable[int])
        True
        >>> _is_subtype(Iterable[int], List[int])
        False
        >>> class MyClass: pass
        >>> _is_subtype(MyClass, Union[str, MyClass])
        True
        >>> _is_subtype(None, type(None))
        True
        >>> _is_subtype(None, Any)
        True
        >>> _is_subtype(Optional[int], Optional[int])
        True
        >>> _is_subtype(Optional[int], Union[int, float, None])
        True
        >>> _is_subtype(int | None, int | None)
        True
        >>> _is_subtype(int, int | None)
        True
        >>> _is_subtype(int | None, int)
        False
    """

    if sub_type is None:
        sub_type = type(None)

    python_sub = _get_class_of_type_annotation(sub_type)
    python_super = _get_class_of_type_annotation(super_type)

    if python_super is object:
        return True

    if python_super == typing.Union or isinstance(python_super, types.UnionType):
        type_args = get_type_arguments(cls=super_type)

        if python_sub == typing.Union or isinstance(python_sub, types.UnionType):
            sub_type_args = get_type_arguments(cls=sub_type)
            return all([x in type_args for x in sub_type_args])

        if any([type(ta) == _ProtocolMeta for ta in type_args]):
            return True  # shortcut

        return sub_type in type_args

    if not _is_generic(sub_type):
        try:
            return issubclass(python_sub, python_super)
        except TypeError:
            if type(python_super) == _ProtocolMeta:
                return True

            return False

    if not issubclass(python_sub, python_super):
        return False

    sub_args = get_type_arguments(cls=sub_type)
    super_args = get_type_arguments(cls=super_type)

    if len(sub_args) != len(super_args) and Ellipsis not in sub_args + super_args:
        return False

    return all(_is_subtype(sub_type=sub_arg, super_type=super_arg, context=context) for sub_arg, super_arg in zip(sub_args, super_args))


def _get_class_of_type_annotation(annotation: Any) -> Any:
    """
        >>> from typing import Dict, List, Any, Tuple, Callable, Union
        >>> _get_class_of_type_annotation(int)
        <class 'int'>
        >>> _get_class_of_type_annotation(Any)
        <class 'object'>
        >>> _get_class_of_type_annotation(Ellipsis)
        <class 'object'>
        >>> _get_class_of_type_annotation(Dict)
        <class 'dict'>
        >>> _get_class_of_type_annotation(Dict[str, int])
        <class 'dict'>
        >>> _get_class_of_type_annotation(List)
        <class 'list'>
        >>> _get_class_of_type_annotation(List[int])
        <class 'list'>
        >>> _get_class_of_type_annotation(Tuple)
        <class 'tuple'>
        >>> _get_class_of_type_annotation(Tuple[int, int])
        <class 'tuple'>
        >>> _get_class_of_type_annotation(Callable[[int], int])
        <class 'collections.abc.Callable'>
        >>> _get_class_of_type_annotation(Callable)
        <class 'collections.abc.Callable'>
    """

    if annotation in [Any, Ellipsis]:
        return object
    elif annotation.__module__ == 'typing' and annotation.__origin__ is not None:
        return annotation.__origin__

    return annotation


def _instancecheck_iterable(iterable: Iterable, type_args: Tuple, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import List, Any, Union
        >>> _instancecheck_iterable([1.0, -4.2, 5.4], (float,), {})
        True
        >>> _instancecheck_iterable([1.0, -4.2, 5], (float,), {})
        False
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Any,), {})
        True
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Union[int, float],), {})
        False
        >>> _instancecheck_iterable(['1.0', -4.2, 5], (Union[int, float, str],), {})
        True
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[int],), {})
        False
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[List[int]],), {})
        True
        >>> _instancecheck_iterable([[], [], [[42]], [[]]], (List[List[float]],), {})
        False
    """
    type_ = type_args[0]
    return all(_is_instance(val, type_, type_vars=type_vars, context=context) for val in iterable)


def _instancecheck_generator(generator: typing.Generator, type_args: Tuple, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    from pedantic.models import GeneratorWrapper

    assert isinstance(generator, GeneratorWrapper)
    return generator._yield_type == type_args[0] and generator._send_type == type_args[1] and generator._return_type == type_args[2]


def _instancecheck_mapping(mapping: Mapping, type_args: Tuple, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Any, Optional
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3}, (int, Any), {})
        True
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3}, (int, int), {})
        True
        >>> _instancecheck_mapping({0: 1, 1: 2, 2: 3.0}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1.0: 2, 2: 3}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: '1', 1: 2, 2: 3}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1: 2, None: 3.0}, (int, int), {})
        False
        >>> _instancecheck_mapping({0: 1, 1: 2, None: 3.0}, (int, Optional[int]), {})
        False
    """
    return _instancecheck_items_view(mapping.items(), type_args, type_vars=type_vars, context=context)


def _instancecheck_items_view(items_view: ItemsView, type_args: Tuple, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Any, Optional
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3}.items(), (int, Any), {})
        True
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3}.items(), (int, int), {})
        True
        >>> _instancecheck_items_view({0: 1, 1: 2, 2: 3.0}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1.0: 2, 2: 3}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: '1', 1: 2, 2: 3}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1: 2, None: 3.0}.items(), (int, int), {})
        False
        >>> _instancecheck_items_view({0: 1, 1: 2, None: 3.0}.items(), (int, Optional[int]), {})
        False
    """
    key_type, value_type = type_args
    return all(_is_instance(obj=key, type_=key_type, type_vars=type_vars, context=context) and
               _is_instance(obj=val, type_=value_type, type_vars=type_vars, context=context)
               for key, val in items_view)


def _instancecheck_tuple(tup: Tuple, type_args: Any, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Any
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(Any, Ellipsis), type_vars={})
        True
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(Any,), type_vars={})
        False
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, int, str, str), type_vars={})
        True
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, float, str, str), type_vars={})
        False
        >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(float, int, str, int), type_vars={})
        False
    """
    if Ellipsis in type_args:
        return all(_is_instance(obj=val, type_=type_args[0], type_vars=type_vars, context=context) for val in tup)

    if tup == () and type_args == ((),):
        return True

    if len(tup) != len(type_args):
        return False

    return all(_is_instance(obj=val, type_=type_, type_vars=type_vars, context=context) for val, type_ in zip(tup, type_args))


def _instancecheck_union(value: Any, type_: Any, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Union, TypeVar, Any
        >>> NoneType = type(None)
        >>> _instancecheck_union(3.0, Union[int, float], {})
        True
        >>> _instancecheck_union(3, Union[int, float], {})
        True
        >>> _instancecheck_union('3', Union[int, float], {})
        False
        >>> _instancecheck_union(None, Union[int, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[float, NoneType], {})
        True
        >>> S = TypeVar('S')
        >>> T = TypeVar('T')
        >>> U = TypeVar('U')
        >>> _instancecheck_union(42, Union[T, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {T: int})
        True
        >>> _instancecheck_union('None', Union[T, NoneType], {T: int})
        False
        >>> _instancecheck_union(42, Union[T, S], {})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: int})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: str})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: int, S: float})
        True
        >>> _instancecheck_union(42, Union[T, S], {T: str, S: float})
        False
        >>> _instancecheck_union(42.8, Union[T, S], {T: str, S: float})
        True
        >>> _instancecheck_union(None, Union[T, S], {T: str, S: float})
        False
        >>> _instancecheck_union(None, Union[T, S], {})
        True
        >>> _instancecheck_union(None, Union[T, NoneType], {T: int})
        True
        >>> _instancecheck_union('None', Union[T, NoneType, S], {T: int})
        True
        >>> _instancecheck_union(42, Union[T, Any], {})
        True
        >>> _instancecheck_union(42, Union[T, Any], {T: float})
        True
        >>> _instancecheck_union(None, Optional[Callable[[float], float]], {})
        True
        >>> _instancecheck_union(3.0, int | float, {})
        True
        >>> _instancecheck_union(3, int | float, {})
        True
        >>> _instancecheck_union('3', int | float, {})
        False
        >>> _instancecheck_union(None, int | NoneType, {})
        True
        >>> _instancecheck_union(None, float | NoneType, {})
        True
        >>> S = TypeVar('S')
        >>> T = TypeVar('T')
        >>> U = TypeVar('U')
        >>> _instancecheck_union(42, T | NoneType, {})
        True
        >>> _instancecheck_union(None, T | NoneType, {})
        True
        >>> _instancecheck_union(None, T | NoneType, {T: int})
        True
        >>> _instancecheck_union('None', T | NoneType, {T: int})
        False
        >>> _instancecheck_union(42, T | S, {})
        True
        >>> _instancecheck_union(42, T | S, {T: int})
        True
        >>> _instancecheck_union(42, T | S, {T: str})
        True
        >>> _instancecheck_union(42, T | S, {T: int, S: float})
        True
        >>> _instancecheck_union(42, T | S, {T: str, S: float})
        False
        >>> _instancecheck_union(42.8, T | S, {T: str, S: float})
        True
        >>> _instancecheck_union(None, T | S, {T: str, S: float})
        False
        >>> _instancecheck_union(None, T | S, {})
        True
        >>> _instancecheck_union(None, T | NoneType, {T: int})
        True
        >>> _instancecheck_union('None', T | NoneType | S, {T: int})
        True
        >>> _instancecheck_union(42, T | Any, {})
        True
        >>> _instancecheck_union(42, T | Any, {T: float})
        True
        >>> _instancecheck_union(None, Optional[Callable[[float], float]], {})
        True
    """

    type_args = get_type_arguments(cls=type_)
    return _check_union(value=value, type_args=type_args, type_vars=type_vars, context=context)


def _check_union(value: Any, type_args: Tuple[Any, ...], type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    args_non_type_vars = [type_arg for type_arg in type_args if not isinstance(type_arg, TypeVar)]
    args_type_vars = [type_arg for type_arg in type_args if isinstance(type_arg, TypeVar)]
    args_type_vars_bounded = [type_var for type_var in args_type_vars if type_var in type_vars]
    args_type_vars_unbounded = [type_var for type_var in args_type_vars if type_var not in args_type_vars_bounded]
    matches_non_type_var = any([_is_instance(obj=value, type_=typ, type_vars=type_vars, context=context) for typ in args_non_type_vars])

    if matches_non_type_var:
        return True

    for bounded_type_var in args_type_vars_bounded:
        try:
            _is_instance(obj=value, type_=bounded_type_var, type_vars=type_vars, context=context)
            return True
        except PedanticException:
            pass

    if not args_type_vars_unbounded:
        return False
    if len(args_type_vars_unbounded) == 1:
        return _is_instance(obj=value, type_=args_type_vars_unbounded[0], type_vars=type_vars, context=context)
    return True  # it is impossible to figure out, how to bound these type variables correctly


def _instancecheck_literal(value: Any, type_: Any, type_vars: Dict[TypeVar_, Any], context: Dict[str, Any] = None) -> bool:
    type_args = get_type_arguments(cls=type_)
    return value in type_args


def _instancecheck_callable(value: Optional[Callable], type_: Any, _, context: Dict[str, Any] = None) -> bool:
    """
        >>> from typing import Tuple, Callable, Any
        >>> def f(x: int, y: float) -> Tuple[float, str]:
        ...       return float(x), str(y)
        >>> _instancecheck_callable(f, Callable[[int, float], Tuple[float, str]], {})
        True
        >>> _instancecheck_callable(f, Callable[[int, float], Tuple[int, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[[int, int], Tuple[float, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[..., Tuple[float, str]], {})
        True
        >>> _instancecheck_callable(f, Callable[..., Tuple[int, str]], {})
        False
        >>> _instancecheck_callable(f, Callable[..., Any], {})
        True
        >>> _instancecheck_callable(f, Callable[[int, int, int], Tuple[float, str]], {})
        False
        >>> _instancecheck_callable(None, Callable[..., Any], {})
        False
    """

    if value is None:
        return False

    if _is_lambda(obj=value):
        return True

    param_types, ret_type = get_type_arguments(cls=type_)

    try:
        sig = inspect.signature(obj=value)
    except TypeError:
        return False

    non_optional_params = {k: v for k, v in sig.parameters.items() if v.default == sig.empty}

    if param_types is not Ellipsis:
        if len(param_types) != len(non_optional_params):
            return False

        for param, expected_type in zip(sig.parameters.values(), param_types):
            if not _is_subtype(sub_type=param.annotation, super_type=expected_type):
                return False

    if not inspect.iscoroutinefunction(value):
        return _is_subtype(sub_type=sig.return_annotation, super_type=ret_type)

    base = get_base_generic(ret_type)

    if base == typing.Awaitable:
        arg = get_type_arguments(ret_type)[0]
    elif base == typing.Coroutine:
        arg = get_type_arguments(ret_type)[2]
    else:
        return False

    return _is_subtype(sub_type=sig.return_annotation, super_type=arg)


def _is_lambda(obj: Any) -> bool:
    return callable(obj) and obj.__name__ == '<lambda>'


def _instancecheck_type(value: Any, type_: Any, type_vars: Dict, context: Dict[str, Any] = None) -> bool:
    type_ = type_[0]

    if type_ == Any or isinstance(type_, typing.TypeVar):
        return True

    return _is_subtype(sub_type=value, super_type=type_, context=context)


_ORIGIN_TYPE_CHECKERS = {}
for class_path, _check_func in {
    'typing.Container': _instancecheck_iterable,
    'typing.Collection': _instancecheck_iterable,
    'typing.AbstractSet': _instancecheck_iterable,
    'typing.MutableSet': _instancecheck_iterable,
    'typing.Sequence': _instancecheck_iterable,
    'typing.Iterable': _instancecheck_iterable,
    'typing.MutableSequence': _instancecheck_iterable,
    'typing.Deque': _instancecheck_iterable,
    'typing.List': _instancecheck_iterable,
    'typing.Set': _instancecheck_iterable,
    'typing.FrozenSet': _instancecheck_iterable,
    'typing.KeysView': _instancecheck_iterable,
    'typing.ValuesView': _instancecheck_iterable,
    'typing.AsyncIterable': _instancecheck_iterable,

    'typing.Mapping': _instancecheck_mapping,
    'typing.MutableMapping': _instancecheck_mapping,
    'typing.MappingView': _instancecheck_mapping,
    'typing.ItemsView': _instancecheck_items_view,
    'typing.Dict': _instancecheck_mapping,
    'typing.DefaultDict': _instancecheck_mapping,
    'typing.Counter': _instancecheck_mapping,
    'typing.ChainMap': _instancecheck_mapping,

    'typing.Tuple': _instancecheck_tuple,
    'typing.Type': _instancecheck_type,

    'typing.Generator': _instancecheck_generator,
}.items():
    class_ = eval(class_path)
    _ORIGIN_TYPE_CHECKERS[class_] = _check_func

_SPECIAL_INSTANCE_CHECKERS = {
    'Union': _instancecheck_union,
    'Optional': _instancecheck_union,
    'Literal': _instancecheck_literal,
    'Callable': _instancecheck_callable,
    'Any': lambda v, t, tv, c: True,
}

NUM_OF_REQUIRED_TYPE_ARGS_EXACT = {
    'Callable': 2,
    'List': 1,
    'Set': 1,
    'FrozenSet': 1,
    'Iterable': 1,
    'Sequence': 1,
    'Dict': 2,
    'Optional': 2,  # because _get_type_arguments(Optional[int]) returns (int, None)
}
NUM_OF_REQUIRED_TYPE_ARGS_MIN = {
    'Tuple': 1,
    'Union': 2,
}


def convert_to_typing_types(x: typing.Type) -> typing.Type:
    """
        Example:
        >>> convert_to_typing_types(int)
        <class 'int'>
        >>> convert_to_typing_types(list)
        Traceback (most recent call last):
        ...
        ValueError: Missing type arguments
        >>> convert_to_typing_types(list[int])
        typing.List[int]
        >>> convert_to_typing_types(set[int])
        typing.Set[int]
        >>> convert_to_typing_types(frozenset[int])
        typing.FrozenSet[int]
        >>> convert_to_typing_types(tuple[int])
        typing.Tuple[int]
        >>> convert_to_typing_types(type[int])
        typing.Type[int]
        >>> convert_to_typing_types(tuple[int, float])
        typing.Tuple[int, float]
        >>> convert_to_typing_types(dict[int, float])
        typing.Dict[int, float]
        >>> convert_to_typing_types(list[dict[int, float]])
        typing.List[typing.Dict[int, float]]
        >>> convert_to_typing_types(list[dict[int, tuple[float, str]]])
        typing.List[typing.Dict[int, typing.Tuple[float, str]]]
    """

    if x in {list, set, dict, frozenset, tuple, type}:
        raise ValueError('Missing type arguments')

    if not hasattr(x, '__origin__'):
        return x

    origin = x.__origin__  # type: ignore # checked above
    args = [convert_to_typing_types(a) for a in x.__args__]  # type: ignore

    if origin is list:
        return typing.List[tuple(args)]
    elif origin is set:
        return typing.Set[tuple(args)]
    elif origin is dict:
        return typing.Dict[tuple(args)]
    elif origin is tuple:
        return typing.Tuple[tuple(args)]
    elif origin is frozenset:
        return typing.FrozenSet[tuple(args)]
    elif origin is type:
        return typing.Type[tuple(args)]

    raise RuntimeError(x)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
