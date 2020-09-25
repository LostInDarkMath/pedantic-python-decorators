from typing import Any, Callable


TYPE_VAR_METHOD_NAME = '__pedantic_m42__'
TYPE_VAR_ATTR_NAME = '__pedantic_a42__'


def get_qualified_name_for_err_msg(func: Callable[..., Any]) -> str:
    return f'In function {func.__qualname__}:' + '\n'
