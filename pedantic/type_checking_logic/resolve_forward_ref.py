from typing import *  # useful for globals(), see below


def resolve_forward_ref(type_: str, globals_: Dict[str, Any] = None, context: Dict = None) -> Type:
    """
        Resolve a type annotation that is a string.

        Raises:
            NameError: in case of [type_] cannot be resolved.
    """

    return eval(str(type_), globals_ or globals(), context or {})
