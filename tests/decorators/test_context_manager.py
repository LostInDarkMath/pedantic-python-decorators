import pytest

from pedantic.decorators import safe_contextmanager


def test_safe_context_manager_no_exception():
    before = False
    after = False

    @safe_contextmanager
    def foo():
        nonlocal before, after
        before = True
        yield 42
        after = True

    assert before is False
    assert after is False

    with foo() as f:
        assert before is True
        assert after is False
        assert f == 42

    assert before is True
    assert after is True


def test_safe_context_manager_with_exception():
    before = False
    after = False

    @safe_contextmanager
    def foo():
        nonlocal before, after
        before = True
        yield 42
        after = True

    assert before is False
    assert after is False

    with pytest.raises(expected_exception=ValueError):
        with foo() as f:
            assert before is True
            assert after is False
            assert f == 42
            raise ValueError('oh no')

    assert before is True
    assert after is True


def test_safe_context_manager_with_args_kwargs():
    @safe_contextmanager
    def foo(a, b):
        yield a, b

    with foo(42, b=43) as f:
        assert f == (42, 43)


def test_safe_context_manager_async():
    with pytest.raises(expected_exception=AssertionError) as err:
        @safe_contextmanager
        async def foo(a, b):
            yield a, b

    expected = 'foo is async. So you need to use "safe_async_contextmanager" instead.'
    assert err.value.args[0] == expected


def test_safe_context_manager_non_generator():
    with pytest.raises(expected_exception=AssertionError) as err:
        @safe_contextmanager
        def foo(a, b):
            return a, b

    expected = 'foo is not a generator.'
    assert err.value.args[0] == expected
