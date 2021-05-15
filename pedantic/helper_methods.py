import warnings
from typing import Type


def _raise_warning(msg: str, category: Type[Warning]) -> None:
    warnings.simplefilter(action='always', category=category)
    warnings.warn(message=msg, category=category, stacklevel=2)
    warnings.simplefilter(action='default', category=category)
