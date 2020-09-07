import inspect
from typing import Any, Callable, Dict

# local file imports
from pedantic.basic_helpers import get_qualified_name_for_err_msg
from pedantic.wrapper_docstring import get_parsed_docstring


class DecoratedFunction:
    def __init__(self, func: Callable[..., Any]):
        self.func = func
        self.annotations: Dict[str, Any] = inspect.getfullargspec(func).annotations
        self.docstring = get_parsed_docstring(func=func)
        self.signature = inspect.signature(func)
        self.err: str = get_qualified_name_for_err_msg(func=func)
