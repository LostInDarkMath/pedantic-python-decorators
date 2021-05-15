
class NotImplementedException(Exception):
    pass


class PedanticException(Exception):
    pass


class PedanticTypeCheckException(PedanticException):
    pass


class PedanticDocstringException(PedanticException):
    pass


class PedanticOverrideException(PedanticException):
    pass


class PedanticCallWithArgsException(PedanticException):
    pass


class PedanticTypeVarMismatchException(PedanticException):
    pass
