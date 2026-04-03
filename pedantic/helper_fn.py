import doctest
from collections.abc import Callable


def run_doctest_of_single_function(f: Callable) -> None:
    """Useful for debugging a function with doctests."""

    finder = doctest.DocTestFinder()
    runner = doctest.DocTestRunner()

    # Find doctests attached to the function
    tests = finder.find(f)

    # Run them
    for test in tests:
        runner.run(test)

    # Fail the pytest test if any doctest failed
    results = runner.summarize()

    if results.failed > 0:
        raise AssertionError(f'Failed tests: {results.failed}')
