from abc import ABC, abstractmethod
from typing import Any


class Deserializable(ABC):
    """A tiny interface which has a static from_json() method which acts like a named constructor."""

    @staticmethod
    @abstractmethod
    def from_json(data: dict[str, Any]) -> 'Deserializable':
        """A named constructor which creates an object from JSON."""
