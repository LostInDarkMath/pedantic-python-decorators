from typing import Dict, Tuple, Any

from pedantic.constants import TypeVar, TYPE_VAR_METHOD_NAME
from pedantic.models.decorated_function import DecoratedFunction


class FunctionCall:
    def __init__(self, func: DecoratedFunction, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._instance = self.args[0] if self.func.is_instance_method else None
        self._type_vars = dict()
        self._params_without_self = {k: v for k, v in self.func.signature.parameters.items() if v.name != 'self'}

        if self._instance and hasattr(self._instance, TYPE_VAR_METHOD_NAME):
            self._get_type_vars = getattr(self._instance, TYPE_VAR_METHOD_NAME)
        else:
            self._get_type_vars = lambda: self._type_vars

    @property
    def func(self) -> DecoratedFunction:
        return self._func

    @property
    def args(self) -> Tuple[Any, ...]:
        return self._args

    @property
    def kwargs(self) -> Dict[str, Any]:
        return self._kwargs

    @property
    def type_vars(self) -> Dict[TypeVar, Any]:
        if hasattr(self._instance, TYPE_VAR_METHOD_NAME):
            self._get_type_vars = getattr(self._instance, TYPE_VAR_METHOD_NAME)
        return self._get_type_vars()

    @property
    def params_without_self(self):
        return self._params_without_self

    @property
    def args_without_self(self) -> Tuple[Any, ...]:
        max_allowed = 0 if not self.func.is_pedantic else 1
        uses_multiple_decorators = self.func.num_of_decorators > max_allowed
        if self.func.is_instance_method or self.func.is_static_method or uses_multiple_decorators:
            return self.args[1:]  # self is always the first argument if present
        return self.args
