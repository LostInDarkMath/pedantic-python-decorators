"""Idea is taken from: https://stackoverflow.com/a/55504010/10975692"""
import inspect
import typing
import collections

typing_protocol = typing.Protocol if hasattr(typing, 'Protocol') else typing._Protocol


def _is_instance(obj: typing.Any, type_: typing.Any, type_vars) -> bool:
    """main function of this file"""
    assert _has_required_type_arguments(type_), \
        f'The type annotation "{type_}" misses some type arguments e.g. ' \
        f'"typing.Tuple[Any, ...]" or "typing.Callable[..., str]".'

    if type_.__module__ == 'typing':
        if _is_generic(type_):
            origin = _get_base_generic(type_)
        else:
            origin = type_
        name = _get_name(origin)

        if name in _SPECIAL_INSTANCE_CHECKERS:
            validator = _SPECIAL_INSTANCE_CHECKERS[name]
            return validator(obj, type_, type_vars)

    if _is_generic(type_):
        python_type = _get_python_type(type_)
        if not isinstance(obj, python_type):
            return False

        base = _get_base_generic(type_)
        validator = _ORIGIN_TYPE_CHECKERS[base]

        type_args = _get_subtypes(type_)
        return validator(obj, type_args, type_vars)

    if isinstance(type_, typing.TypeVar):
        if type_ in type_vars:
            other = type_vars[type_]
            assert type(obj) == type(other), \
                f'For TypeVar {type_} exists a type conflict: value {obj} has type {type(obj)} and value ' \
                f'{other} has type {type(other)}'
        else:
            type_vars[type_] = obj
        return True

    if _is_type_new_type(type_):
        return isinstance(obj, type_.__supertype__)

    return isinstance(obj, type_)


def _is_type_new_type(type_: typing.Any) -> bool:
    return type_.__qualname__ == typing.NewType('name', int).__qualname__  # arguments of NewType() are arbitrary here


def _get_name(cls: typing.Any) -> str:
    """
    Examples:
        >>> _get_name(typing.Tuple)
        'Tuple'
        >>> _get_name(typing.Callable)
        'Callable'
    """
    if hasattr(cls, '_name'):
        return cls._name
    elif hasattr(cls, '__name__'):
        return cls.__name__
    else:
        return type(cls).__name__[1:]


def _is_generic(cls: typing.Any) -> bool:
    """
    Detects any kind of generic, for example `List` or `List[int]`. This includes "special" types like
    Union and Tuple - anything that's subscriptable, basically.
    Examples:
        >>> _is_generic(int)  # float, bool, str
        False
        >>> _is_generic(typing.List[int])
        True
        >>> _is_generic(typing.List[typing.List[int]])
        True
        >>> _is_generic(typing.Any)
        False
        >>> _is_generic(typing.Callable[[int], int])
        True
    """
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
    """
        Detects generic base classes.

        Examples:
        >>> _is_base_generic(int)  # int, float, str, bool
        False
        >>> _is_base_generic(typing.List)
        True
        >>> _is_base_generic(typing.Callable)
        True
        >>> _is_base_generic(typing.List[int])
        False
        >>> _is_base_generic(typing.Callable[[int], str])
        False
        >>> _is_base_generic(typing.List[typing.List[int]])
        False
        >>> _is_base_generic(list)
        False
    """

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


def _has_required_type_arguments(cls: typing.Any) -> bool:
    """Examples:
    >>> _has_required_type_arguments(typing.List)
    False
    >>> _has_required_type_arguments(typing.List[int])
    True
    >>> _has_required_type_arguments(typing.Callable[[int, float], typing.Tuple[float, str]])
    True
    """
    requirements_exact = {
        'Callable': 2,
        'List': 1,
        'Set': 1,
        'FrozenSet': 1,
        'Iterable': 1,
        'Sequence': 1,
        'Dict': 2,
        'Optional': 2,  # because typing.get_args(typing.Optional[int]) returns (int, None)
    }
    requirements_min = {
        'Tuple': 1,
        'Union': 2,
    }
    base: str = _get_name(cls=cls)

    if '[' not in str(cls) and (base in requirements_min or base in requirements_exact):
        return False

    num_type_args = len(_get_type_arguments(cls))

    if base in requirements_exact:
        return requirements_exact[base] == num_type_args
    elif base in requirements_min:
        return requirements_min[base] <= num_type_args
    else:
        return True


