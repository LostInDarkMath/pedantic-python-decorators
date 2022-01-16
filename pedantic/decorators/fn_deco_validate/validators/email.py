import re
from typing import Callable

from pedantic import overrides
from pedantic.decorators.fn_deco_validate.validators import Validator

REGEX_EMAIL = r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$"


class Email(Validator):
    def __init__(self, email_pattern: str = REGEX_EMAIL, post_processor: Callable[[str], str] = lambda x: x) -> None:
        self._pattern = email_pattern
        self._post_processor = post_processor

    @overrides(Validator)
    def validate(self, value: str) -> str:
        if not re.fullmatch(pattern=self._pattern, string=value):
            self.raise_exception(msg=f'invalid email address: {value}', value=value)

        return self._post_processor(value)
