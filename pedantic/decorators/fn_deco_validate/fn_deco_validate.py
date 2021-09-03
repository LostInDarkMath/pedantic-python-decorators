import inspect
from enum import Enum
from functools import wraps
from typing import Any, Callable

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.parameters import Parameter, ExternalParameter


class ReturnAs(Enum):
    KWARGS = 'KWARGS'
    ARGS = 'ARGS'


def validate(*parameters: Parameter, return_as: ReturnAs = ReturnAs.KWARGS, strict: bool = True) -> Callable:
    """
        Validates the values that are passed to the function by using the validators in the passed parameters.

        Args:
            parameters (multiple Parameter): The parameters that will be validated.
            return_as (ReturnAs): Pass the arguments as kwargs to the decorated function if ReturnAs.KWARGS.
                Positional arguments are used otherwise.
            strict (bool): If strict is true, you have to define a Parameter for each of the
                arguments the decorated function takes.

        Returns:
            Callable: The decorated function.
    """

    def validator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = {}
            parameter_dict = {parameter.name: parameter for parameter in parameters}
            used_parameters = []

            for k, v in kwargs.items():
                if k in parameter_dict:
                    parameter = parameter_dict[k]
                    result[k] = parameter.validate(value=v)
                    used_parameters.append(parameter.name)
                else:
                    if strict:
                        raise ValidationError(f'Got more arguments expected: No parameter found for argument {k}')
                    else:
                        result[k] = v

            bound_args = inspect.signature(func).bind_partial(*args).arguments

            for k in bound_args:
                if k in parameter_dict:
                    parameter = parameter_dict[k]
                    result[k] = parameter.validate(value=bound_args[k])
                    used_parameters.append(parameter.name)
                else:
                    if strict and k != 'self':
                        raise ValidationError(f'Got more arguments expected: No parameter found for argument {k}')
                    else:
                        result[k] = bound_args[k]

            unused_parameters = [parameter for parameter in parameters if parameter.name not in used_parameters]

            for parameter in unused_parameters:
                if not isinstance(parameter, ExternalParameter):
                    raise ValidationError(f'Got no value for parameter {parameter.name}')

                value = parameter.load_value()
                result[parameter.name] = parameter.validate(value=value)

            if return_as == ReturnAs.KWARGS:
                if 'self' in result:
                    return func(result.pop('self'), **result)
                else:
                    return func(**result)
            else:
                return func(*result.values())  # TODO bug
        return wrapper
    return validator
