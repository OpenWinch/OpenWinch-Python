#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
from os import path
from openwinch import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

with open("CHANGELOG.md", "r") as clog:
    changelog = clog.read()

setup(
    version=__version__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages()
)
