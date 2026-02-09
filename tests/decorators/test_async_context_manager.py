import pytest

from pedantic.decorators import safe_async_contextmanager


@pytest.mark.asyncio
async def test_safe_context_manager_no_exception():
    before = False
    after = False

    @safe_async_contextmanager
    async def foo():
        nonlocal before, after
        before = True
        yield 42
        after = True

    assert before is False
    assert after is False

    async with foo() as f:
        assert before is True
        assert after is False
        assert f == 42

    assert before is True
    assert after is True


@pytest.mark.asyncio
async def test_safe_context_manager_with_exception():
    before = False
    after = False

    @safe_async_contextmanager
    async def foo():
        nonlocal before, after
        before = True
        yield 42
        after = True

    assert before is False
    assert after is False

    with pytest.raises(expected_exception=ValueError):
        async with foo() as f:
            assert before is True
            assert after is False
            assert f == 42
            raise ValueError('oh no')

    assert before is True
    assert after is True


@pytest.mark.asyncio
async def test_safe_context_manager_with_args_kwargs():
    @safe_async_contextmanager
    async def foo(a, b):
        yield a, b

    async with foo(42, b=43) as f:
        assert f == (42, 43)


def test_safe_context_manager_async():
    with pytest.raises(expected_exception=AssertionError) as err:
        @safe_async_contextmanager
        def foo(a, b):
            yield a, b

    expected = 'foo is not an async generator. So you need to use "safe_contextmanager" instead.'
    assert err.value.args[0] == expected


@pytest.mark.asyncio
async def test_safe_context_manager_non_generator():
    with pytest.raises(expected_exception=AssertionError) as err:
        @safe_async_contextmanager
        async def foo(a, b):
            return a, b

    expected = 'foo is not a generator.'
    assert err.value.args[0] == expected
