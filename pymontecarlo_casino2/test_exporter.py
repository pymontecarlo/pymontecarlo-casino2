#!/usr/bin/env python
""" """

# Standard library modules.
import operator

# Third party modules.
import pytest

from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.SimulationOptions import (
    DIRECTION_COSINES_SOUM,
    CROSS_SECTION_MOTT_EQUATION,
    IONIZATION_CROSS_SECTION_GRYZINSKI,
    IONIZATION_POTENTIAL_HOVINGTON,
    RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER,
    ENERGY_LOSS_JOY_LUO,
)

# Local modules.
from pymontecarlo_casino2.exporter import Casino2Exporter

from pymontecarlo.options.base import apply_lazy
from pymontecarlo.options.beam import PencilBeam
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import VerticalLayerSample, HorizontalLayerSample
from pymontecarlo.options.model import (
    ElasticCrossSectionModel,
    IonizationCrossSectionModel,
    IonizationPotentialModel,
    RandomNumberGeneratorModel,
    DirectionCosineModel,
)
from pymontecarlo.util.error import ErrorAccumulator

# Globals and constants variables.


@pytest.fixture
def exporter():
    return Casino2Exporter()


def _test_material_region(material, region):
    elements = list(map(operator.attrgetter("Z"), region.getElements()))

    assert region.Name == material.name
    assert len(elements) == len(material.composition)

    for z in material.composition:
        assert z in elements

    assert region.Rho == pytest.approx(material.density_kg_per_m3 / 1000.0, abs=1e-4)


@pytest.mark.asyncio
async def test_export_beam_pencil(event_loop, exporter, options, tmp_path):
    options.beam = PencilBeam(10e3)

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    simops = simdata.getSimulationOptions()

    assert simops.getIncidentEnergy_keV(0) == pytest.approx(
        options.beam.energy_keV, abs=1e-4
    )
    assert simops.Beam_Diameter == pytest.approx(0.0, abs=1e-4)
    assert simops._positionStart_nm == pytest.approx(0.0, abs=1e-4)


@pytest.mark.asyncio
async def test_export_substrate(event_loop, exporter, options, tmp_path):
    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    simops = simdata.getSimulationOptions()
    regionops = simdata.getRegionOptions()

    assert simops.getIncidentEnergy_keV(0) == pytest.approx(
        options.beam.energy_keV, abs=1e-4
    )
    assert simops.Beam_Diameter == pytest.approx(
        2.7947137 * options.beam.diameter_m * 1e9 / 2.0, abs=1e-4
    )
    assert simops._positionStart_nm == pytest.approx(0.0, abs=1e-4)

    assert regionops.getNumberRegions() == 1

    region = regionops.getRegion(0)
    _test_material_region(options.sample.material, region)

    assert simops.getNumberElectrons() == options.program.number_trajectories

    assert simops.FEmissionRX


@pytest.mark.asyncio
async def test_export_substrate_nodensity(event_loop, exporter, options, tmp_path):
    material = Material("blah", {29: 1.0})
    options.sample.material = material

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    regionops = simdata.getRegionOptions()

    assert regionops.getNumberRegions() == 1

    region = regionops.getRegion(0)

    expected = apply_lazy(material.density_kg_per_m3, material, options)
    assert region.Rho == pytest.approx(expected / 1000.0, abs=1e-4)


@pytest.mark.asyncio
async def test_export_grainboundaries(event_loop, exporter, options, tmp_path):
    # Options
    mat1 = Material("Mat1", {79: 0.5, 47: 0.5}, 2.0)
    mat2 = Material("Mat2", {29: 0.5, 30: 0.5}, 3.0)
    mat3 = Material("Mat3", {13: 0.5, 14: 0.5}, 4.0)

    sample = VerticalLayerSample(mat1, mat2)
    sample.add_layer(mat3, 25e-9)
    options.sample = sample

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    regionops = simdata.getRegionOptions()

    assert regionops.getNumberRegions() == 3

    region = regionops.getRegion(0)
    _test_material_region(mat1, region)

    region = regionops.getRegion(1)
    _test_material_region(mat3, region)

    region = regionops.getRegion(2)
    _test_material_region(mat2, region)


