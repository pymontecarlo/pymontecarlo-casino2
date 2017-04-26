"""
Casino 2 worker
"""

# Standard library modules.
import logging
import os
import sys
import subprocess
import tempfile
import shutil
from distutils.dir_util import copy_tree

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import WorkerError
from pymontecarlo.program.worker import Worker, SubprocessWorkerMixin

# Globals and constants variables.

class Casino2Worker(Worker, SubprocessWorkerMixin):

    def run(self, token, simulation, outputdir):
        options = simulation.options
        program = options.program
        exporter = program.create_exporter()
        importer = program.create_importer()

        executable = program.executable
        executable_dir = os.path.dirname(executable)

        # NOTE: Create a temporary directory because Casino cannot
        # accept long file path
        tmpdir = tempfile.mkdtemp()

        try:
            # Export
            exporter.export(options, tmpdir)
            simfilepath = os.path.join(tmpdir, exporter.DEFAULT_SIM_FILENAME)
            simfilepath = simfilepath.replace('/', '\\')

            # Launch
            if sys.platform == 'win32':
                args = [executable, '-batch', simfilepath]
            elif sys.platform == 'linux' or sys.platform == 'darwin':
                args = ['wine', executable, '-batch', simfilepath]
            else:
                raise WorkerError('Unsupported operating system: {}'
                                  .format(sys.platform))

            logging.debug('Launching %s', ' '.join(args))

            token.update(0.1, 'Running Casino 2')
            stdout = subprocess.PIPE
            cwd = executable_dir

            with self._create_process(args, stdout=stdout, cwd=cwd) as process:
                self._wait_process(process, token)

            # Import results
            token.update(0.9, 'Importing results')
            simulation.results += importer.import_(options, tmpdir)

            # Copy to output directory
            copy_tree(tmpdir, outputdir)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        token.update(1.0, 'Casino 2 ended')
        return simulation
