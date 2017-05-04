""""""

# Standard library modules.
import os
import sys

# Third party modules.

# Local modules.
from pymontecarlo.program.base import Program
from pymontecarlo.util.sysutil import is_64bits
from pymontecarlo.options.limit import ShowersLimit

from pymontecarlo_casino2.configurator import Casino2Configurator
from pymontecarlo_casino2.expander import Casino2Expander
from pymontecarlo_casino2.exporter import Casino2Exporter
from pymontecarlo_casino2.importer import Casino2Importer
from pymontecarlo_casino2.validator import Casino2Validator
from pymontecarlo_casino2.worker import Casino2Worker

# Globals and constants variables.

class Casino2Program(Program):

    @classmethod
    def getidentifier(self):
        return 'casino2'

    @classmethod
    def create_configurator(cls):
        return Casino2Configurator()

    def create_expander(self):
        return Casino2Expander()

    def create_validator(self):
        return Casino2Validator()

    def create_exporter(self):
        return Casino2Exporter()

    def create_worker(self):
        return Casino2Worker()

    def create_importer(self):
        return Casino2Importer()

    def create_default_limits(self, options):
        return [ShowersLimit(10000)]

    @property
    def executable(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        casino2dir = os.path.join(basedir, 'casino2')

        if not os.path.exists(casino2dir):
            raise RuntimeError('Casino 2 program cannot be found')

        if sys.platform == 'darwin': # Wine only works with 32-bit
            filename = 'wincasino2.exe'
        else:
            filename = 'wincasino2_64.exe' if is_64bits() else 'wincasino2.exe'
        filepath = os.path.join(casino2dir, filename)

        if not os.path.exists(filepath):
            raise RuntimeError('Cannot find {}. Installation might be corrupted.'
                               .format(filepath))

        return filepath
