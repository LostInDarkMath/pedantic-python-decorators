from setuptools import find_packages
from setuptools import setup

url = "https://github.com/LostInDarkMath/PythonHelpers"

setup(
    # important things
    name="pedantic",
    version="1.0.0",
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
    author="Willi Sontopski",
    # author_email="me@example.com",
    license="Apache-2.0 License",
    maintainer="Will Sontopski",
    description="Some useful Python decorators for cleaner software development.",
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
