import inspect
import re
import types
from typing import Any, Callable, Dict

from pedantic.basic_helpers import get_qualified_name_for_err_msg
from pedantic.wrapper_docstring import get_parsed_docstring, Docstring

FUNCTIONS_THAT_REQUIRE_KWARGS = [
    '__new__', '__init__', '__str__', '__del__', '__int__', '__float__', '__complex__', '__oct__', '__hex__',
    '__index__', '__trunc__', '__repr__', '__unicode__', '__hash__', '__nonzero__', '__dir__', '__sizeof__'
]


class DecoratedFunction:
    def __init__(self, func: Callable[..., Any]) -> None:
        assert isinstance(func, (types.FunctionType, types.MethodType)), f'{func} should be a method or function.'
        self._func = func
        self._full_arg_spec = inspect.getfullargspec(func)
        self._docstring = get_parsed_docstring(func=func)
        self._signature = inspect.signature(func)
        self._err: str = get_qualified_name_for_err_msg(func=func)
        self._source: str = inspect.getsource(object=func)

    @property
    def func(self) -> Callable[..., Any]:
        return self._func

    @property
    def annotations(self) -> Dict[str, Any]:
        return self._full_arg_spec.annotations

    @property
    def docstring(self) -> Docstring:
        return self._docstring

    @property
    def signature(self) -> inspect.Signature:
        return self._signature

    @property
    def err(self) -> str:
        return self._err

    @property
    def source(self) -> str:
        return self._source

    @property
    def name(self) -> str:
        return self._func.__name__

    @property
    def is_static_method(self) -> bool:
        return '@staticmethod' in self.source

    @property
    def wants_args(self) -> bool:
        return '*args' in self.source

    @property
    def is_property_setter(self) -> bool:
        return f'@{self.name}.setter' in self.source

    @property
    def should_have_kwargs(self) -> bool:
        if self.is_property_setter or self.wants_args:
            return False
        elif not self.name.startswith('__') or not self.name.endswith('__'):
            return True
        return self.name in FUNCTIONS_THAT_REQUIRE_KWARGS

    @property
    def is_instance_method(self) -> bool:
        return self._full_arg_spec.args != [] and self._full_arg_spec.args[0] == 'self'

    @property
    def num_of_decorators(self) -> int:
        return len(re.findall('@', self.source.split('def')[0]))
