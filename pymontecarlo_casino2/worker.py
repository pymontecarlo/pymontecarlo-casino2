"""
Casino 2 worker
"""

# Standard library modules.
import os
import sys
import tempfile
import shutil
import asyncio
import logging

logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pymontecarlo.exceptions import WorkerError
from pymontecarlo.options.program.worker import WorkerBase
from pymontecarlo.util.process import create_startupinfo, kill_process

# Globals and constants variables.


class Casino2Worker(WorkerBase):
    async def _run(self, token, simulation, outputdir):
        options = simulation.options
        program = options.program

        executable = program.executable
        executable_dir = os.path.dirname(executable)

        # NOTE: Create a temporary directory because Casino cannot
        # accept long file path
        tmpdir = tempfile.mkdtemp()

        try:
            # Export
            token.update(0.15, "Exporting options")
            await program.exporter.export(options, tmpdir)

            # Launch
            token.update(0.2, "Running Casino 2")

            simfilepath = os.path.join(tmpdir, program.exporter.DEFAULT_SIM_FILENAME)
            simfilepath = simfilepath.replace("/", "\\")

            if sys.platform == "win32":
                args = [executable, "-batch", simfilepath]
            elif sys.platform == "linux" or sys.platform == "darwin":
                args = ["wine", executable, "-batch", simfilepath]
            else:
                raise WorkerError(
                    "Unsupported operating system: {}".format(sys.platform)
                )

            logger.debug("Launching %s", " ".join(args))

            kwargs = {}
            kwargs["stdout"] = asyncio.subprocess.DEVNULL
            kwargs["stderr"] = asyncio.subprocess.DEVNULL
            kwargs["cwd"] = executable_dir
            kwargs["startupinfo"] = create_startupinfo()

            process = await asyncio.create_subprocess_exec(*args, **kwargs)
            returncode = await process.wait()

            if returncode != 0:
                raise WorkerError(
                    "Error running the simulation. Casino2 threw an error."
                )

            # Import results
            token.update(0.9, "Importing results")
            simulation.results += await program.importer.import_(options, tmpdir)

            # Copy to output directory
            shutil.copytree(tmpdir, outputdir, dirs_exist_ok=True)

        except asyncio.CancelledError:
            # Make sure the process is killed before raising CancelledError
            kill_process(process.pid)
            raise

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

        return simulation
