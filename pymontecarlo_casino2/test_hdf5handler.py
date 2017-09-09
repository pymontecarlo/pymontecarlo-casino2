#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pymontecarlo.testcase import TestCase

from pymontecarlo_casino2.hdf5handler import Casino2ProgramHDF5Handler
from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class TestCasino2ProgramHDF5Handler(TestCase):

    def testconvert_parse(self):
        handler = Casino2ProgramHDF5Handler()
        program = Casino2Program(number_trajectories=500)
        program2 = self.convert_parse_hdf5handler(handler, program)
        self.assertEqual(program2, program)

#        import h5py
#        with h5py.File('/tmp/program.h5', 'w') as f:
#            handler.convert(program, f)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()