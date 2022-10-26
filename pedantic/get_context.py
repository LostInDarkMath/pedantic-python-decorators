import sys
from typing import Type, Dict, List


def get_context(depth: int = 1, increase_depth_if_name_matches: List[str] = None) -> Dict[str, Type]:
    """
        Get the context of a frame at the given depth of the current call stack.
        See also: https://docs.python.org/3/library/sys.html#sys._getframe
    """

    frame = sys._getframe(depth)
    name = frame.f_code.co_name

    if name in (increase_depth_if_name_matches or []):
        frame = sys._getframe(depth + 1)

    return {**frame.f_globals, **frame.f_locals}
