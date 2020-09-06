from typing import Any, Callable


def get_qualified_name_for_err_msg(func: Callable[..., Any]) -> str:
    """uniform design for error messages"""
    return f'In function {func.__qualname__}:' + '\n'
