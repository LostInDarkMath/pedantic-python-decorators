"""Idea is taken from: https://stackoverflow.com/a/55504010/10975692"""

import inspect
import typing
import collections

typing_protocol = typing.Protocol if hasattr(typing, 'Protocol') else typing._Protocol


def is_instance(obj: typing.Any, type_: typing.Any) -> bool:
    """The main function of this module."""

    if type_.__module__ == 'typing':
        if is_qualified_generic(type_):
            base_generic = get_base_generic(type_)
        else:
            base_generic = type_
        name = _get_name(base_generic)

        try:
            validator = _SPECIAL_INSTANCE_CHECKERS[name]
        except KeyError:
            pass
        else:
            return validator(obj, type_)

    if is_base_generic(type_):
        python_type = _get_python_type(type_)
        return isinstance(obj, python_type)

    if is_qualified_generic(type_):
        python_type = _get_python_type(type_)
        if not isinstance(obj, python_type):
            return False

        base = get_base_generic(type_)
        validator = _ORIGIN_TYPE_CHECKERS[base]

        type_args = get_subtypes(type_)
        return validator(obj, type_args)

    return isinstance(obj, type_)


def _has_required_type_arguments(cls: typing.Any) -> bool:
    """Examples:
    >>> _has_required_type_arguments(typing.List)
    >>> False
    >>> _has_required_type_arguments(typing.List[int])
    >>> True
    >>> _has_required_type_arguments(typing.Callable[[int, float], typing.Tuple[float, str]])
    >>> True
    """
    num_type_args = len(_get_type_arguments(cls))
    requirements_exact = {
        'typing.Callable': 2,
        'typing.List': 1,
        'typing.Set': 1,
        'typing.FrozenSet': 1,
        'typing.Iterable': 1,
        'typing.Dict': 2,
        'typing.Optional': 2,  # because typing.get_args(typing.Optional[int]) returns (int, None)
    }
    requirements_min = {
        'typing.Tuple': 1,
        'typing.Union': 2,
    }
    base: str = _get_base_class_as_str(cls=cls)

    if base in requirements_exact:
        return requirements_exact[base] == num_type_args
    elif base in requirements_min:
        return requirements_min[base] <= num_type_args
    else:
        return True


def _get_type_arguments(cls: typing.Any) -> typing.Tuple[typing.Any, ...]:
    """Examples:
    >>> _get_type_arguments(int)
    >>> ()
    >>> _get_type_arguments(typing.List)
    >>> ()
    >>> _get_type_arguments(typing.List[int])
    >>> (<class 'int'>,)
    >>> get_type_arguments(typing.Callable[[int, float], str])
    >>> ([<class 'int'>, <class 'float'>], <class 'str'>)
    >>> get_type_arguments(typing.Callable[..., str])
    >>> (Ellipses, <class 'str'>)
    """
    if hasattr(typing, 'get_args'):
        # Python 3.8.0 throws index error here, for argument cls = typing.Callable (without type arguments)
        try:
            return _clean_type_arguments(args=typing.get_args(cls))
        except IndexError:
            return ()
    elif hasattr(cls, '__args__'):
        # return cls.__args__  # DOESNT WORK. So below is the modified (!) implementation of typing.get_args()

        res = _clean_type_arguments(args=cls.__args__)
        if res == ():
            return ()

        origin = _get_origin(cls)
        if ((origin is typing.Callable) or (origin is collections.abc.Callable)) and res[0] is not Ellipsis:
            res = (list(res[:-1]), res[-1])
        return res
    else:
        return ()


def _clean_type_arguments(args: typing.Tuple[typing.Any, ...]) -> typing.Tuple[typing.Any, ...]:
    if args is None or args == () or any([isinstance(o, typing.TypeVar) for o in args]):
        return ()
    return args


def _get_origin(cls: typing.Any) -> typing.Any:
    """Examples:
    >>> _get_origin(typing.List[float])
    >>> <class 'list'>
    """
    return typing.get_origin(cls) if hasattr(typing, 'get_origin') else cls.__origin__


def _get_base_class_as_str(cls: typing.Any) -> str:
    """Example:
    >>> _get_base_class_as_str(typing.List[int])
    >>> 'typing.List'
    """
    return str(cls).split('[')[0]


