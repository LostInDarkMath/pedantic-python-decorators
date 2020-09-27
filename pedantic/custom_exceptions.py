
class NotImplementedException(Exception):
    pass


class TooDirtyException(Exception):
    pass


class PedanticException(Exception):
    pass


class PedanticTypeCheckException(PedanticException):
    def __init__(self, salary, message="Salary is not in (5000, 15000) range"):
        self.salary = salary
        self.message = message
        super().__init__(self.message)


class PedanticDocstringException(PedanticException):
    pass


class PedanticOverrideException(PedanticException):
    pass