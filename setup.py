#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pip.download import PipSession
from pip.req import parse_requirements


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import mozy
version = mozy.__version__

session = PipSession()

requirements = [
    str(req.req) for req in parse_requirements('requirements.txt', session=session)
]

setup(
    name='Mozy',
    version=version,
    author='',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/mozy',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    license="MIT",
)
