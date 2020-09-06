import unittest
from typing import List

# local file imports
from pedantic.method_decorators import pedantic_require_docstring, pedantic


class TestRequireDocstringGoogleFormat(unittest.TestCase):

    def test_no_doc_string(self):
        """Problem here: No docstring"""
        with self.assertRaises(expected_exception=AssertionError):
            @pedantic_require_docstring
            def calc(n: int, m: int, i: int) -> int:
                return n + m + i

    def test_one_line_doc_string(self):
        """Problem here: The docstring misses arguments and return value"""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_google_docstring_1(self):
        """Problem here: List[str] != list"""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_google_docstring_4(self):
        """Problem here: Argument 'amount' is NOT a parameter of the function."""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_google_no_args_keyword(self):
        """Problem here: Docstring misses the keyword 'Args:' before the arguments listed."""
        with self.assertRaises(expected_exception=AssertionError):
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
        """Problem here: Docstring misses the keyword 'Returns:' before the return value."""
        with self.assertRaises(expected_exception=AssertionError):
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
            a = 'hi'

        calc()

    def test_keep_it_simple_2(self):
        """Problem here: docstring misses argument"""
        with self.assertRaises(expected_exception=AssertionError):
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
            a = 'hi ' + name

        calc(name='maria')

    def test_undocumented_arg(self):
        """Problem here: docstring misses argument"""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_restructured_text_1(self):
        """Problem here: reStructured Text docstring format cannot be parsed"""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_return_value_1(self):
        """Problem here: There is a return value documented, but nothing is returned."""
        with self.assertRaises(expected_exception=AssertionError):
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
                a = [file_loc, str(print_cols)]

    def test_return_value_11(self):
        """Problem here: There is a return value documented, but nothing is returned."""
        with self.assertRaises(expected_exception=AssertionError):
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
                a = [file_loc, str(print_cols)]

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

    def test_return_value_2(self):
        """Problem here: the return value is not documented"""
        with self.assertRaises(expected_exception=AssertionError):
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

    def test_return_value_3(self):
        """Problem here: the return value is not documented"""
        with self.assertRaises(expected_exception=AssertionError):
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
        """Problem here: Currently, only Google docstrings are supported"""

        with self.assertRaises(expected_exception=AssertionError):
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

    def test_pedantic_1(self):
        with self.assertRaises(expected_exception=AssertionError):
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


if __name__ == '__main__':
    t = TestRequireDocstringGoogleFormat()
    t.test_no_doc_string()