@pytest.mark.asyncio
async def test_export_multilayers(event_loop, exporter, options, tmp_path):
    # Options
    mat1 = Material("Mat1", {79: 0.5, 47: 0.5}, 2.0)
    mat2 = Material("Mat2", {29: 0.5, 30: 0.5}, 3.0)
    mat3 = Material("Mat3", {13: 0.5, 14: 0.5}, 4.0)

    sample = HorizontalLayerSample(mat1)
    sample.add_layer(mat2, 25e-9)
    sample.add_layer(mat3, 55e-9)
    options.sample = sample

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    regionops = simdata.getRegionOptions()

    assert regionops.getNumberRegions() == 3

    region = regionops.getRegion(0)
    _test_material_region(mat2, region)

    region = regionops.getRegion(1)
    _test_material_region(mat3, region)

    region = regionops.getRegion(2)
    _test_material_region(mat1, region)


@pytest.mark.asyncio
async def test_export_multilayers2(event_loop, exporter, options, tmp_path):
    # Options
    mat1 = Material("Mat1", {79: 0.5, 47: 0.5}, 2.0)
    mat2 = Material("Mat2", {29: 0.5, 30: 0.5}, 3.0)
    mat3 = Material("Mat3", {13: 0.5, 14: 0.5}, 4.0)

    sample = HorizontalLayerSample()
    sample.add_layer(mat1, 15e-9)
    sample.add_layer(mat2, 25e-9)
    sample.add_layer(mat3, 55e-9)
    options.sample = sample

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    regionops = simdata.getRegionOptions()

    assert regionops.getNumberRegions() == 3

    region = regionops.getRegion(0)
    _test_material_region(mat1, region)

    region = regionops.getRegion(1)
    _test_material_region(mat2, region)

    region = regionops.getRegion(2)
    _test_material_region(mat3, region)


@pytest.mark.asyncio
async def test_export_models(event_loop, exporter, options, tmp_path):
    # Options
    options.program.elastic_cross_section_model = (
        ElasticCrossSectionModel.MOTT_DROUIN1993
    )
    options.program.ionization_cross_section_model = (
        IonizationCrossSectionModel.GRYZINSKY
    )
    options.program.ionization_potential_model = IonizationPotentialModel.HOVINGTON
    options.program.random_number_generator_model = RandomNumberGeneratorModel.MERSENNE
    options.program.direction_cosine_model = DirectionCosineModel.SOUM1979

    # Export
    await exporter.export(options, tmp_path)

    # Test
    filepaths = list(tmp_path.glob("*.sim"))
    assert len(filepaths) == 1

    casfile = File()
    casfile.readFromFilepath(filepaths[0])
    simdata = casfile.getOptionSimulationData()
    simops = simdata.getSimulationOptions()

    assert simops.getTotalElectronElasticCrossSection() == CROSS_SECTION_MOTT_EQUATION
    assert simops.getPartialElectronElasticCrossSection() == CROSS_SECTION_MOTT_EQUATION
    assert (
        simops.getIonizationCrossSectionType() == IONIZATION_CROSS_SECTION_GRYZINSKI - 1
    )
    assert simops.getIonizationPotentialType() == IONIZATION_POTENTIAL_HOVINGTON
    assert simops.getDirectionCosines() == DIRECTION_COSINES_SOUM
    assert simops.getEnergyLossType() == ENERGY_LOSS_JOY_LUO
    assert (
        simops.getRandomNumberGeneratorType()
        == RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER
    )


@pytest.mark.asyncio
async def test_export_program_number_trajectories_too_low(
    event_loop, exporter, options
):
    options.program.number_trajectories = 0

    erracc = ErrorAccumulator()
    await exporter._export(options, None, erracc, dry_run=True)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0


@pytest.mark.asyncio
async def test_export_program_number_trajectories_too_high(
    event_loop, exporter, options
):
    options.program.number_trajectories = 1e10

    erracc = ErrorAccumulator()
    await exporter._export(options, None, erracc, dry_run=True)

    assert len(erracc.exceptions) == 1
    assert len(erracc.warnings) == 0