def _get_type_arguments(cls: typing.Any) -> typing.Tuple[typing.Any, ...]:
    """Examples:
    >>> _get_type_arguments(int)
    ()
    >>> _get_type_arguments(typing.List) # NOTE: That output here is different on different Python versions!
    (~T,)
    >>> _get_type_arguments(typing.List[int])
    (<class 'int'>,)
    >>> _get_type_arguments(typing.Callable[[int, float], str])
    ([<class 'int'>, <class 'float'>], <class 'str'>)
    >>> _get_type_arguments(typing.Callable[..., str])
    (Ellipsis, <class 'str'>)
    """
    if hasattr(typing, 'get_args'):
        return typing.get_args(cls)
    elif hasattr(cls, '__args__'):
        # return cls.__args__  # DOESNT WORK. So below is the modified (!) implementation of typing.get_args()
        res = cls.__args__
        origin = _get_base_generic(cls)
        if ((origin is typing.Callable) or (origin is collections.abc.Callable)) and res[0] is not Ellipsis:
            res = (list(res[:-1]), res[-1])
        return res
    else:
        return ()


def _get_base_generic(cls: typing.Any) -> typing.Any:
    """
    Examples:
    >>> _get_base_generic(typing.List[float])
    typing.List
    """
    if not hasattr(typing, '_GenericAlias'):
        return cls.__origin__

    if cls._name is None:
        return cls.__origin__
    else:
        return getattr(typing, cls._name)


def _is_subtype(sub_type, super_type):
    if not _is_generic(sub_type):
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
    if not _is_generic(super_type) or _is_base_generic(super_type):
        return True

    # at this point we know that `super_type` is a qualified generic... so if `sub_type` isn't
    # qualified, it can't be a subtype.
    if _is_base_generic(sub_type):
        return False

    # at this point we know that both types are qualified generics, so we just have to
    # compare their sub-types.
    sub_args = _get_subtypes(sub_type)
    super_args = _get_subtypes(super_type)
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


def _get_python_type(cls: typing.Any) -> typing.Any:
    """Like `python_type`, but only works with `typing` classes."""
    if hasattr(cls, '__origin__'):
        return cls.__origin__
    else:
        for typ in cls.mro():
            if typ.__module__ == 'builtins' and typ is not object:
                return typ


def _get_subtypes(cls):
    subtypes = cls.__args__

    if _get_base_generic(cls) is typing.Callable:
        if len(subtypes) != 2 or subtypes[0] is not ...:
            subtypes = (subtypes[:-1], subtypes[-1])
    return subtypes


def _instancecheck_iterable(iterable, type_args, type_vars):
    type_ = type_args[0]
    return all(_is_instance(val, type_, type_vars=type_vars) for val in iterable)


def _instancecheck_mapping(mapping, type_args, type_vars):
    return _instancecheck_items_view(mapping.items(), type_args, type_vars=type_vars)


def _instancecheck_items_view(items_view, type_args, type_vars):
    key_type, value_type = type_args
    return all(_is_instance(key, key_type, type_vars=type_vars) and
               _is_instance(val, value_type, type_vars=type_vars)
               for key, val in items_view)


def _instancecheck_tuple(tup, type_args, type_vars) -> bool:
    """Examples:
    >>> _instancecheck_tuple(tup=(42.0, 43, 'hi', 'you'), type_args=(typing.Any, Ellipsis), type_vars={})  \
        # = Tuple[Any, ...]
    True
    """
    if Ellipsis in type_args:
        return all(_is_instance(val, type_args[0], type_vars=type_vars) for val in tup)

    if len(tup) != len(type_args):
        return False

    return all(_is_instance(val, type_, type_vars=type_vars) for val, type_ in zip(tup, type_args))


_ORIGIN_TYPE_CHECKERS = {}
for class_path, _check_func in {
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
    'typing.ItemsView': _instancecheck_items_view,
    'typing.Dict': _instancecheck_mapping,
    'typing.DefaultDict': _instancecheck_mapping,
    'typing.Counter': _instancecheck_mapping,
    'typing.ChainMap': _instancecheck_mapping,

    # other
    'typing.Tuple': _instancecheck_tuple,
}.items():
    try:
        class_ = eval(class_path)
    except AttributeError:
        continue

    _ORIGIN_TYPE_CHECKERS[class_] = _check_func


def _instancecheck_callable(value, type_, _):
    if not callable(value):
        return False

    if _is_base_generic(type_):
        return True

    param_types, ret_type = _get_subtypes(type_)
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

    assert not missing_annotations, \
        f'Parsing of type annotations failed. Maybe you are about to return a lambda expression. ' \
        f'Try returning an inner function instead. {missing_annotations}'
    return True


def _instancecheck_union(value, type_, type_vars):
    types = _get_subtypes(type_)
    return any(_is_instance(value, typ, type_vars=type_vars) for typ in types)


_SPECIAL_INSTANCE_CHECKERS = {
    'Union': _instancecheck_union,
    'Callable': _instancecheck_callable,
    'Any': lambda v, t, tv: True,
}


if __name__ == "__main__":
    import doctest
    doctest.testmod()
