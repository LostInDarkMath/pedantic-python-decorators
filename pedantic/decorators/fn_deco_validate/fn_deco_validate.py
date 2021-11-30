import inspect
from enum import Enum
from functools import wraps
from typing import Any, Callable, List, Dict

from pedantic.decorators.fn_deco_validate.exceptions import ValidateException, TooManyArguments
from pedantic.decorators.fn_deco_validate.parameters import Parameter, ExternalParameter
from pedantic.decorators.fn_deco_validate.parameters.abstract_parameter import NoValue

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
        ignore_input: bool = False,
) -> Callable:
    """
        Validates the values that are passed to the function by using the validators in the passed parameters.
        The decorated function could also be async or an instance method as well as a normal function.

        Args:
            parameters (multiple Parameter): The parameters that will be validated.
            return_as (ReturnAs): Pass the arguments as kwargs to the decorated function if ReturnAs.KWARGS.
                Positional arguments are used otherwise.
            strict (bool): If strict is true, you have to define a Parameter for each of the
                arguments the decorated function takes.
            ignore_input (bool): If True, all given arguments passed to this decorator are ignored.
                This can be useful if you use only ExternalParameters.

        Returns:
            Callable: The decorated function.
    """

    def validator(func: Callable) -> Callable:
        is_coroutine = inspect.iscoroutinefunction(func)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = _wrapper_content(*args, **kwargs)

            if return_as == ReturnAs.ARGS:
                return func(*result.values())

            if return_as == ReturnAs.KWARGS_WITHOUT_NONE:
                result = {k: v for k, v in result.items() if v is not None}

            if 'self' in result:
                return func(result.pop('self'), **result)

            return func(**result)

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            result = _wrapper_content(*args, **kwargs)

            if return_as == ReturnAs.ARGS:
                return await func(*result.values())

            if return_as == ReturnAs.KWARGS_WITHOUT_NONE:
                result = {k: v for k, v in result.items() if v is not None}

            if 'self' in result:
                return await func(result.pop('self'), **result)

            return await func(**result)

        def _wrapper_content(*args, **kwargs) -> Dict[str, Any]:
            result = {}
            parameter_dict = {parameter.name: parameter for parameter in parameters}
            used_parameter_names: List[str] = []
            signature = inspect.signature(func)

            if not ignore_input:
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
                if isinstance(parameter, ExternalParameter):
                    if parameter.has_value():
                        v = parameter.load_value()
                        result[parameter.name] = parameter.validate(value=v)
                        continue

                if parameter.is_required:
                    return parameter.raise_exception(msg=f'Value for parameter {parameter.name} is required.')
                elif parameter.default_value == NoValue:
                    if parameter.name in signature.parameters and \
                            signature.parameters[parameter.name].default is not signature.empty:
                        value = signature.parameters[parameter.name].default
                    else:
                        raise ValidateException(f'Got neither value nor default value for parameter {parameter.name}')
                else:
                    value = parameter.default_value

                result[parameter.name] = value

            # this is ugly, but I really want this behavior
            if strict and IS_FLASK_INSTALLED:
                if all([isinstance(p, FlaskJsonParameter) for p in parameter_dict.values()]) and request.is_json:
                    unexpected_args = [k for k in request.json if k not in parameter_dict]

                    if unexpected_args:
                        raise TooManyArguments(f'Got unexpected arguments: {unexpected_args}')

            return result

        if is_coroutine:
            return async_wrapper
        else:
            return wrapper
    return validator
