## -*- encoding: utf-8 -*-
import os
import sys
import setuptools
from codecs import open # To open the README file with proper encoding
from setuptools.command.test import test as TestCommand # for tests


with open("README.md", "r") as fh:
    long_description = fh.read()

# For the tests
class SageTest(TestCommand):
    def run_tests(self):
        errno = os.system("sage -t --force-lib phitigra")
        if errno != 0:
            sys.exit(1)

setuptools.setup(
    name="phitigra",
    version="0.0.1",
    author="Jean-Florent Raymond",
    author_email="j-florent.raymond@uca.fr",
    description="A graph editor for jupyter/sagemath",
    url="https://gitlab.limos.fr/jfraymon/phitigra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    cmdclass = {'test': SageTest}, # adding a special setup command for tests
)
