import inspect
from typing import Any, get_args, Generic

from pedantic.method_decorators import _parse_documented_type


def check_generic(instance: Any) -> None:
    if not is_generic_class(instance=instance):
        return

    type_vars = dict()
    generic_type_vars = get_args(type(instance).__orig_bases__[0])  # TODO works only for direct inheritence

    name = instance.__class__.__name__
    frames = inspect.stack()
    filtered = list(filter(lambda f: f.function == 'wrapper', frames))
    assert len(filtered) == 1, f'Filter error'
    frame = frames[frames.index(filtered[0]) + 1]
    src = [clean_line(line) for line in inspect.getsource(frame.frame).split('\n')]
    target = f'={name}('
    filtered_src = list(filter(lambda line: target in line, src))
    assert len(filtered_src) == 1
    target_var = filtered_src[0].split(target)[0]
    constructor_call = filtered_src[0].split(target)[1]
    assert ':' in target_var, \
        f'Initialization of generic class {name} should have a type annotation like "{target_var}: ' \
        f'{name}[SomeType] = {constructor_call}"'
    type_annotation = target_var.split(':')[1]
    print(type_annotation)
    type_var = type_annotation.replace(name, '').strip()[1:-1]
    print(type_var)
    parsed_type = _parse_documented_type(type_=type_var, context={}, err='')  # TODO context
    print(parsed_type)
    type_vars[generic_type_vars[0]] = parsed_type


def is_generic_class(instance: Any) -> bool:
    return Generic in instance.__class__.__bases__


def clean_line(line: str) -> str:
    return line.split('#')[0].split('"""')[0].split("'''")[0].replace(' ', '')