def _is_generic(cls: typing.Any) -> bool:
    if hasattr(typing, '_GenericAlias'):
        if isinstance(cls, typing._GenericAlias):
            return True

        if isinstance(cls, typing._SpecialForm):
            return cls not in {typing.Any}
    else:
        if isinstance(cls, (typing.GenericMeta, typing._Union, typing._Optional, typing._ClassVar)):
            return True
    return False


def _is_base_generic(cls: typing.Any) -> bool:
    if hasattr(typing, '_GenericAlias'):
        if isinstance(cls, typing._GenericAlias):
            if cls.__origin__ in {typing.Generic, typing_protocol}:
                return False

            if str(cls) in ['typing.Tuple', 'typing.Callable']:
                return True

            return len(cls.__parameters__) > 0

        if isinstance(cls, typing._SpecialForm):
            return cls._name in {'ClassVar', 'Union', 'Optional'}
    else:
        if isinstance(cls, (typing.GenericMeta, typing._Union)):
            return cls.__args__ in {None, ()}

        if isinstance(cls, typing._Optional):
            return True
    return False


def _get_base_generic(cls: typing.Any) -> typing.Any:
    if cls._name is None or not hasattr(typing, '_GenericAlias'):
        return cls.__origin__
    else:
        return getattr(typing, cls._name)


def _get_python_type(cls: typing.Any) -> typing.Any:
    """Like `python_type`, but only works with `typing` classes."""
    if hasattr(typing, '_GenericAlias'):
        return cls.__origin__
    else:
        for typ in cls.mro():
            if typ.__module__ == 'builtins' and typ is not object:
                return typ


def _get_name(cls: typing.Any) -> str:
    if hasattr(typing, '_GenericAlias'):
        return cls._name
    else:
        try:
            return cls.__name__
        except AttributeError:
            return type(cls).__name__[1:]


def _get_subtypes(cls):
    subtypes = cls.__args__

    if get_base_generic(cls) is typing.Callable:
        if len(subtypes) != 2 or subtypes[0] is not ...:
            subtypes = (subtypes[:-1], subtypes[-1])
    return subtypes


def is_generic(cls):
    """
    Detects any kind of generic, for example `List` or `List[int]`. This includes "special" types like
    Union and Tuple - anything that's subscriptable, basically.
    """
    return _is_generic(cls)


def is_base_generic(cls: typing.Any) -> bool:
    """
    Detects generic base classes.

    Examples:
    >>> is_base_generic(int)  # int, float, str, bool
    >>> False
    >>> is_base_generic(typing.List)
    >>> True
    >>> is_base_generic(typing.Callable)
    >>> True
    >>> is_base_generic(typing.List[int])
    >>> False
    >>> is_base_generic(typing.Callable[[int], str])
    >>> False
    >>> is_base_generic(typing.List[typing.List[int]])
    >>> False
    """
    assert _has_required_type_arguments(cls), \
        f'The type annotation "{cls}" misses some type arguments e.g. ' \
        f'"typing.Tuple[Any, ...]" or "typing.Callable[..., str]".'
    return _is_base_generic(cls)


def is_qualified_generic(cls):
    """
    Detects generics with arguments, for example `List[int]` (but not `List`)
    """
    return is_generic(cls) and not is_base_generic(cls)


def get_base_generic(cls):
    return _get_base_generic(cls)


def get_subtypes(cls):
    return _get_subtypes(cls)


def _instancecheck_iterable(iterable, type_args):
    type_ = type_args[0]
    return all(is_instance(val, type_) for val in iterable)


def _instancecheck_mapping(mapping, type_args):
    return _instancecheck_itemsview(mapping.items(), type_args)


def _instancecheck_itemsview(itemsview, type_args):
    key_type, value_type = type_args
    return all(is_instance(key, key_type) and is_instance(val, value_type) for key, val in itemsview)


def _instancecheck_tuple(tup, type_args) -> bool:
    """Examples:
    >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(typing.Any, Ellipsis))  # = Tuple[Any, ...]
    >>> True
    """
    if Ellipsis in type_args:
        return all(is_instance(val, type_args[0]) for val in tup)

    if len(tup) != len(type_args):
        return False

    return all(is_instance(val, type_) for val, type_ in zip(tup, type_args))


