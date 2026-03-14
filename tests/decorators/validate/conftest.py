import os

import pytest


@pytest.fixture(autouse=True)
def cleanup_env_vars() -> None:
    if 'FOO' in os.environ:
        del os.environ['FOO']
