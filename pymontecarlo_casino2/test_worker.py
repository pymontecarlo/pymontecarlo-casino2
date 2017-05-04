#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pymontecarlo
from pymontecarlo.testcase import TestCase
from pymontecarlo.simulation import Simulation
from pymontecarlo.options.material import Material
from pymontecarlo.options.sample import \
    SubstrateSample, HorizontalLayerSample, VerticalLayerSample
from pymontecarlo.util.future import Token
from pymontecarlo_casino2.worker import Casino2Worker

# Globals and constants variables.

@unittest.skipUnless(pymontecarlo.settings.has_program('casino2'),
                     'Casino 2 should be configured to run these tests')
class TestCasino2Worker(TestCase):

    def setUp(self):
        super().setUp()

        self.token = Token()
        self.outputdir = self.create_temp_dir()

        self.options = self.create_basic_options()
        self.options.program = pymontecarlo.settings.get_program('casino2')

        self.worker = Casino2Worker()

    def _run_and_test(self, sample):
        self.options.sample = sample
        simulation = Simulation(self.options)
        self.worker.run(self.token, simulation, self.outputdir)

        self.assertEqual(2, len(simulation.results))

    def testsubstrate(self):
        sample = SubstrateSample(Material.pure(39))
        self._run_and_test(sample)

    def testhorizontallayers2(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers3(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers4(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers5(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers6(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers7(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers8(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        self._run_and_test(sample)


    def testhorizontallayers9(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers10(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        sample.add_layer(Material.pure(49), 20e-9)
        self._run_and_test(sample)

    def testhorizontallayers11(self):
        sample = HorizontalLayerSample(Material.pure(39))
        sample.add_layer(Material.pure(40), 20e-9)
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        sample.add_layer(Material.pure(49), 20e-9)
        sample.add_layer(Material.pure(50), 20e-9)
        self._run_and_test(sample)

    def testverticallayers2(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        self._run_and_test(sample)

    def testverticallayers3(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        self._run_and_test(sample)

    def testverticallayers4(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        self._run_and_test(sample)

    def testverticallayers5(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        self._run_and_test(sample)

    def testverticallayers6(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        self._run_and_test(sample)

    def testverticallayers7(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        self._run_and_test(sample)

    def testverticallayers8(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        self._run_and_test(sample)

    def testverticallayers9(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        self._run_and_test(sample)

    def testverticallayers10(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        sample.add_layer(Material.pure(49), 20e-9)
        self._run_and_test(sample)

    def testverticallayers11(self):
        sample = VerticalLayerSample(Material.pure(39), Material.pure(40))
        sample.add_layer(Material.pure(41), 20e-9)
        sample.add_layer(Material.pure(42), 20e-9)
        sample.add_layer(Material.pure(44), 20e-9)
        sample.add_layer(Material.pure(45), 20e-9)
        sample.add_layer(Material.pure(46), 20e-9)
        sample.add_layer(Material.pure(47), 20e-9)
        sample.add_layer(Material.pure(48), 20e-9)
        sample.add_layer(Material.pure(49), 20e-9)
        sample.add_layer(Material.pure(50), 20e-9)
        self._run_and_test(sample)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
