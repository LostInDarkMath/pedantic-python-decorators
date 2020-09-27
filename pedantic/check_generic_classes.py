import inspect
from typing import Any, get_args, Generic, TypeVar, Dict

from pedantic.type_hint_parser import _get_type_arguments


def check_generic(instance: Any) -> Dict[TypeVar, Any]:
    type_vars = dict()

    if not is_generic_class(instance=instance):
        return type_vars

    assert_constructor_called_with_generics(instance=instance)

    # The information I need is set after the object construction in the __orig_class__ attribute.
    # This method is called before construction and therefore it returns if the value isn't set
    # https://stackoverflow.com/questions/60985221/how-can-i-access-t-from-a-generict-instance-early-in-its-lifecycle
    if not hasattr(instance, '__orig_class__'):
        return type_vars

    generic_type_vars = get_args(type(instance).__orig_bases__[0])  # TODO works only for direct inheritance
    generic_type_args = _get_type_arguments(instance.__orig_class__)
    assert len(generic_type_args) == len(generic_type_vars), f'len doesnt match'
    for i, type_var in enumerate(generic_type_vars):
        type_vars[type_var] = generic_type_args[i]
    return type_vars


def assert_constructor_called_with_generics(instance: Any) -> None:
    # TODO maybe we should not do this here and use "first come first serve if no generics are provided. Thats easy"
    name = instance.__class__.__name__
    frames = inspect.stack()
    filtered = list(filter(lambda f: f.function == 'wrapper', frames))
    if not filtered: # that's the case if the pseudo-method "get_type_vars()" is called
        return

    frame = frames[frames.index(filtered[-1]) + 1]
    if frame.function == '__call__':
        frame = frames[frames.index(filtered[0]) + 2]

    src = [clean_line(line) for line in inspect.getsource(frame.frame).split('\n')]
    target = f'={name}'
    filtered_src = list(filter(lambda line: target in line, src))
    assert len(filtered_src) >= 1, f'No constructor call found in source\n {src}' # TODO error message
    for match in filtered_src:
        constructor_call = match.split(target)[1]
        generics = constructor_call.split('(')[0]
        assert '[' in generics and ']' in generics, f'Use generics!'


def is_generic_class(instance: Any) -> bool:
    return Generic in instance.__class__.__bases__


def clean_line(line: str) -> str:
    return line.split('#')[0].split('"""')[0].split("'''")[0].replace(' ', '')
