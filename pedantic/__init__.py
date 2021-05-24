import sys

assert sys.version_info >= (3, 6), f'Pedantic does not work with Python versions below 3.6.'

from pedantic.decorators import overrides, rename_kwargs, timer, count_calls, trace, trace_if_returns, \
    does_same_as_function, deprecated, unimplemented, require_kwargs, validate_args, pedantic, \
    pedantic_require_docstring, for_all_methods, trace_class, timer_class, pedantic_class, \
    pedantic_class_require_docstring, Rename, mock

from pedantic.exceptions import NotImplementedException

from pedantic.tests.tests_main import run_all_tests

from pedantic.env_var_logic import disable_pedantic, enable_pedantic, is_enabled
