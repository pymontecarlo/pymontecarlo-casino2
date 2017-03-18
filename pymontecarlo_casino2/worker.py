"""
Casino 2 worker
"""

# Standard library modules.
import logging
import os
import subprocess

# Third party modules.

# Local modules.
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

        exporter.export(options, outputdir)
        simfilepath = os.path.join(outputdir, exporter.DEFAULT_SIM_FILENAME)
        simfilepath = simfilepath.replace('/', '\\')

        # Launch
        args = [executable, '-batch', simfilepath]
        logging.debug('Launching %s', ' '.join(args))

        token.update(0.0, 'Running Casino 2')
        stdout = subprocess.PIPE
        cwd = executable_dir

        with self._create_process(args, stdout=stdout, cwd=cwd) as process:
            self._wait_process(process, token)

        # Import results
        token.update(0.9, 'Importing results')
        simulation.results += importer.import_(options, outputdir)

        token.update(1.0, 'Casino 2 ended')
        return simulation
