""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.program.base import ProgramHDF5Handler

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramHDF5Handler(ProgramHDF5Handler):

    def parse(self, group):
        return Casino2Program()

    def convert(self, program, group):
        super().convert(program, group)

    @property
    def CLASS(self):
        return Casino2Program
