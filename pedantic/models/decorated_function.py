import inspect
from typing import Any, Callable, Dict

# local file imports
from pedantic.basic_helpers import get_qualified_name_for_err_msg
from pedantic.wrapper_docstring import get_parsed_docstring, Docstring


class DecoratedFunction:
    def __init__(self, func: Callable[..., Any]):
        self._func = func
        self._annotations = inspect.getfullargspec(func).annotations
        self._docstring = get_parsed_docstring(func=func)
        self._signature = inspect.signature(func)
        self._err: str = get_qualified_name_for_err_msg(func=func)

    @property
    def func(self) -> Callable[..., Any]:
        return self._func

    @property
    def annotations(self) -> Dict[str, Any]:
        return self._annotations

    @property
    def docstring(self) -> Docstring:
        return self._docstring

    @property
    def signature(self) -> inspect.Signature:
        return self._signature

    @property
    def err(self) -> str:
        return self._err
