""""""

# Standard library modules.

# Third party modules.
import numpy as np

# Local modules.
from pymontecarlo.fileformat.base import HDF5Handler

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramHDF5Handler(HDF5Handler):

    CLASS = Casino2Program

    ATTR_EXECUTABLE = 'executable'

    def parse(self, group):
        executable = group.attrs.get(self.ATTR_EXECUTABLE).decode('ascii')
        return Casino2Program(executable)

    def convert(self, obj, group):
        super().convert(obj, group)
        group.attrs[self.ATTR_EXECUTABLE] = np.string_(obj.executable)
