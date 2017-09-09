""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.options.program.expander import Expander, expand_to_single

# Globals and constants variables.

class Casino2Expander(Expander):

    def expand_analyses(self, analyses):
        return expand_to_single(analyses)
