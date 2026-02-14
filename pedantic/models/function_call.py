import inspect
from typing import Any, ForwardRef

from pedantic.constants import TYPE_VAR_METHOD_NAME, TYPE_VAR_SELF, ReturnType, TypeVar
from pedantic.exceptions import PedanticCallWithArgsException, PedanticTypeCheckException
from pedantic.models.decorated_function import DecoratedFunction
from pedantic.models.generator_wrapper import GeneratorWrapper
from pedantic.type_checking_logic.check_types import assert_value_matches_type


class FunctionCall:
    """Represents a function call."""

    def __init__(  # noqa: D107
        self,
        func: DecoratedFunction,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        context: dict[str, type],
    ) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._context = context
        self._instance = self.args[0] if self.func.is_instance_method else None
        self._type_vars = {}
        self._params_without_self = {k: v for k, v in self.func.signature.parameters.items() if v.name != 'self'}
        self._already_checked_kwargs = []
        self._get_type_vars = lambda: self._type_vars

    @property
    def func(self) -> DecoratedFunction:  # noqa: D102
        return self._func

    @property
    def args(self) -> tuple[Any, ...]:  # noqa: D102
        return self._args

    @property
    def kwargs(self) -> dict[str, Any]:  # noqa: D102
        return self._kwargs

    @property
    def not_yet_check_kwargs(self) -> dict[str, Any]:  # noqa: D102
        return {k: v for k, v in self._kwargs.items() if k not in self._already_checked_kwargs}

    @property
    def type_vars(self) -> dict[TypeVar, Any]:  # noqa: D102
        if hasattr(self._instance, TYPE_VAR_METHOD_NAME):
            self._get_type_vars = getattr(self._instance, TYPE_VAR_METHOD_NAME)

        res = self._get_type_vars()

        if TYPE_VAR_SELF not in res:
            res[TYPE_VAR_SELF] = self.clazz

        return res

    @property
    def clazz(self) -> type | None:
        """Returns the enclosing class of the called function if there is one."""

        if self._instance is not None:
            # case instance method
            return type(self._instance)
        if self.func.is_class_method:
            return self.func.func.__self__
        if self.func.is_static_method:
            if not self.args:
                # static method was called on class
                class_name = self.func.full_name.split('.')[-2]
                return ForwardRef(class_name)   # this ForwardRef is resolved later

            # static method was called on instance
            return type(self.args[0])

        return None

    @property
    def params_without_self(self) -> dict[str, inspect.Parameter]:  # noqa: D102
        return self._params_without_self

    @property
    def args_without_self(self) -> tuple[Any, ...]:  # noqa: D102
        max_allowed = 0 if not self.func.is_pedantic else 1
        uses_multiple_decorators = self.func.num_of_decorators > max_allowed

        if self.func.is_instance_method or self.func.is_static_method or uses_multiple_decorators:
            return self.args[1:]  # self is always the first argument if present
        return self.args

    def assert_uses_kwargs(self) -> None:  # noqa: D102
        if self.func.should_have_kwargs and self.args_without_self:
            raise PedanticCallWithArgsException(
                f'{self.func.err}Use kwargs when you call function {self.func.name}. Args: {self.args_without_self}')

    def check_types(self) -> ReturnType:
        """Performs type checking on return value."""
        self._check_types_of_arguments()
        return self._check_types_return(result=self._get_return_value())

    async def async_check_types(self) -> ReturnType:
        """Performs type checking on return value."""
        self._check_types_of_arguments()
        return self._check_types_return(result=await self._async_get_return_value())

    def _check_types_of_arguments(self) -> None:
        d = self.params_without_self.items()
        self._check_type_param(params={k: v for k, v in d if not str(v).startswith('*')})
        self._check_types_args(params={k: v for k, v in d if str(v).startswith('*') and not str(v).startswith('**')})
        self._check_types_kwargs(params={k: v for k, v in d if str(v).startswith('**')})

    def _check_type_param(self, params: dict[str, inspect.Parameter]) -> None:
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
            elif key in self.kwargs:
                actual_value = self.kwargs[key]
            else:
                actual_value = param.default

            assert_value_matches_type(
                value=actual_value,
                type_=param.annotation,
                err=self.func.err,
                type_vars=self.type_vars,
                key=key,
                context=self._context,
            )

    def _check_types_args(self, params: dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        expected = next(iter(params.values())).annotation  # it's not possible to have more than 1

        for arg in self.args:
            assert_value_matches_type(
                value=arg,
                type_=expected,
                err=self.func.err,
                type_vars=self.type_vars,
                context=self._context,
            )

    def _check_types_kwargs(self, params: dict[str, inspect.Parameter]) -> None:
        if not params:
            return

        param = next(iter(params.values())) # it's not possible to have more than 1
        self._assert_param_has_type_annotation(param=param)

        for kwarg in self.not_yet_check_kwargs:
            actual_value = self.kwargs[kwarg]
            assert_value_matches_type(
                value=actual_value,
                type_=param.annotation,
                err=self.func.err,
                type_vars=self.type_vars,
                key=kwarg,
                context=self._context,
            )

    def _check_types_return(self, result: Any) -> GeneratorWrapper | None:
        if self.func.signature.return_annotation is inspect.Signature.empty:
            raise PedanticTypeCheckException(
                f'{self.func.err}There should be a type hint for the return type (e.g. None if nothing is returned).')

        expected_result_type = self.func.annotations['return']

        if self.func.is_generator:
            return GeneratorWrapper(
                wrapped=result, expected_type=expected_result_type, err_msg=self.func.err, type_vars=self.type_vars)

        msg = (
            f'{self.func.err}Type hint of return value is incorrect: Expected type {expected_result_type} '
            f'but {result} of type {type(result)} was the return value which does not match.'
        )
        assert_value_matches_type(
            value=result,
            type_=expected_result_type,
            err=self.func.err,
            type_vars=self.type_vars,
            msg=msg,
            context=self._context,
        )
        return result

    def _assert_param_has_type_annotation(self, param: inspect.Parameter) -> None:
        if param.annotation == inspect.Parameter.empty:
            raise PedanticTypeCheckException(f'{self.func.err}Parameter "{param.name}" should have a type hint.')

    def _get_return_value(self) -> Any:
        if self.func.is_static_method or self.func.is_class_method:
            return self.func.func(**self.kwargs)

        return self.func.func(*self.args, **self.kwargs)

    async def _async_get_return_value(self) -> Any:
        if self.func.is_static_method or self.func.is_class_method:
            return await self.func.func(**self.kwargs)

        return await self.func.func(*self.args, **self.kwargs)
