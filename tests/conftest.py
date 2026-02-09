import os

import pytest

from pedantic.env_var_logic import ENVIRONMENT_VARIABLE_NAME


@pytest.fixture(autouse=True)
def cleanup_env_vars() -> None:
    for env_var in [ENVIRONMENT_VARIABLE_NAME, 'foo']:
        if env_var in os.environ:
            del os.environ[env_var]
