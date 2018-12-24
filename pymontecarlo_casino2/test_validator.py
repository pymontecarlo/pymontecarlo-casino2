#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase
from pymontecarlo_casino2.program import Casino2Program
from pymontecarlo_casino2.validator import Casino2Validator

# Globals and constants variables.

class TestCasino2Validator(TestCase):

    def setUp(self):
        super().setUp()

        self.validator = Casino2Validator()

        self.options = self.create_basic_options()
        self.options.program = Casino2Program()

    def testvalidate_options(self):
        self.validator.validate_options(self.options)

    def test_validate_program_number_trajectories(self):
        self.options.program.number_trajectories = 0

        errors = set()
        warnings = set()
        self.validator._validate_options(self.options, errors, warnings)

        self.assertEqual(1, len(errors))
        self.assertEqual(0, len(warnings))

    def test_validate_program_number_trajectories2(self):
        self.options.program.number_trajectories = 1e10

        errors = set()
        warnings = set()
        self.validator._validate_options(self.options, errors, warnings)

        self.assertEqual(1, len(errors))
        self.assertEqual(0, len(warnings))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
