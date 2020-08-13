rem @(
rem echo [run]
rem echo omit = *pedantic/unit_tests*
rem ) > .coveragerc

pip install coverage
coverage run -m unittest pedantic/unit_tests/tests_main.py
rem coverage report -m
coverage html 
cd htmlcov
index.html