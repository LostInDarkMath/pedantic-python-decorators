from typing import Any, Callable, TypeVar as Tv
import sys


TYPE_VAR_METHOD_NAME = '__pedantic_m42__'
TYPE_VAR_ATTR_NAME = '__pedantic_a42__'
TypeVar = Tv if sys.version_info >= (3, 7) else type
# because in Python 3.6 there is a bug: https://github.com/python/typing/issues/520


def get_qualified_name_for_err_msg(func: Callable[..., Any]) -> str:
    return f'In function {func.__qualname__}:' + '\n'
