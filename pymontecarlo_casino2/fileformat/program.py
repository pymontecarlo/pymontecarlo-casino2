""""""

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramHDF5Handler(HDF5Handler):

    ATTR_EXECUTABLE = 'executable'

    def _parse_executable(self, group):
        return group.attrs.get(self.ATTR_EXECUTABLE).decode('ascii')

    def can_parse(self, group):
        return super().can_parse(group) and \
            self.ATTR_EXECUTABLE in group.attrs

    def parse(self, group):
        executable = self._parse_executable(group)
        return Casino2Program(executable)

    def _convert_executable(self, executable, group):
        group.attrs[self.ATTR_EXECUTABLE] = np.string_(executable)

    def convert(self, program, group):
        super().convert(program, group)
        self._convert_executable(program.executable, group)

    @property
    def CLASS(self):
        return Casino2Program
