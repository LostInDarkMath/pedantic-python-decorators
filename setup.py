from setuptools import find_packages, setup
from os import path

url = "https://github.com/LostInDarkMath/pedantic-python-decorators"
author = "Willi Sontopski"

# read the contents of the README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # important things
    name="pedantic",
    version="1.1.0",
    packages=find_packages(),
    # scripts = ["say_hello.py"]
    install_requires=['docstring_parser'],
    # package_data={
    #     # If any package contains *.txt or *.rst files, include them:
    #     "": ["*.txt", "*.rst"],
    #     # And include any *.msg files found in the "hello" package, too:
    #     "hello": ["*.msg"],
    # },

    # metadata to display on PyPI
    author=author,
    # author_email="me@example.com",
    license="Apache-2.0 License",
    maintainer=author,
    description="Some useful Python decorators for cleaner software development.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="decorators tools helpers type-checking pedantic type annotations",
    url=url,
    project_urls={
        "Bug Tracker": f'{url}/issues',
        "Documentation": url,
        "Source Code": url,
    },

    # less important things
    include_package_data=False,
    zip_safe=True,
)
