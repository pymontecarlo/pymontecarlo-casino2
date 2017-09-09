#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo_casino2.serieshandler import Casino2ProgramSeriesHandler
from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class TestCasino2ProgramSeriesHandler(TestCase):

    def testconvert(self):
        handler = Casino2ProgramSeriesHandler()
        program = Casino2Program(number_trajectories=500)
        s = self.convert_serieshandler(handler, program)
        self.assertEqual(8, len(s))
        self.assertEqual(program.name, s['program'])
        self.assertEqual(500, s['number of trajectories'])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
