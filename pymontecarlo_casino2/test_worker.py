#!/usr/bin/env python
""" """

# Standard library modules.
import asyncio

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.simulation import Simulation
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import (
    SubstrateSample,
    HorizontalLayerSample,
    VerticalLayerSample,
)
from pymontecarlo.util.token import Token, TokenState
from pymontecarlo_casino2.worker import Casino2Worker
from pymontecarlo_casino2.program import Casino2Program
from pymontecarlo.exceptions import ProgramNotFound

# Globals and constants variables.


def _has_casino2():
    try:
        program = Casino2Program()
        program.executable  # Raise RuntimeError
    except ProgramNotFound:
        return False

    return True


if not _has_casino2():
    pytest.skip("Casino2 cannot be executed", allow_module_level=True)


def _create_samples():
    yield SubstrateSample(Material.pure(39))

    for number_layers in range(1, 10 + 1):
        sample = HorizontalLayerSample(Material.pure(39))
        for i in range(number_layers):
            sample.add_layer(Material.pure(40 + i), 20e-9)
        yield sample

    for number_layers in range(0, 9 + 1):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        for i in range(number_layers):
            sample.add_layer(Material.pure(40 + i), 20e-9)
        yield sample


@pytest.mark.asyncio
@pytest.mark.parametrize("sample", _create_samples())
async def test_casino2_worker(event_loop, options, sample, tmpdir):
    options.sample = sample

    worker = Casino2Worker()
    token = Token("test")
    simulation = Simulation(options)
    outputdir = str(tmpdir)

    await worker.run(token, simulation, outputdir)

    assert token.state == TokenState.DONE
    assert token.progress == 1.0
    assert token.status == "Done"
    assert len(simulation.results) == 1


@pytest.mark.asyncio
async def test_casino2_cancel(event_loop, options, tmpdir):
    # Increase number of electrons
    options.program.number_trajectories = 10000

    worker = Casino2Worker()
    token = Token("test")
    simulation = Simulation(options)
    outputdir = str(tmpdir)

    task = asyncio.create_task(worker.run(token, simulation, outputdir))

    await asyncio.sleep(0.5)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        assert True, "Task was cancelled properly"
    else:
        assert False

    assert token.state == TokenState.CANCELLED
    assert token.progress == 1.0
    assert token.status == "Cancelled"
    assert len(simulation.results) == 0
