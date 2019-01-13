""""""

# Standard library modules.
import math

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.options import Options
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import SubstrateSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

@pytest.fixture
def options():
    program = Casino2Program(number_trajectories=50)
    beam = GaussianBeam(15e3, 10e-9)
    sample = SubstrateSample(Material.pure(29))
    detector = PhotonDetector('xray', math.radians(40.0))
    analyses = [PhotonIntensityAnalysis(detector)]
    tags = ['basic', 'test']
    return Options(program, beam, sample, analyses, tags)
