from unittest import TestCase
from typing import List, Optional

from pedantic.exceptions import PedanticTypeCheckException, PedanticDocstringException
from pedantic.decorators.fn_deco_pedantic import pedantic_require_docstring, pedantic
from pedantic.decorators.class_decorators import pedantic_class_require_docstring, pedantic_class


class TestRequireDocstringGoogleFormat(TestCase):

    def test_no_docstring(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(n: int, m: int, i: int) -> int:
                return n + m + i

    def test_one_line_doc_string_missing_arguments_and_return(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(n: int, m: int, i: int) -> int:
                """Returns the sum of the three args."""
                return n + m + i

    def test_one_line_doc_string_corrected(self):
        @pedantic_require_docstring
        def calc(n: int, m: int, i: int) -> int:
            """Returns the sum of the three args.

            Args:
                n (int): something
                m (int): something
                i (int): something

            Returns:
                int: bar
            """
            return n + m + i

        calc(n=42, m=40, i=38)

    def test_list_vs_typing_list(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)

                Returns:
                    list: a list of strings representing the header columns
                """
                return [file_loc, str(print_cols)]

    def test_google_docstring_2(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
                List[str]: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols)]

        calc(file_loc='Hi', print_cols=False)

    def test_google_docstring_3(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
                List[str]: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols)]

        calc(file_loc='Hi', print_cols=False)

    def test_more_parameter_documented_than_the_function_takes(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)
                    amount (int): THIS ARGUMENT IS NOT TAKEN BY THE FUNCTION

                Returns:
                    List[str]: a list of strings representing the header columns
                """
                return [file_loc, str(print_cols)]

    def test_google_docstring_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool, amount: int) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
                amount (int): now it is

            Returns:
                List[str]: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols), str(amount)]

        calc(file_loc='Hi', print_cols=False, amount=42)

    def test_no_args_keyword_before_documented_arguments(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> list:
                """Gets and prints the spreadsheet's header columns

                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

                Returns:
                    list: a list of strings representing the header columns
                """
                return [file_loc, str(print_cols)]

    def test_google_no_return_keyword(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> list:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)

                list: a list of strings representing the header columns
                """
                return [file_loc, str(print_cols)]

    def test_keep_it_simple(self):
        @pedantic_require_docstring
        def calc() -> None:
            """Gets and prints the spreadsheet's header columns"""
            pass

        calc()

    def test_docstring_misses_argument(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(name: str) -> None:
                """Gets and prints the spreadsheet's header columns"""
                print('hi ' + name)

    def test_keep_it_simple_2_corrected(self):
        @pedantic_require_docstring
        def calc(name: str) -> None:
            """Gets and prints the spreadsheet's header columns

            Args:
                name (str): the name
            """
            print('hi ' + name)

        calc(name='maria')

    def test_undocumented_arg(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool, number: int) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)

                Returns:
                    List[str]: a list of strings representing the header columns
                """
                return [file_loc, str(print_cols), str(number)]

    def test_undocumented_arg_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool, number: int) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
                number (int): magic number

            Returns:
                List[str]: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols), str(number)]

        calc(file_loc='Hi', print_cols=False, number=42)

    def test_restructured_text_style_doctsring_cannot_be_parsed_yet(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                :param file_loc: The file location of the spreadsheet
                :type file_loc: str
                :param print_cols: A flag used to print the columns to the console
                :type print_cols: bool
                :returns: a list of strings representing the header column
                :rtype: List[str]
                """
                return [file_loc, str(print_cols)]

    def test_return_nothing_but_document_return_value(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool):
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)

                Returns:
                    list: a list of strings representing the header columns
                """
                print([file_loc, str(print_cols)])

    def test_return_nothing_but_document_return_value_2(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> None:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)

                Returns:
                    list: a list of strings representing the header columns
                """
                print([file_loc, str(print_cols)])

    def test_return_value_1_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> None:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
            """

            a = [file_loc, str(print_cols)]
        calc(file_loc='Hi', print_cols=False)

    def test_return_value_is_not_documented(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            # the error message here is actually wrong due to the behavior of the docstring-parser package
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console (default is False)

                Returns:
                """
                return [file_loc, str(print_cols)]

    def test_return_value_2_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
                List[str]: results
            """

            return [file_loc, str(print_cols)]

        calc(file_loc='Hi', print_cols=False)

    def test_return_value_is_not_documented_3(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc(file_loc: str, print_cols: bool) -> List[str]:
                """Gets and prints the spreadsheet's header columns

                Args:
                    file_loc (str): The file location of the spreadsheet
                    print_cols (bool): A flag used to print the columns to the console
                        (default is False)
                """
                return [file_loc, str(print_cols)]

    def test_wrong_format_1(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            class MyText:
                text = 'hi'

                @pedantic_require_docstring
                def __contains__(self, substring: str) -> bool:
                    """
                    Checks if contains substring.
                    Overriding __contains__ build in functions allows to use the 'in' operator blah readability

                    Example:
                    my_text = MyText('abc')
                    if 'ab' in my_text -> true
                    :param: substring: substring
                    :return: True if substring is stored, False otherwise.
                    """
                    return substring in self.text

    def test_undocumented_arg_3(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic
            def calc(a: int, b: float, c: str) -> str:
                """Returns some cool string

                Args:
                    a (int): something
                    b (float): something

                Returns:
                    str: something
                """
                return str(a) + str(b) + c

            calc(a=42, b=3.14, c='hi')

    def test_pedantic_1_corrected(self):
        @pedantic
        def calc(a: int, b: float, c: str) -> str:
            """Returns some cool string

            Args:
                a (int): something
                b (float): something
                c (str): something

            Returns:
                str: something
            """
            return str(a) + str(b) + c

        calc(a=42, b=3.14, c='hi')

    def test_documented_none_as_return_type(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def calc() -> None:
                """some cool stuff

                Returns:
                    None: the evil void
                """
                pass

    def test_exception_in_docstring_parser(self):
        @pedantic_class
        class Foo:
            def func(self, b: str) -> str:
                """
                Function with docstring syntax error below.
                Args:
                    b (str):
                    simple string
                Returns:
                    str: simple string
                """
                return b

    def test_user_class(self):
        class BPMNEnum:
            attr = 'BPMNEnum'

        class BPMNElement:
            attr = 'BPMNElement'

        @pedantic_class_require_docstring
        class MyClass:
            def make_element(self, element_type: BPMNEnum,
                             src_tgt_elements: Optional[List[BPMNElement]] = None) -> List[BPMNElement]:
                """
                Searches all element_types in XML-DOM and returns corresponding
                BPMN-Objects.
                Args:
                    element_type(BPMNEnum): abc
                    src_tgt_elements (Optional[List[BPMNElement]]): abc

                Returns:
                    List[BPMNElement]: abc
                """
                element_type.attr = '42'
                return src_tgt_elements

        m = MyClass()
        m.make_element(element_type=BPMNEnum(), src_tgt_elements=[BPMNElement()])
        with self.assertRaises(expected_exception=PedanticTypeCheckException):
            m.make_element(element_type=BPMNElement(), src_tgt_elements=[BPMNEnum()])

    def test_user_class_with_typing(self):
        class BPMNEnum:
            attr = 'BPMNEnum'

        class BPMNElement:
            attr = 'BPMNElement'

        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_class_require_docstring
            class MyClass:

                def make_element(self, element_type: BPMNEnum,
                                 src_tgt_elements: Optional[List[BPMNElement]] = None) -> List[BPMNElement]:
                    """
                    Searches all element_types in XML-DOM and returns corresponding
                    BPMN-Objects.
                    Args:
                        element_type(BPMNEnum): abc
                        src_tgt_elements (typing.Optional[List[BPMNElement]]): abc

                    Returns:
                        List[BPMNElement]: abc
                    """
                    element_type.attr = '42'
                    return src_tgt_elements

    def test_factory(self):
        @pedantic_require_docstring
        def get_instance() -> TestCase:
            """
            Returns:
                TestCase: A new TestCase
            """
            return TestCase()

        get_instance()

    def test_pedantic_args(self):
        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic(require_docstring=True)
            def no_docstrings() -> None:
                print('.')

        with self.assertRaises(expected_exception=PedanticDocstringException):
            @pedantic_require_docstring
            def no_docstrings() -> None:
                print('.')
