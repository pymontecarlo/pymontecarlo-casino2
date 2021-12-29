#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, "README.md"), "r") as fp:
    LONG_DESCRIPTION = fp.read()

PACKAGES = find_packages()
PACKAGE_DATA = {"pymontecarlo_casino2": ["templates/*.sim"]}

casinodir = os.path.join(BASEDIR, "pymontecarlo_casino2", "casino2")
for root, _dirnames, filenames in os.walk(casinodir):
    dirpath = os.path.join("casino2", root[len(casinodir) + 1 :])
    for filename in filenames:
        relpath = os.path.join(dirpath, filename)
        PACKAGE_DATA["pymontecarlo_casino2"].append(relpath)

with open(os.path.join(BASEDIR, "requirements.txt"), "r") as fp:
    INSTALL_REQUIRES = fp.read().splitlines()

EXTRAS_REQUIRE = {}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {}

setup(
    name="pyMonteCarlo-Casino2",
    version=versioneer.get_version(),
    url="https://github.com/pymontecarlo",
    description="Python interface for Monte Carlo simulation program Casino 2",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Philippe T. Pinard and Hendrix Demers",
    author_email="philippe.pinard@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    cmdclass=CMDCLASS,
    entry_points=ENTRY_POINTS,
)
