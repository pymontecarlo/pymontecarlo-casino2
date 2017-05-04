""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.program.expander import Expander, expand_to_single

# Globals and constants variables.

class Casino2Expander(Expander):

    def expand_detectors(self, detectors):
        return expand_to_single(detectors)

    def expand_limits(self, limits):
        return expand_to_single(limits)

    def expand_models(self, models):
        return expand_to_single(models)

    def expand_analyses(self, analyses):
        return expand_to_single(analyses)
