import sys

from pedantic.class_decorators \
    import pedantic_class, pedantic_class_require_docstring, timer_class, trace_class, for_all_methods

from pedantic.method_decorators import pedantic, pedantic_require_docstring, trace, timer, \
    needs_refactoring, dirty, unimplemented, deprecated, validate_args, \
    require_kwargs, trace_if_returns, does_same_as_function, overrides

from pedantic.exceptions import NotImplementedException, TooDirtyException

from pedantic.unit_tests.tests_main import run_all_tests

from pedantic.set_envionment_variables import disable_pedantic, enable_pedantic, is_enabled

assert sys.version_info >= (3, 6), f'Pedantic does not work with Python versions below 3.6.'
