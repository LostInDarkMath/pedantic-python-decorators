from setuptools import find_packages, setup
from os import path


def get_content_from_readme(file_name: str = 'README.md') -> str:
    this_directory = path.abspath(path.dirname(__file__))

    with open(path.join(this_directory, file_name), encoding='utf-8') as file:
        return file.read()


url = "https://github.com/LostInDarkMath/pedantic-python-decorators"
author = "Willi Sontopski"

setup(
    name="pedantic",
    version="1.8.4",
    python_requires='>=3.6.1',
    packages=find_packages(),
    install_requires=['docstring_parser'],
    author=author,
    author_email="willi_sontopski@arcor.de",
    license="Apache-2.0 License",
    maintainer=author,
    description="Some useful Python decorators for cleaner software development.",
    long_description=get_content_from_readme(),
    long_description_content_type='text/markdown',
    keywords="decorators tools helpers type-checking pedantic type annotations",
    url=url,
    project_urls={
        "Bug Tracker": f'{url}/issues',
        "Documentation": 'https://lostindarkmath.github.io/pedantic-python-decorators/pedantic/',
        "Source Code": url,
    },
    include_package_data=False,
    zip_safe=True,
)
