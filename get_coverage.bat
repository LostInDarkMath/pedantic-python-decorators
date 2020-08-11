@(
echo [run]
echo omit = *pedantic/unit_tests*
) > .coveragerc

pip install coverage
coverage run -m unittest pedantic/unit_tests/tests_main.py
rem coverage report -m
coverage html 
cd htmlcov
index.html