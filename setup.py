# mini framework setup.py

import io
from os import path

from setuptools import setup, find_packages, find_namespace_packages

this_directory = path.abspath(path.dirname(__file__))


def parse_requirements(filename):
    """加载requirements.txt的依赖项"""
    with open(filename, "r") as file:
        lines = (line.strip() for line in file)
        return [line for line in lines if line and not line.startswith("#")]


requirements = parse_requirements("requirements.txt")

with io.open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mini_framework",
    use_scm_version=True,
    description="Mini Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["any"],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Framework",
        "Topic :: Framework :: Backends",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    keywords="Mini Framework",
    packages=find_packages(
        where=".",
        exclude=["tests", "tests.*", "web_test"],
        include=[
            "mini_framework*",
        ],
    ),
    package_dir={"": "."},
    package_data={
        "mini_framework": [
            "web/resources/*",
            "web/resources/statics/*",
            "web/resources/statics/swagger-ui/*",
            "web/resources/statics/redoc-ui/*",
            "web/templates/*",
            "databases/version/templates/*"
        ]
    },
    include_package_data=True,
)