_ORIGIN_TYPE_CHECKERS = {}
for class_path, check_func in {
    # iterables
    'typing.Container': _instancecheck_iterable,
    'typing.Collection': _instancecheck_iterable,
    'typing.AbstractSet': _instancecheck_iterable,
    'typing.MutableSet': _instancecheck_iterable,
    'typing.Sequence': _instancecheck_iterable,
    'typing.MutableSequence': _instancecheck_iterable,
    'typing.ByteString': _instancecheck_iterable,
    'typing.Deque': _instancecheck_iterable,
    'typing.List': _instancecheck_iterable,
    'typing.Set': _instancecheck_iterable,
    'typing.FrozenSet': _instancecheck_iterable,
    'typing.KeysView': _instancecheck_iterable,
    'typing.ValuesView': _instancecheck_iterable,
    'typing.AsyncIterable': _instancecheck_iterable,

    # mappings
    'typing.Mapping': _instancecheck_mapping,
    'typing.MutableMapping': _instancecheck_mapping,
    'typing.MappingView': _instancecheck_mapping,
    'typing.ItemsView': _instancecheck_itemsview,
    'typing.Dict': _instancecheck_mapping,
    'typing.DefaultDict': _instancecheck_mapping,
    'typing.Counter': _instancecheck_mapping,
    'typing.ChainMap': _instancecheck_mapping,

    # other
    'typing.Tuple': _instancecheck_tuple,
}.items():
    try:
        cls = eval(class_path)
    except AttributeError:
        continue

    _ORIGIN_TYPE_CHECKERS[cls] = check_func


def _instancecheck_callable(value, type_):
    if not callable(value):
        return False

    if is_base_generic(type_):
        return True

    param_types, ret_type = get_subtypes(type_)
    sig = inspect.signature(value)

    missing_annotations = []

    if param_types is not ...:
        if len(param_types) != len(sig.parameters):
            return False

        # if any of the existing annotations don't match the type, we'll return False.
        # Then, if any annotations are missing, we'll throw an exception.
        for param, expected_type in zip(sig.parameters.values(), param_types):
            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                missing_annotations.append(param)
                continue

            if not _is_subtype(param_type, expected_type):
                return False

    if sig.return_annotation is inspect.Signature.empty:
        missing_annotations.append('return')
    else:
        if not _is_subtype(sig.return_annotation, ret_type):
            return False

    assert not missing_annotations,\
        f'Parsing of type annotations failed. Maybe you are about to return a lambda expression. ' \
        f'Try returning an inner function instead. {missing_annotations}'
    return True


def _instancecheck_union(value, type_):
    types = get_subtypes(type_)
    return any(is_instance(value, typ) for typ in types)


_SPECIAL_INSTANCE_CHECKERS = {
    'Union': _instancecheck_union,
    'Callable': _instancecheck_callable,
    'Any': lambda v, t: True,
}


def _is_subtype(sub_type, super_type):
    if not is_generic(sub_type):
        python_super = _python_type(super_type)
        python_sub = _python_type(sub_type)
        return issubclass(python_sub, python_super)

    # at this point we know `sub_type` is a generic
    python_sub = _python_type(sub_type)
    python_super = _python_type(super_type)
    if not issubclass(python_sub, python_super):
        return False

    # at this point we know that `sub_type`'s base type is a subtype of `super_type`'s base type.
    # If `super_type` isn't qualified, then there's nothing more to do.
    if not is_generic(super_type) or is_base_generic(super_type):
        return True

    # at this point we know that `super_type` is a qualified generic... so if `sub_type` isn't
    # qualified, it can't be a subtype.
    if is_base_generic(sub_type):
        return False

    # at this point we know that both types are qualified generics, so we just have to
    # compare their sub-types.
    sub_args = get_subtypes(sub_type)
    super_args = get_subtypes(super_type)
    return all(_is_subtype(sub_arg, super_arg) for sub_arg, super_arg in zip(sub_args, super_args))


def _python_type(annotation):
    """
    Given a type annotation or a class as input, returns the corresponding python class.

    Examples:
        >>> _python_type(typing.Dict)
        <class 'dict'>
        >>> _python_type(typing.List[int])
        <class 'list'>
        >>> _python_type(int)
        <class 'int'>
        >>> _python_type(typing.Any)
        <class 'object'>
    """
    if hasattr(annotation, 'mro'):
        mro = annotation.mro()
        if typing.Type in mro:
            return annotation._python_type
        elif annotation.__module__ == 'typing':
            return _get_python_type(annotation)
        else:
            return annotation
    elif annotation == typing.Any or annotation == Ellipsis:
        return object
    else:
        return _get_python_type(annotation)
