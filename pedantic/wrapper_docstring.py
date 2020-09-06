from typing import Any, Callable

# third party imports
from docstring_parser import parse, Docstring

# local file imports
from pedantic.basic_helpers import get_qualified_name_for_err_msg


def get_parsed_docstring(func: Callable[..., Any]) -> Docstring:
    try:
        return parse(func.__doc__)
    except (Exception, TypeError) as ex:
        raise AssertionError(
            f'{get_qualified_name_for_err_msg(func=func)} '
            f'Could not parse docstring. Please check syntax. Details: {ex}')
