import inspect
from enum import Enum
from functools import wraps
from typing import Any, Callable, List

from pedantic.decorators.fn_deco_validate.exceptions import ValidateException, TooManyArguments
from pedantic.decorators.fn_deco_validate.parameters import Parameter, ExternalParameter

try:
    from flask import request
    from pedantic.decorators.fn_deco_validate.parameters.flask_parameters import FlaskJsonParameter
    IS_FLASK_INSTALLED = True
except ImportError:
    IS_FLASK_INSTALLED = False


class ReturnAs(Enum):
    ARGS = 'ARGS'
    KWARGS_WITH_NONE = 'KWARGS_WITH_NONE'
    KWARGS_WITHOUT_NONE = 'KWARGS_WITHOUT_NONE'


def validate(
        *parameters: Parameter,
        return_as: ReturnAs = ReturnAs.KWARGS_WITHOUT_NONE,
        strict: bool = True,
) -> Callable:
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
            used_parameter_names: List[str] = []

            for k, v in kwargs.items():
                if k in parameter_dict:
                    parameter = parameter_dict[k]
                    result[k] = parameter.validate(value=v)
                    used_parameter_names.append(parameter.name)
                else:
                    if strict:
                        raise TooManyArguments(f'Got more arguments expected: No parameter found for argument {k}')
                    else:
                        result[k] = v

            signature = inspect.signature(func)
            wants_args = '*args' in str(signature)
            used_args = []

            try:
                bound_args = signature.bind_partial(*args).arguments
            except TypeError as ex:
                raise ValidateException(str(ex))

            for k in bound_args:
                if k == 'args' and wants_args:
                    for arg, parameter in zip(
                            [a for a in args if a not in used_args],
                            [p for p in parameters if p.name not in used_parameter_names]
                    ):
                        print(f'Validate value {arg} with {parameter}')
                        result[parameter.name] = parameter.validate(arg)
                        used_parameter_names.append(parameter.name)
                elif k in parameter_dict:
                    parameter = parameter_dict[k]
                    result[k] = parameter.validate(value=bound_args[k])
                    used_parameter_names.append(parameter.name)
                    used_args.append(bound_args[k])
                else:
                    if strict and k != 'self':
                        raise TooManyArguments(f'Got more arguments expected: No parameter found for argument {k}')
                    else:
                        result[k] = bound_args[k]

            unused_parameters = [parameter for parameter in parameters if parameter.name not in used_parameter_names]

            for parameter in unused_parameters:
                if not isinstance(parameter, ExternalParameter):
                    if not parameter.is_required:
                        continue

                    raise ValidateException(f'Got no value for parameter {parameter.name}')

                value = parameter.load_value()
                validated_value = parameter.validate(value=value)
                result[parameter.name] = validated_value

            # this is ugly, but i really want this behavior
            if strict and IS_FLASK_INSTALLED:
                if all([isinstance(p, FlaskJsonParameter) for p in parameter_dict.values()]):
                    unexpected_args = [k for k in request.json if k not in parameter_dict]

                    if unexpected_args:
                        raise TooManyArguments(f'Got unexpected arguments: {unexpected_args}')

            if return_as == ReturnAs.ARGS:
                return func(*result.values())

            if return_as == ReturnAs.KWARGS_WITHOUT_NONE:
                result = {k: v for k, v in result.items() if v is not None and 'self'}

            if 'self' in result:
                return func(result.pop('self'), **result)

            return func(**result)
        return wrapper
    return validator
