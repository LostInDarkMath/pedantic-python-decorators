import sys


def get_context(depth: int = 1, increase_depth_if_name_matches: list[str] | None = None) -> dict[str, type]:
    """
    Get the context of a frame at the given depth of the current call stack.

    See also: https://docs.python.org/3/library/sys.html#sys._getframe
    """

    frame = sys._getframe(depth)  # noqa: SLF001
    name = frame.f_code.co_name

    if name in (increase_depth_if_name_matches or []):
        frame = sys._getframe(depth + 1)  # noqa: SLF001

    return {**frame.f_globals, **frame.f_locals}
