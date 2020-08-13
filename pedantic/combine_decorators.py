from typing import List, Callable, Any


def combine(decorators: List[Callable[[Callable[..., Any]], Callable[..., Any]]]) -> Callable[..., Any]:
    """Use multiple decorators on the same class or method without any conflicts.

    Examples (see unit tests for details):
        - @combine([pedantic, overrides(ParentClass)])
        - @combine([pedantic, validate_args(lambda x: x > 42)])
        - @combine([pedantic_class, trace_class])
    """
    def get_combined_decorator(func: Callable[..., Any], ) -> Callable[..., Any]:
        def master_decorator(*args, **kwargs) -> Any:
            results = []
            for decorator in decorators:
                results.append(decorator(func)(*args, **kwargs))
                assert len(set(results)) <= 1, \
                    f'The method "{func.__name__}" returned different results for different decorators: {results}'
            return func(*args, **kwargs)
        return master_decorator
    return get_combined_decorator
