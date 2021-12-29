""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.program.expander import ExpanderBase, expand_to_single

# Globals and constants variables.


class Casino2Expander(ExpanderBase):
    def expand_analyses(self, analyses):
        return expand_to_single(analyses)
