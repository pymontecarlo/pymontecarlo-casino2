#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel

from pymontecarlo_casino2.program import Casino2Program, Casino2ProgramBuilder

# Globals and constants variables.

class TestCasino2Program(TestCase):

    def setUp(self):
        super().setUp()

        self.program = Casino2Program()

    def testname(self):
        self.assertEqual('Casino 2', self.program.name)

class TestCasino2ProgramBuilder(TestCase):

    def testbuild(self):
        b = Casino2ProgramBuilder()
        programs = b.build()
        self.assertEqual(1, len(programs))

    def testbuild2(self):
        b = Casino2ProgramBuilder()
        b.add_number_trajectories(100)
        b.add_number_trajectories(200)
        b.add_elastic_cross_section_model(ElasticCrossSectionModel.RUTHERFORD)
        b.add_elastic_cross_section_model(ElasticCrossSectionModel.MOTT_CZYZEWSKI1990)
        programs = b.build()
        self.assertEqual(4, len(programs))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
