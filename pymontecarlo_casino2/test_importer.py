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
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResult
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
        self.assertEqual(1, len(self.simulation.results))

    def test_import_analysis_photonintensity_emitted(self):
        result = self.simulation.find_result(EmittedPhotonIntensityResult)[0]

        self.assertEqual(29, len(result))

        q = result[('Au', 'La')]
        self.assertAlmostEqual(2.73255e-7, q.n, 13)

        q = result[('Si', 'Ka1')]
        self.assertAlmostEqual(1.6331941e-6, q.n, 13)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.ERROR)
    unittest.main()
