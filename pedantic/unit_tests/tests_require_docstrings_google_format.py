import unittest
from typing import List

# local file imports
from pedantic.method_decorators import pedantic_require_docstring


class TestRequireDocstringGoogleFormat(unittest.TestCase):

    def test_no_doc_string(self):
        """Problem here: No docstring"""
        @pedantic_require_docstring
        def calc(n: int, m: int, i: int) -> int:
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(n=42, m=40, i=38)

    def test_one_line_doc_string(self):
        """Problem here: The docstring misses arguments and return value"""
        @pedantic_require_docstring
        def calc(n: int, m: int, i: int) -> int:
            """Returns the sum of the three args."""
            return n + m + i

        with self.assertRaises(expected_exception=AssertionError):
            calc(n=42, m=40, i=38)

    def test_one_line_doc_string_corrected(self):
        @pedantic_require_docstring
        def calc(n: int, m: int, i: int) -> int:
            """Returns the sum of the three args.

            Args:
                n (int): bla
                m (int): blub
                i (int): foo

            Returns:
                int: bar
            """
            return n + m + i

        calc(n=42, m=40, i=38)

    def test_google_docstring_1(self):
        """Problem here: List[str] != list"""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

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
        def calc(file_loc: str, print_cols: bool) -> list:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
                list: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols)]

        calc(file_loc='Hi', print_cols=False)

    def test_google_docstring_4(self):
        """Problem here: Argument 'ammount' is NOT a parameter of the function."""
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> list:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
                ammount (int): THIS ARGUMENT IS NOT TAKEN BY THE FUNCTION

            Returns:
                list: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols)]

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

    def test_google_docstring_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool, ammount: int) -> list:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
                ammount (int): now it is

            Returns:
                list: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols), ammount]

        calc(file_loc='Hi', print_cols=False, ammount=42)

    def test_google_no_args_keyword(self):
        """Problem here: Docstring misses the keyword 'Args:' before the arguments listed."""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

    def test_google_no_return_keyword(self):
        """Problem here: Docstring misses the keyword 'Returns:' before the return value."""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

    def test_keep_it_simple(self):
        @pedantic_require_docstring
        def calc() -> None:
            """Gets and prints the spreadsheet's header columns"""
            a = 'hi'

        calc()

    def test_keep_it_simple_2(self):
        """Problem here: docstring misses argument"""
        @pedantic_require_docstring
        def calc(name: str) -> None:
            """Gets and prints the spreadsheet's header columns"""
            a = 'hi ' + name

        with self.assertRaises(expected_exception=AssertionError):
            calc(name='maria')

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
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool, number: int) -> list:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
                list: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols), str(number)]

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False, number=42)

    def test_undocumented_arg_corrected(self):
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool, number: int) -> list:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
                number (int): magic number

            Returns:
                list: a list of strings representing the header columns
            """

            return [file_loc, str(print_cols), str(number)]

        calc(file_loc='Hi', print_cols=False, number=42)

    def test_restructured_text_1(self):
        """Problem here: reStructured Text docstring format cannot be parsed"""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

    def test_return_value_1(self):
        """Problem here: There is a return value documented, but nothing is returned."""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

    def test_return_value_11(self):
        """Problem here: There is a return value documented, but nothing is returned."""
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

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

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
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)

            Returns:
            """

            return [file_loc, str(print_cols)]

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)

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
        @pedantic_require_docstring
        def calc(file_loc: str, print_cols: bool) -> List[str]:
            """Gets and prints the spreadsheet's header columns

            Args:
                file_loc (str): The file location of the spreadsheet
                print_cols (bool): A flag used to print the columns to the console
                    (default is False)
            """

            return [file_loc, str(print_cols)]

        with self.assertRaises(expected_exception=AssertionError):
            calc(file_loc='Hi', print_cols=False)
