from collections.abc import Callable
from typing import TypeVar as Tv

TYPE_VAR_METHOD_NAME = '__pedantic_m42__'
TYPE_VAR_ATTR_NAME = '__pedantic_a42__'
TYPE_VAR_SELF = Tv('__pedantic_t42__')  # noqa: PLC0132
ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED = '__pedantic_g42__'

TypeVar = Tv
ReturnType = TypeVar('ReturnType')
F = Callable[..., ReturnType]
C = TypeVar('C')
K = TypeVar('K')
V = TypeVar('V')
