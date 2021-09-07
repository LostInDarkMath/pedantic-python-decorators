import re

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators import Validator

REGEX_EMAIL = r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$"


class Email(Validator):
    def __init__(self, email_pattern: str = REGEX_EMAIL) -> None:
        self._pattern = email_pattern

    @overrides(Validator)
    def validate(self, value: str) -> str:
        if not re.fullmatch(pattern=self._pattern, string=value):
            raise ValidationError(f'invalid email address: {value}')

        return value
