class PedanticException(Exception):  # noqa: N818
    """The base exception class for all Pedantic exceptions."""


class PedanticTypeCheckException(PedanticException):
    """Raised if a type hint is incorrect."""


class PedanticDocstringException(PedanticException):
    """Raised if the docstring is invalid e.g., wrong types"""


class PedanticOverrideException(PedanticException):
    """Raised when a child class overrides a method that the parent class does not have."""


class PedanticCallWithArgsException(PedanticException):
    """Raised if a function is called with kwargs but is called with args."""


class PedanticTypeVarMismatchException(PedanticException):
    """Raised if a TypeVar type conflict happens."""
