from typing import TypeVar as Tv, Callable, Dict, Mapping
import sys


TYPE_VAR_METHOD_NAME = '__pedantic_m42__'
TYPE_VAR_ATTR_NAME = '__pedantic_a42__'
ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED = '__pedantic_g42__'

TypeVar = Tv if sys.version_info >= (3, 7) else type
# because in Python 3.6 there is a bug: https://github.com/python/typing/issues/520

ReturnType = TypeVar('Return Type')
F = Callable[..., ReturnType]
C = TypeVar('Class')
K = TypeVar('Key')
V = TypeVar('Value')
