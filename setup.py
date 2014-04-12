#!/usr/bin/env python

import re
from distutils.core import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('wbdata/__init__.py').read(),
    re.M
    ).group(1)

setup(
    name='wbdata',
    version=version,
    author="Oliver Sherouse",
    author_email="oliver.sherouse@gmail.com",
    packages=["wbdata"],
    url="https://github.com/oliversherouse/wbdata",
    description="A library to access World Bank data",
    requires=["decorator"],
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
