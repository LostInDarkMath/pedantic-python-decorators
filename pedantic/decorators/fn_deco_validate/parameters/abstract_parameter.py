from typing import Iterable, Any

from pedantic.decorators.fn_deco_validate.exceptions import ValidationError
from pedantic.decorators.fn_deco_validate.validators.abstract_validator import Validator


class Parameter:
    def __init__(self, name: str, validators: Iterable[Validator] = None) -> None:
        self.name = name
        self.validators = validators if validators else []

    def validate(self, value: Any) -> Any:
        """ Apply all validators to the given value and collect all ValidationErrors. """

        result_value = value
        errors = []

        for validator in self.validators:
            try:
                result_value = validator.validate(value=result_value)
            except ValidationError as e:
                errors.append(e)

        if errors:
            raise ValidationError(errors=errors)

        return result_value
