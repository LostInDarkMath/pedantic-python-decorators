@(
echo [run]
echo omit = *PythonHelpers/unit_tests*
) > .coveragerc

pip install coverage
coverage run -m unittest PythonHelpers/unit_tests/tests_main.py
rem coverage report -m
coverage html 
cd htmlcov
index.html