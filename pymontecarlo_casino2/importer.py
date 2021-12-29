"""
Casino 2 importer
"""

# Standard library modules.
import os

# Third party modules.
from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.line import (
    ATOMLINE_KA1,
    ATOMLINE_KA2,
    ATOMLINE_KB1,
    ATOMLINE_KB2,
    ATOMLINE_LA,
    ATOMLINE_LB1,
    ATOMLINE_LB2,
    ATOMLINE_LG,
    ATOMLINE_MA,
)

import pyxray

# Local modules.
from pymontecarlo.options.program.importer import ImporterBase
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.results.photonintensity import EmittedPhotonIntensityResultBuilder

from pymontecarlo_casino2.exporter import Casino2Exporter

# Globals and constants variables.

LINE_LOOKUP = {
    ATOMLINE_KA1: pyxray.xray_transition("Ka1"),
    ATOMLINE_KA2: pyxray.xray_transition("Ka2"),
    ATOMLINE_KB1: pyxray.xray_transition("Kb1"),
    ATOMLINE_KB2: pyxray.xray_transition("Kb3"),
    ATOMLINE_LA: pyxray.xray_transition("La"),
    ATOMLINE_LB1: pyxray.xray_transition("Lb1"),
    ATOMLINE_LB2: pyxray.xray_transition("Lb2"),
    ATOMLINE_LG: pyxray.xray_transition("Lg1"),
    ATOMLINE_MA: pyxray.xray_transition("Ma"),
}


class Casino2Importer(ImporterBase):

    DEFAULT_CAS_FILENAME = (
        os.path.splitext(Casino2Exporter.DEFAULT_SIM_FILENAME)[0] + ".cas"
    )

    def __init__(self):
        super().__init__()

        self.import_analysis_methods[
            PhotonIntensityAnalysis
        ] = self._import_analysis_photonintensity
        self.import_analysis_methods[KRatioAnalysis] = self._import_analysis_kratio

    async def _import(self, options, dirpath, erracc):
        filepath = os.path.join(dirpath, self.DEFAULT_CAS_FILENAME)

        casfile = File()
        with open(filepath, "rb") as fileobj:
            casfile.readFromFileObject(fileobj)

        simdata = casfile.getResultsFirstSimulation()

        return self._run_importers(options, dirpath, erracc, simdata)

    def _import_analysis_photonintensity(
        self, options, analysis, dirpath, erracc, simdata
    ):
        emitted_builder = EmittedPhotonIntensityResultBuilder(analysis)
        intensities = simdata.get_total_xray_intensities_1_esr()

        for z in intensities:
            for line in intensities[z]:
                if line not in LINE_LOOKUP:
                    continue

                transition = LINE_LOOKUP[line]
                xrayline = pyxray.xray_line(z, transition)
                value = intensities[z][line]
                error = 0.0
                emitted_builder.add_intensity(xrayline, value, error)

        return [emitted_builder.build()]

    def _import_analysis_kratio(self, options, analysis, dirpath, erracc, simdata):
        # Do nothing
        return []
