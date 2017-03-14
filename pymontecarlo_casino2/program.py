""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.program.base import Program
from pymontecarlo.options.limit import ShowersLimit

from pymontecarlo_casino2.configurator import Casino2Configurator
from pymontecarlo_casino2.expander import Casino2Expander
from pymontecarlo_casino2.exporter import Casino2Exporter
from pymontecarlo_casino2.importer import Casino2Importer
from pymontecarlo_casino2.validator import Casino2Validator
from pymontecarlo_casino2.worker import Casino2Worker

# Globals and constants variables.

class Casino2Program(Program):

    def __init__(self, executable=None):
        self.executable = executable

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
        return ShowersLimit(10000)
