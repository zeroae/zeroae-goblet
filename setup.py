#!/usr/bin/env python

"""The setup script."""

import os

from setuptools import setup, find_namespace_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

# The requirements section should be kept in sync with the environment.yml file
requirements = [
    # fmt: off
    "chalice>=1.13",
    "click>=7.0",
    "click-plugins",
    "entrypoints",
    "environs",
    "jinja2",
    "octokitpy==0.13.0",
    "pypubsub==4.0.3",
    "python-dateutil",
    # fmt: on
]

setup_requirements = [
    # fmt: off
    "pytest-runner",
    "setuptools_scm",
    "wheel",
    # fmt: on
]

test_requirements = [
    # fmt: off
    "pytest>=3",
    "pytest-chalice",
    "pytest-cov",
    # fmt: on
]

conda_rosetta_stone = {
    # fmt: off
    "pypa-requirement": "conda-dependency"
    # fmt: on
}

setup_kwargs = dict(
    author="Patrick Sodré",
    author_email="psodre@gmail.com",
    use_scm_version={"write_to": "zeroae/goblet/_version.py"},
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A Chalice blueprint for creating GitHub Apps",
    # fmt: off
    entry_points={
        "zeroae.cli": [
            "goblet=zeroae.goblet.cli:goblet",
        ],
    },
    # fmt: on
    install_requires=requirements,
    license="Apache",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="goblet zeroae",
    name="zeroae-goblet",
    packages=find_namespace_packages(include=["zeroae.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={
        # fmt: off
        "test": test_requirements
        # fmt: on
    },
    url="https://github.com/zeroae/zeroae-goblet",
    zip_safe=False,
)

if "CONDA_BUILD_STATE" in os.environ:
    try:
        from setuptools_scm import get_version

        setup_kwargs["version"] = get_version(**setup_kwargs["use_scm_version"])
        del setup_kwargs["use_scm_version"]
    except ModuleNotFoundError:
        print(
            "Error: zeroae-goblet requires that setuptools_scm be installed with conda-build!"  # noqa: E501
        )
        raise
    setup_kwargs["conda_rosetta_stone"] = conda_rosetta_stone

setup(**setup_kwargs)
