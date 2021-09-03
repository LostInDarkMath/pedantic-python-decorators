import unittest
import doctest


def run_doctests() -> None:
    unittest.TextTestRunner().run(get_doctest_test_suite())


def get_doctest_test_suite() -> unittest.TestSuite:
    parent_module = __import__('pedantic')
    modules = [
        parent_module.decorators.fn_deco_count_calls,
        parent_module.decorators.fn_deco_deprecated,
        parent_module.decorators.fn_deco_does_same_as_function,
        parent_module.decorators.fn_deco_overrides,
        parent_module.decorators.fn_deco_pedantic,
        parent_module.decorators.fn_deco_rename_kwargs,
        parent_module.decorators.fn_deco_timer,
        parent_module.decorators.fn_deco_trace,
        parent_module.decorators.fn_deco_trace_if_returns,
        parent_module.decorators.fn_deco_unimplemented,
        parent_module.type_checking_logic.check_types,
        parent_module.type_checking_logic.check_generic_classes,
        parent_module.type_checking_logic.check_docstring,
    ]
    test_suites = [doctest.DocTestSuite(module=module, optionflags=doctest.ELLIPSIS) for module in modules]
    return unittest.TestSuite(test_suites)


if __name__ == '__main__':
    run_doctests()
