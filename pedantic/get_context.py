import sys
from typing import Type, Dict


def get_context(depth: int = 1) -> Dict[str, Type]:
    """
        Get the context of a frame at the given depth of the current call stack.
        See also: https://docs.python.org/3/library/sys.html#sys._getframe
    """

    frame = sys._getframe(depth)
    return {**frame.f_globals, **frame.f_locals}
