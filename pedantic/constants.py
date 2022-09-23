from typing import TypeVar as Tv, Callable


TYPE_VAR_METHOD_NAME = '__pedantic_m42__'
TYPE_VAR_ATTR_NAME = '__pedantic_a42__'
ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED = '__pedantic_g42__'

TypeVar = Tv
ReturnType = TypeVar('ReturnType')
F = Callable[..., ReturnType]
C = TypeVar('C')
K = TypeVar('K')
V = TypeVar('V')
