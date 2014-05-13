#!/usr/bin/env python
"""
================================================================================
:mod:`command` -- Special command for distutils
================================================================================

.. module:: command
   :synopsis: Special command for distutils

.. inheritance-diagram:: pymontecarlo.program.casino2.util.dist.command

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from distutils.core import Command, DistutilsOptionError

# Third party modules.

# Local modules.
from pymontecarlo.program.casino2.util.dist.debbuilder import Casino2DebBuilder

# Globals and constants variables.

class bdist_deb_program(Command):

    description = 'Build deb for Casino2 program'

    user_options = [('zip-file=', None,
                     "zip file containing the Casino 2 program and files "
                     ""),
                    ('dist-dir=', 'd',
                     "directory to put final built distributions in "
                     "[default: dist]"), ]

    def initialize_options(self):
        self.dist_dir = None
        self.zip_file = None

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = "dist"
        if self.zip_file is None:
            raise DistutilsOptionError('you must specify zip-file')

    def run(self):
        builder = Casino2DebBuilder(self.zip_file)
        builder.build(self.dist_dir, arch='i386')
        builder.build(self.dist_dir, arch='amd64')
