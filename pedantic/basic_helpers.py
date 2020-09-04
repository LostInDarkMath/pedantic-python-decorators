from typing import Any, Callable


def get_qual_name_msg(func: Callable[..., Any]) -> str:
    """uniform design for error messages"""
    return f'In function {func.__qualname__}:' + '\n'
