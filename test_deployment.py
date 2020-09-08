import unittest
from pedantic import pedantic_class


class AfterDeployment(unittest.TestCase):
    """Checks if the wheel was built correctly. That will fail if setup.py misses some files."""
    def test_deployment_successful(self):
        @pedantic_class
        class MyClass:
            def __init__(self):
                print('test')

        with self.assertRaises(expected_exception=AssertionError):
            MyClass()


if __name__ == '__main__':
    unittest.main()
