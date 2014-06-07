#!/usr/bin/env python
"""
================================================================================
:mod:`config` -- Casino 2 Monte Carlo program configuration
================================================================================

.. module:: config
   :synopsis: Casino 2 Monte Carlo program configuration

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import glob

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.program.config import Program
from pymontecarlo.program.casino2.converter import Converter
from pymontecarlo.program.casino2.exporter import Exporter
from pymontecarlo.program.casino2.importer import Importer
from pymontecarlo.program.casino2.worker import Worker

# Globals and constants variables.

class _CasinoProgram(Program):

    def __init__(self):
        Program.__init__(self, 'Casino 2', 'casino2', Converter, Worker,
                          Exporter, Importer, autorun=False)

    def validate(self):
        settings = get_settings()

        if 'casino2' not in settings:
            raise AssertionError("Missing 'casino2' section in settings")

        if 'exe' not in settings.casino2:
            raise AssertionError("Missing 'exe' option in 'casino2' section of settings")

        exe = settings.casino2.exe
        if os.path.splitext(exe)[1] != '.app' and not os.path.isfile(exe):
            raise AssertionError("Specified Casino 2 executable (%s) does not exist" % exe)
        if not os.access(exe, os.X_OK):
            raise AssertionError("Specified Casino 2 executable (%s) is not executable" % exe)

    def autoconfig(self, programs_path):
        if sys.platform == 'linux':
            exe_path = '/usr/bin/casino2'
            if not os.path.exists(exe_path):
                return False
        else:
            paths = glob.glob(os.path.join(programs_path, self.alias, '*casino*'))
            if len(paths) != 1:
                return False
            exe_path = paths[0]

        settings = get_settings()
        settings.add_section('casino2').exe = exe_path
        return True

program = _CasinoProgram()
