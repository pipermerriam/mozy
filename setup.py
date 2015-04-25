#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import mozy
version = mozy.__version__

setup(
    name='Mozy',
    version=version,
    author='',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/mozy',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
)
