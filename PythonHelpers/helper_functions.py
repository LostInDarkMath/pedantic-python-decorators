from sys import version_info
from typing import Tuple


def get_python_version() -> Tuple[int, int]:
    """Returns (3, 8) when called with Python version 3.8.x"""
    return version_info[:2]
