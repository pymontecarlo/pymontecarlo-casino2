#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import tempfile
import shutil
import os
import glob
import operator

# Third party modules.
from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.SimulationOptions import \
    (DIRECTION_COSINES_SOUM, CROSS_SECTION_MOTT_EQUATION,
     IONIZATION_CROSS_SECTION_GRYZINSKI, IONIZATION_POTENTIAL_HOVINGTON,
     RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER, ENERGY_LOSS_JOY_LUO)

# Local modules.
from pymontecarlo_casino2.exporter import Casino2Exporter

from pymontecarlo.testcase import TestCase
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import VerticalLayerSample, HorizontalLayerSample
from pymontecarlo.options.model import \
    (ElasticCrossSectionModel, IonizationCrossSectionModel,
     IonizationPotentialModel, RandomNumberGeneratorModel,
     DirectionCosineModel)

# Globals and constants variables.

class TestCasino2Exporter(TestCase):

    def setUp(self):
        super().setUp()

        self.e = Casino2Exporter()

        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testexport(self):
        # Options
        options = self.create_basic_options()

        # Export
        self.e.export(options, self.tmpdir)

        # Test
        filepaths = glob.glob(os.path.join(self.tmpdir, '*.sim'))
        self.assertEqual(1, len(filepaths))

        casfile = File()
        casfile.readFromFilepath(filepaths[0])
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        regionops = simdata.getRegionOptions()

        self.assertAlmostEqual(options.beam.energy_keV, simops.getIncidentEnergy_keV(0), 4)
        self.assertAlmostEqual(2.7947137 * options.beam.diameter_m * 1e9 / 2.0, simops.Beam_Diameter, 4) # FWHM
        self.assertAlmostEqual(0.0, simops._positionStart_nm, 4)

        self.assertEqual(1, regionops.getNumberRegions())
        region = regionops.getRegion(0)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(options.sample.material.density_g_per_cm3, region.Rho, 4)
        self.assertEqual('Copper', region.Name)
        self.assertEqual(1, len(elements))
        self.assertTrue(29 in elements)

        self.assertEqual(100, simops.getNumberElectrons())

        self.assertTrue(simops.FEmissionRX)

    def testexport_grainboundaries(self):
        # Options
        options = self.create_basic_options()

        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, 2.0)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, 3.0)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, 4.0)

        sample = VerticalLayerSample(mat1, mat2)
        sample.add_layer(mat3, 25e-9)
        options.sample = sample

        # Export
        self.e.export(options, self.tmpdir)

        # Test
        filepaths = glob.glob(os.path.join(self.tmpdir, '*.sim'))
        self.assertEqual(1, len(filepaths))

        casfile = File()
        casfile.readFromFilepath(filepaths[0])
        simdata = casfile.getOptionSimulationData()
        regionops = simdata.getRegionOptions()

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat1.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

        region = regionops.getRegion(1)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat3.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

        region = regionops.getRegion(2)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat2.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

    def testexport_multilayers1(self):
        # Options
        options = self.create_basic_options()

        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, 2.0)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, 3.0)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, 4.0)

        sample = HorizontalLayerSample(mat1)
        sample.add_layer(mat2, 25e-9)
        sample.add_layer(mat3, 55e-9)
        options.sample = sample

        # Export
        self.e.export(options, self.tmpdir)

        # Test
        filepaths = glob.glob(os.path.join(self.tmpdir, '*.sim'))
        self.assertEqual(1, len(filepaths))

        casfile = File()
        casfile.readFromFilepath(filepaths[0])
        simdata = casfile.getOptionSimulationData()
        regionops = simdata.getRegionOptions()

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat2.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

        region = regionops.getRegion(1)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat3.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

        region = regionops.getRegion(2)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat1.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

    def testexport_multilayers2(self):
        # Options
        options = self.create_basic_options()

        mat1 = Material('Mat1', {79: 0.5, 47: 0.5}, 2.0)
        mat2 = Material('Mat2', {29: 0.5, 30: 0.5}, 3.0)
        mat3 = Material('Mat3', {13: 0.5, 14: 0.5}, 4.0)

        sample = HorizontalLayerSample()
        sample.add_layer(mat1, 15e-9)
        sample.add_layer(mat2, 25e-9)
        sample.add_layer(mat3, 55e-9)
        options.sample = sample

        # Export
        self.e.export(options, self.tmpdir)

        # Test
        filepaths = glob.glob(os.path.join(self.tmpdir, '*.sim'))
        self.assertEqual(1, len(filepaths))

        casfile = File()
        casfile.readFromFilepath(filepaths[0])
        simdata = casfile.getOptionSimulationData()
        regionops = simdata.getRegionOptions()

        self.assertEqual(3, regionops.getNumberRegions())

        region = regionops.getRegion(0)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat1.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat1', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(79 in elements)
        self.assertTrue(47 in elements)

        region = regionops.getRegion(1)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat2.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat2', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(29 in elements)
        self.assertTrue(30 in elements)

        region = regionops.getRegion(2)
        elements = list(map(operator.attrgetter('Z'), region.getElements()))
        self.assertAlmostEqual(mat3.density_kg_per_m3 / 1000.0, region.Rho, 4)
        self.assertEqual('Mat3', region.Name)
        self.assertEqual(2, len(elements))
        self.assertTrue(13 in elements)
        self.assertTrue(14 in elements)

    def testexport_models(self):
        # Options
        options = self.create_basic_options()

        options.models.append(ElasticCrossSectionModel.MOTT_DROUIN1993)
        options.models.append(IonizationCrossSectionModel.GRYZINSKY)
        options.models.append(IonizationPotentialModel.HOVINGTON)
        options.models.append(RandomNumberGeneratorModel.MERSENNE)
        options.models.append(DirectionCosineModel.SOUM1979)

        # Export
        self.e.export(options, self.tmpdir)

        # Test
        filepaths = glob.glob(os.path.join(self.tmpdir, '*.sim'))
        self.assertEqual(1, len(filepaths))

        casfile = File()
        casfile.readFromFilepath(filepaths[0])
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()

        self.assertEqual(CROSS_SECTION_MOTT_EQUATION, simops.getTotalElectronElasticCrossSection())
        self.assertEqual(CROSS_SECTION_MOTT_EQUATION, simops.getPartialElectronElasticCrossSection())
        self.assertEqual(IONIZATION_CROSS_SECTION_GRYZINSKI, simops.getIonizationCrossSectionType())
        self.assertEqual(IONIZATION_POTENTIAL_HOVINGTON, simops.getIonizationPotentialType())
        self.assertEqual(DIRECTION_COSINES_SOUM, simops.getDirectionCosines())
        self.assertEqual(ENERGY_LOSS_JOY_LUO, simops.getEnergyLossType())
        self.assertEqual(RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER, simops.getRandomNumberGeneratorType())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
