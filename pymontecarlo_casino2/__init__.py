from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions

from pymontecarlo_casino2.program import *

try:
    from pymontecarlo_casino2.program_gui import *
except ImportError:
    pass
