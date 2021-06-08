import inspect
from typing import Any, Callable

from pedantic.decorators.fn_deco_validate.parameters import Parameter, ExternalParameter


def validate(*parameters: Parameter) -> Callable:
    def validator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            for parameter in parameters:
                if isinstance(parameter, ExternalParameter):
                    value = parameter.load_value()
                else:
                    bound_arguments: inspect.BoundArguments = inspect.signature(func).bind(*args, **kwargs)
                    value = bound_arguments.arguments[parameter.name]

                kwargs[parameter.name] = parameter.validate(value=value)

            return func(**kwargs)
        return wrapper
    return validator
