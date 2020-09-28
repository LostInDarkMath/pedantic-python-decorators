import inspect
from typing import Dict, Tuple, Any

from pedantic.constants import TypeVar, TYPE_VAR_METHOD_NAME, ReturnType, filter_dict
from pedantic.exceptions import PedanticCallWithArgsException, PedanticTypeCheckException
from pedantic.check_types import check_type
from pedantic.models.decorated_function import DecoratedFunction


class FunctionCall:
    def __init__(self, func: DecoratedFunction, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._instance = self.args[0] if self.func.is_instance_method else None
        self._type_vars = dict()
        self._params_without_self = {k: v for k, v in self.func.signature.parameters.items() if v.name != 'self'}
        self._already_checked_kwargs = []

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
    def not_yet_check_kwargs(self) -> Dict[str, Any]:
        return {k: v for k, v in self._kwargs.items() if k not in self._already_checked_kwargs}

    @property
    def type_vars(self) -> Dict[TypeVar, Any]:
        if hasattr(self._instance, TYPE_VAR_METHOD_NAME):
            self._get_type_vars = getattr(self._instance, TYPE_VAR_METHOD_NAME)
        return self._get_type_vars()

    @property
    def params_without_self(self) -> Dict[str, inspect.Parameter]:
        return self._params_without_self

    @property
    def args_without_self(self) -> Tuple[Any, ...]:
        max_allowed = 0 if not self.func.is_pedantic else 1
        uses_multiple_decorators = self.func.num_of_decorators > max_allowed
        if self.func.is_instance_method or self.func.is_static_method or uses_multiple_decorators:
            return self.args[1:]  # self is always the first argument if present
        return self.args

    def assert_uses_kwargs(self) -> None:
        if self.func.should_have_kwargs and self.args_without_self:
            raise PedanticCallWithArgsException(
                f'{self.func.err} Use kwargs when you call function {self.func.name}. Args: {self.args_without_self}')

    def check_types(self) -> ReturnType:
        d = self.params_without_self
        self._check_type_param(params=filter_dict(dict_=d, filter_=lambda k, v: not str(v).startswith('*')))
        self._check_types_args(params=filter_dict(
            dict_=d, filter_=lambda k, v: str(v).startswith('*') and not str(v).startswith('**')))
        self._check_types_kwargs(params=filter_dict(dict_=d, filter_=lambda k, v: str(v).startswith('**')))
        return self._check_types_return()

    def _check_type_param(self, params: Dict[str, inspect.Parameter]) -> None:
        arg_index = 1 if self.func.is_instance_method else 0

        for key, param in params.items():
            self._already_checked_kwargs.append(key)
            self._assert_param_has_type_annotation(param=param)

            if param.default is inspect.Signature.empty:
                if self.func.should_have_kwargs:
                    if key not in self.kwargs:
                        raise PedanticTypeCheckException(f'{self.func.err} Parameter "{key}" is unfilled.')
                    actual_value = self.kwargs[key]
                else:
                    actual_value = self.args[arg_index]
                    arg_index += 1
            else:
                actual_value = self.kwargs[key] if key in self.kwargs else param.default

            if not check_type(value=actual_value, type_=param.annotation, err=self.func.err, type_vars=self.type_vars):
                raise PedanticTypeCheckException(f'{self.func.err} Type hint is incorrect: Passed Argument '
                                                 f'{key}={actual_value} does not have type {param.annotation}.')

    def _check_types_args(self, params: Dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        expected = list(params.values())[0].annotation  # it's not possible to have more then 1

        for arg in self.args:
            if not check_type(value=arg, type_=expected, err=self.func.err, type_vars=self.type_vars):
                raise PedanticTypeCheckException(
                    f'{self.func.err} Type hint is incorrect: Passed argument {arg} does not have type {expected}.')

    def _check_types_kwargs(self, params: Dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        param = list(params.values())[0]  # it's not possible to have more then 1
        self._assert_param_has_type_annotation(param=param)

        for kwarg in self.not_yet_check_kwargs:
            actual_value = self.kwargs[kwarg]
            if not check_type(value=actual_value, type_=param.annotation,
                              err=self.func.err, type_vars=self.type_vars):
                raise PedanticTypeCheckException(f'{self.func.err} Type hint is incorrect: Passed Argument {kwarg}='
                                                 f'{actual_value} does not have type {param.annotation}.')

    def _check_types_return(self) -> None:
        if self.func.signature.return_annotation is inspect.Signature.empty:
            raise PedanticTypeCheckException(
                f'{self.func.err} There should be a type hint for the return type (e.g. None if nothing is returned).')

        if self.func.is_static_method:
            result = self.func.func(**self.kwargs)
        else:
            result = self.func.func(*self.args, **self.kwargs)

        expected_result_type = self.func.annotations['return']

        if not check_type(value=result, type_=expected_result_type,
                          err=self.func.err, type_vars=self.type_vars):
            raise PedanticTypeCheckException(
                f'{self.func.err} Return type is incorrect: Expected {expected_result_type} '
                f'but {result} was the return value which does not match.')
        return result

    def _assert_param_has_type_annotation(self, param: inspect.Parameter):
        if param.annotation == inspect.Parameter.empty:
            raise PedanticTypeCheckException(f'{self.func.err} Parameter "{param.name}" should have a type hint.')
