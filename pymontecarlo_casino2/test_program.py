#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class TestCasino2Program(TestCase):

    def setUp(self):
        super().setUp()

        self.program = Casino2Program()

    def testname(self):
        self.assertEqual('Casino 2', self.program.name)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
