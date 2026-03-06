from typing import *  # noqa: F403, useful for globals(), see below


def resolve_forward_ref(type_: str, globals_: dict[str, Any] | None = None, context: dict | None = None) -> type:  # noqa: F405
    """
    Resolve a type annotation that is a string.

    Raises:
        NameError: in case of [type_] cannot be resolved.
    """

    return eval(str(type_), globals_ or globals(), context or {})  # # noqa: S307
