import os

ENVIRONMENT_VARIABLE_NAME = 'ENABLE_PEDANTIC'


def enable_pedantic() -> None:  # noqa: D103
    os.environ[ENVIRONMENT_VARIABLE_NAME] = '1'


def disable_pedantic() -> None:  # noqa: D103
    os.environ[ENVIRONMENT_VARIABLE_NAME] = '0'


def is_enabled() -> bool: # noqa: D103
    if ENVIRONMENT_VARIABLE_NAME not in os.environ:
        return True

    return os.environ[ENVIRONMENT_VARIABLE_NAME] == '1'
