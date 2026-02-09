import pytest

from pedantic import deprecated


def test_deprecated_no_args():
    @deprecated
    def old_method(i: int) -> str: return str(i)

    with pytest.warns(DeprecationWarning, match="deprecated"):
        old_method(42)


def test_deprecated_with_args():
    @deprecated(message="my deprecation message")
    def old_method(i: int) -> str:
        return str(i)

    with pytest.warns(DeprecationWarning, match="my deprecation message"):
        old_method(42)


@pytest.mark.asyncio
async def test_deprecated_async():
    @deprecated
    async def old_method(i: int) -> str:
        return str(i)

    with pytest.warns(DeprecationWarning, match="deprecated"):
        await old_method(42)
