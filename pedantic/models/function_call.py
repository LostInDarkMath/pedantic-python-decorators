import inspect
from typing import Dict, Tuple, Any, Union

from pedantic.constants import TypeVar, TYPE_VAR_METHOD_NAME, ReturnType
from pedantic.exceptions import PedanticCallWithArgsException, PedanticTypeCheckException
from pedantic.type_checking_logic.check_types import _assert_value_matches_type
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.generator_wrapper import GeneratorWrapper


class FunctionCall:
    def __init__(self, func: DecoratedFunction, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._instance = self.args[0] if self.func.is_instance_method else None
        self._type_vars = dict()
        self._params_without_self = {k: v for k, v in self.func.signature.parameters.items() if v.name != 'self'}
        self._already_checked_kwargs = []
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
                f'{self.func.err}Use kwargs when you call function {self.func.name}. Args: {self.args_without_self}')

    def check_types(self) -> ReturnType:
        d = self.params_without_self.items()
        self._check_type_param(params={k: v for k, v in d if not str(v).startswith('*')})
        self._check_types_args(params={k: v for k, v in d if str(v).startswith('*') and not str(v).startswith('**')})
        self._check_types_kwargs(params={k: v for k, v in d if str(v).startswith('**')})
        return self._check_types_return(result=self._get_return_value())

    async def async_check_types(self) -> ReturnType:
        d = self.params_without_self.items()
        self._check_type_param(params={k: v for k, v in d if not str(v).startswith('*')})
        self._check_types_args(params={k: v for k, v in d if str(v).startswith('*') and not str(v).startswith('**')})
        self._check_types_kwargs(params={k: v for k, v in d if str(v).startswith('**')})
        return self._check_types_return(result=await self._async_get_return_value())

    def _check_type_param(self, params: Dict[str, inspect.Parameter]) -> None:
        arg_index = 1 if self.func.is_instance_method else 0

        for key, param in params.items():
            self._already_checked_kwargs.append(key)
            self._assert_param_has_type_annotation(param=param)

            if param.default is inspect.Signature.empty:
                if self.func.should_have_kwargs:
                    if key not in self.kwargs:
                        raise PedanticTypeCheckException(f'{self.func.err}Parameter "{key}" is unfilled.')
                    actual_value = self.kwargs[key]
                else:
                    actual_value = self.args[arg_index]
                    arg_index += 1
            else:
                if key in self.kwargs:
                    actual_value = self.kwargs[key]
                else:
                    actual_value = param.default

            _assert_value_matches_type(value=actual_value,
                                       type_=param.annotation,
                                       err=self.func.err,
                                       type_vars=self.type_vars,
                                       key=key)

    def _check_types_args(self, params: Dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        expected = list(params.values())[0].annotation  # it's not possible to have more then 1

        for arg in self.args:
            _assert_value_matches_type(value=arg, type_=expected, err=self.func.err, type_vars=self.type_vars)

    def _check_types_kwargs(self, params: Dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        param = list(params.values())[0]  # it's not possible to have more then 1
        self._assert_param_has_type_annotation(param=param)

        for kwarg in self.not_yet_check_kwargs:
            actual_value = self.kwargs[kwarg]
            _assert_value_matches_type(value=actual_value,
                                       type_=param.annotation,
                                       err=self.func.err,
                                       type_vars=self.type_vars,
                                       key=kwarg)

    def _check_types_return(self, result: Any) -> Union[None, GeneratorWrapper]:
        if self.func.signature.return_annotation is inspect.Signature.empty:
            raise PedanticTypeCheckException(
                f'{self.func.err}There should be a type hint for the return type (e.g. None if nothing is returned).')

        expected_result_type = self.func.annotations['return']

        if self.func.is_generator:
            return GeneratorWrapper(
                wrapped=result, expected_type=expected_result_type, err_msg=self.func.err, type_vars=self.type_vars)

        msg = f'{self.func.err}Type hint of return value is incorrect: Expected type {expected_result_type} ' \
              f'but {result} of type {type(result)} was the return value which does not match.'
        _assert_value_matches_type(value=result,
                                   type_=expected_result_type,
                                   err=self.func.err,
                                   type_vars=self.type_vars,
                                   msg=msg)
        return result

    def _assert_param_has_type_annotation(self, param: inspect.Parameter):
        if param.annotation == inspect.Parameter.empty:
            raise PedanticTypeCheckException(f'{self.func.err}Parameter "{param.name}" should have a type hint.')

    def _get_return_value(self) -> Any:
        if self.func.is_static_method:
            return self.func.func(**self.kwargs)
        else:
            return self.func.func(*self.args, **self.kwargs)

    async def _async_get_return_value(self) -> Any:
        if self.func.is_static_method:
            return await self.func.func(**self.kwargs)
        else:
            return await self.func.func(*self.args, **self.kwargs)
