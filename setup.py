#!/usr/bin/env python

from distutils.core import setup

setup(
    name='wbdata',
    version='0.1.0',
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
