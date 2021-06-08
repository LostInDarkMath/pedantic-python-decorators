from typing import Any, Iterable, Union, Dict, List


class ValidationError(Exception):
    def __init__(self,
                 message: str = 'invalid parameter',
                 validator_name: str = '',
                 value: Any = None,
                 errors: Iterable['ValidationError'] = None,
                 ) -> None:
        self.validator_name = validator_name
        self.value = value
        self.message = message
        self.errors = errors if errors else []

    def __str__(self) -> str:
        return f'Rule: {self.validator_name}, Value: {self.value}, Message: {self.message}'

    @property
    def to_dict(self) -> Union[Dict[str, str], List[Dict[str, str]]]:
        if self.errors:
            return [error.to_dict for error in self.errors]

        return {
            'rule': self.validator_name,
            'value': str(self.value),
            'message': self.message,
        }
