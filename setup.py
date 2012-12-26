#!/usr/bin/env python

from distutils.core import setup

setup(
    name='wbdata',
    version='0.0.1',
    author="Oliver Sherouse",
    author_email="oliver.sherouse@gmail.com",
    packages=["wbdata"],
    url="https://github.com/oliversherouse/wbdata",
    licence="GPL2",
    description="A library to access World Bank data",
    install_requires=[
        "decorator >= 3.4.0"
    ],
    long_description=open('README.rst').read()
)
