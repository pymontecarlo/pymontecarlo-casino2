"""
Casino 2 importer
"""

# Standard library modules.
import os

# Third party modules.

from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.Element import \
    LINE_K, LINE_L, LINE_M, GENERATED, EMITTED

# Local modules.
from pymontecarlo.program.importer import Importer
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.results.photonintensity import \
    EmittedPhotonIntensityResultBuilder, GeneratedPhotonIntensityResultBuilder
from pymontecarlo.util.xrayline import XrayLine

from pymontecarlo_casino2.exporter import Casino2Exporter

# Globals and constants variables.

LINE_LOOKUP = {LINE_K: 'K', LINE_L: 'L3', LINE_M: 'M5'}

class Casino2Importer(Importer):

    DEFAULT_CAS_FILENAME = os.path.splitext(Casino2Exporter.DEFAULT_SIM_FILENAME)[0] + '.cas'

    def __init__(self):
        super().__init__()

        self.import_analysis_methods[PhotonIntensityAnalysis] = self._import_analysis_photonintensity
        self.import_analysis_methods[KRatioAnalysis] = self._import_analysis_kratio

    def _import(self, options, dirpath, errors):
        filepath = os.path.join(dirpath, self.DEFAULT_CAS_FILENAME)

        casfile = File()
        with open(filepath, 'rb') as fileobj:
            casfile.readFromFileObject(fileobj)

        simdata = casfile.getResultsFirstSimulation()

        return self._run_importers(options, dirpath, errors, simdata)

    def _import_analysis_photonintensity(self, analysis, dirpath, errors, simdata):
        cas_intensities = simdata.getTotalXrayIntensities()

        emitted_builder = EmittedPhotonIntensityResultBuilder(analysis)
        generated_builder = GeneratedPhotonIntensityResultBuilder(analysis)

        for z in cas_intensities:
            for line in cas_intensities[z]:
                transition = LINE_LOOKUP[line]
                xrayline = XrayLine(z, transition)
                datum = cas_intensities[z][line]

                value = datum[EMITTED]
                error = 0.0
                emitted_builder.add_intensity(xrayline, value, error)

                value = datum[GENERATED]
                error = 0.0
                generated_builder.add_intensity(xrayline, value, error)

        return [emitted_builder.build(), generated_builder.build()]

    def _import_analysis_kratio(self, analysis, dirpath, errors, simdata):
        # Do nothing
        return []

