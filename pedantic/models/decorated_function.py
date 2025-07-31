import inspect
import re
from typing import Any, Callable, Dict, Optional

try:
    from docstring_parser import parse, Docstring
    IS_DOCSTRING_PARSER_INSTALLED = True
except ImportError:
    IS_DOCSTRING_PARSER_INSTALLED = False
    Docstring = None
    parse = None

from pedantic.exceptions import PedanticTypeCheckException

FUNCTIONS_THAT_REQUIRE_KWARGS = [
    '__new__', '__init__', '__str__', '__del__', '__int__', '__float__', '__complex__', '__oct__', '__hex__',
    '__index__', '__trunc__', '__repr__', '__unicode__', '__hash__', '__nonzero__', '__dir__', '__sizeof__'
]


class DecoratedFunction:
    def __init__(self, func: Callable[..., Any]) -> None:
        self._func = func

        if not callable(func):
            raise PedanticTypeCheckException(f'{self.full_name} should be a method or function.')

        self._full_arg_spec = inspect.getfullargspec(func)
        self._signature = inspect.signature(func)
        self._err = f'In function {self.full_name}:\n'

        try:
            source = inspect.getsource(object=func)
        except TypeError:
            source = None

        self._source: str | None = source

        if IS_DOCSTRING_PARSER_INSTALLED:
            self._docstring = parse(func.__doc__)
        else:  # pragma: no cover
            self._docstring = None

    @property
    def func(self) -> Callable[..., Any]:
        return self._func

    @property
    def annotations(self) -> Dict[str, Any]:
        return self._full_arg_spec.annotations

    @property
    def docstring(self) -> Optional[Docstring]:
        """
            Returns the docstring if the docstring-parser package is installed else None.
            See also https://pypi.org/project/docstring-parser/
        """

        return self._docstring

    @property
    def raw_doc(self) -> Optional[str]:
        return self._func.__doc__

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
        if hasattr(self._func, '__name__'):
            return self._func.__name__

        return self._func.func.__name__

    @property
    def full_name(self) -> str:
        if hasattr(self._func, '__qualname__'):
            return self._func.__qualname__

        return self._func.func.__qualname__

    @property
    def is_static_method(self) -> bool:
        """ I honestly have no idea how to do this better :( """

        if self.source is None:
            return False

        return '@staticmethod' in self.source

    @property
    def wants_args(self) -> bool:
        if self.source is None:
            return False

        return '*args' in self.source

    @property
    def is_property_setter(self) -> bool:
        if self.source is None:
            return False

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
    def is_class_method(self) -> bool:
        """
            Returns true if the function is decoratorated with the @classmethod decorator.
            See also: https://stackoverflow.com/questions/19227724/check-if-a-function-uses-classmethod
        """

        return inspect.ismethod(self._func)

    @property
    def num_of_decorators(self) -> int:
        if self.source is None:
            return 0

        return len(re.findall('@', self.source.split('def')[0]))

    @property
    def is_pedantic(self) -> bool:
        if self.source is None:
            return False

        return '@pedantic' in self.source or '@require_kwargs' in self.source

    @property
    def is_coroutine(self) -> bool:
        return inspect.iscoroutinefunction(self._func)

    @property
    def is_generator(self) -> bool:
        return inspect.isgeneratorfunction(self._func)
