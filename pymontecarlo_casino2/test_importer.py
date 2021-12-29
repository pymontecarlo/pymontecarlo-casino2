#!/usr/bin/env python
""" """

# Standard library modules.
import os

# Third party modules.
import pytest

# Local modules.
from pymontecarlo_casino2.importer import Casino2Importer

from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
from pymontecarlo.simulation import Simulation

# Globals and constants variables.


@pytest.fixture
def importer():
    return Casino2Importer()


@pytest.mark.asyncio
async def test_import_(event_loop, importer, options, testdatadir):
    dirpath = os.path.join(testdatadir, "sim1")
    results = await importer.import_(options, dirpath)
    simulation = Simulation(options, results)

    assert len(simulation.results) == 1

    result = simulation.find_result(EmittedPhotonIntensityResult)[0]
    assert len(result) == 43

    q = result[("Au", "La")]
    assert q.n == pytest.approx(2.73255e-7, abs=1e-13)

    q = result[("Si", "Ka1")]
    assert q.n == pytest.approx(1.6331941e-6, abs=1e-13)
