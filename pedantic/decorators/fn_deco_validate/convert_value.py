from typing import Any

from pedantic.decorators.fn_deco_validate.exceptions import ConversionError

T = bool | int | float | str | dict | list


def convert_value(value: Any, target_type: type[T]) -> T:  # noqa: D103
    if isinstance(value, target_type):
        return value

    value = str(value).strip().lower()

    if target_type is bool:
        if value in ['true', '1']:
            return True
        if value in ['false', '0']:
            return False

        raise ConversionError(f'Value {value} cannot be converted to bool.')

    try:
        if target_type is list:
            return [item.strip() for item in value.split(',')]
        if target_type is dict:
            value = {item.split(':')[0].strip(): item.partition(':')[-1].strip() for item in value.split(',')}

        return target_type(value)
    except ValueError as ex:
        raise ConversionError(f'Value {value} cannot be converted to {target_type}.') from ex
