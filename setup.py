#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(name="pyMathBitPrecise",
      version="0.8",
      description="number types of variable bit size and utils for bit manipulations",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/Nic30/pyMathBitPrecise",
      author="Michal Orsak",
      author_email="michal.o.socials@gmail.com",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: System :: Hardware",
        "Topic :: System :: Emulators",
        "Topic :: Utilities"],
      license="MIT",
      packages=find_packages(),
)
