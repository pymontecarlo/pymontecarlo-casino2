#!/usr/bin/env python
"""
================================================================================
:mod:`worker` -- Casino 2 worker
================================================================================

.. module:: worker
   :synopsis: Casino 2 worker

.. inheritance-diagram:: pymontecarlo.program.casino2.runner.worker

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2012 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import sys
import logging
import os
import subprocess

# Third party modules.

# Local modules.
from pymontecarlo.settings import get_settings
from pymontecarlo.program.worker import SubprocessWorker as _Worker

# Globals and constants variables.

class Worker(_Worker):
    def __init__(self, program):
        """
        Runner to run Casino2 simulation(s).
        """
        _Worker.__init__(self, program)

        self._executable = get_settings().casino2.exe
        logging.debug('Casino2 executable: %s', self._executable)

        self._executable_dir = os.path.dirname(self._executable)
        logging.debug('Casino2 directory: %s', self._executable_dir)

    def run(self, options, outputdir, workdir, *args, **kwargs):
        if sys.platform == 'darwin':
            self.create(options, outputdir, *args, **kwargs)
            raise NotImplementedError("Simulations with Casino2 cannot be directly run in MacOS. "
                "The .sim file was created in the output directory.")

        simfilepath = self.create(options, workdir)

        # Launch
        args = [self._executable, '-batch', simfilepath.replace('/', '\\')]
        logging.debug('Launching %s', ' '.join(args))

        self._status = 'Running Casino2'

        self._create_process(args, stdout=subprocess.PIPE,
                             cwd=self._executable_dir)
        self._join_process()

        logging.debug('Casino2 ended')

        return self._extract_results(options, simfilepath)

    def _extract_results(self, options, simfilepath):
        casfilepath = os.path.splitext(simfilepath)[0] + '.cas'
        if not os.path.exists(casfilepath):
            raise IOError('Cannot find results for %s' % simfilepath)

        # Import results to pyMonteCarlo
        logging.debug('Importing results from Casino2')
        with open(casfilepath, 'rb') as fp:
            return self._importer.import_cas(options, fp)
