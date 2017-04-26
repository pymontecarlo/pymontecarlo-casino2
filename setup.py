#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, 'README.rst'), 'r') as fp:
    LONG_DESCRIPTION = fp.read()

PACKAGES = find_packages()
PACKAGE_DATA = {'pymontecarlo_casino2': ['templates/*.sim']}

casinodir = os.path.join(BASEDIR, 'pymontecarlo_casino2', 'casino2')
for root, _dirnames, filenames in os.walk(casinodir):
    dirpath = os.path.join('casino2', root[len(casinodir) + 1:])
    for filename in filenames:
        relpath = os.path.join(dirpath, filename)
        PACKAGE_DATA['pymontecarlo_casino2'].append(relpath)

INSTALL_REQUIRES = ['pymontecarlo', 'pycasinotools']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage']}

CMDCLASS = versioneer.get_cmdclass()

ENTRY_POINTS = {'pymontecarlo.program':
                ['casino2 = pymontecarlo_casino2.program:Casino2Program'],

                'pymontecarlo.formats.hdf5':
                ['Casino2ProgramHDF5Handler = pymontecarlo_casino2.formats.hdf5.program:Casino2ProgramHDF5Handler']}

setup(name="pyMonteCarlo-Casino2",
      version=versioneer.get_version(),
      url='https://github.com/pymontecarlo',
      description="Python interface for Monte Carlo simulation program Casino 2",
      author="Hendrix Demers and Philippe T. Pinard",
      author_email="hendrix.demers@mail.mcgill.ca and philippe.pinard@gmail.com",
      license="GPL v3",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=PACKAGES,
      package_data=PACKAGE_DATA,

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,

      test_suite='nose.collector',
)

