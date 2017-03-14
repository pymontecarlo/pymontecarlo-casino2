#!/usr/bin/env python
""" """

# Standard library modules.
import os
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo_casino2.importer import Casino2Importer

from pymontecarlo.testcase import TestCase
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResult, GeneratedPhotonIntensityResult
from pymontecarlo.simulation import Simulation

# Globals and constants variables.

class TestCasino2Importer(TestCase):

    def setUp(self):
        super().setUp()

        self.options = self.create_basic_options()

        dirpath = os.path.join(os.path.dirname(__file__), 'testdata', 'sim1')
        imp = Casino2Importer()
        results = imp.import_(self.options, dirpath)
        self.simulation = Simulation(self.options, results)

    def testskeleton(self):
        self.assertEqual(2, len(self.simulation.results))

    def test_import_analysis_photonintensity_emitted(self):
        result = self.simulation.find_result(EmittedPhotonIntensityResult)[0]

        self.assertEqual(10, len(result))

        q = result[('Au', 'L3')]
        self.assertAlmostEqual(8.0088, q.n, 4)

        q = result[('Si', 'K')]
        self.assertAlmostEqual(38.7659, q.n, 4)

    def test_import_analysis_photonintensity_generated(self):
        result = self.simulation.find_result(GeneratedPhotonIntensityResult)[0]

        self.assertEqual(10, len(result))

        q = result[('Au', 'L3')]
        self.assertAlmostEqual(8.0270, q.n, 4)

        q = result[('Si', 'K')]
        self.assertAlmostEqual(46.8173, q.n, 4)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
