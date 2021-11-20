from typing import Type, Any, Union

from pedantic.decorators.fn_deco_validate.exceptions import ConversionError

T = Union[bool, int, float, str, dict, list]


def convert_value(value: Any, target_type: Type[T]) -> T:
    if isinstance(value, target_type):
        return value

    value = str(value).strip().lower()

    if target_type == bool:
        if value in ['true', '1']:
            return True
        elif value in ['false', '0']:
            return False

        raise ConversionError(f'Value {value} cannot be converted to bool.')

    try:
        if target_type == list:
            return [item.strip() for item in value.split(',')]
        elif target_type == dict:
            value = {item.split(':')[0].strip(): item.partition(':')[-1].strip() for item in value.split(',')}

        return target_type(value)
    except ValueError:
        raise ConversionError(f'Value {value} cannot be converted to {target_type}.')
