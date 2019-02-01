"""
ExporterBase to CAS file
"""

# Standard library modules.
import os

# Third party modules.
import pyxray

from pkg_resources import resource_stream #@UnresolvedImport

from casinotools.fileformat.casino2.File import File
from casinotools.fileformat.casino2.SimulationOptions import \
    (DIRECTION_COSINES_SOUM, DIRECTION_COSINES_DROUIN,
     CROSS_SECTION_MOTT_JOY, CROSS_SECTION_MOTT_EQUATION,
     CROSS_SECTION_MOTT_BROWNING, CROSS_SECTION_MOTT_RUTHERFORD,
     IONIZATION_CROSS_SECTION_POUCHOU,
     IONIZATION_CROSS_SECTION_BROWN_POWELL, IONIZATION_CROSS_SECTION_CASNATI,
     IONIZATION_CROSS_SECTION_GRYZINSKI, IONIZATION_CROSS_SECTION_JAKOBY,
     IONIZATION_POTENTIAL_JOY, IONIZATION_POTENTIAL_BERGER,
     IONIZATION_POTENTIAL_HOVINGTON,
     RANDOM_NUMBER_GENERATOR_PRESS_ET_AL, RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER,
     ENERGY_LOSS_JOY_LUO)

# Local modules.
from pymontecarlo.options import Particle, VACUUM
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import  \
    SubstrateSample, HorizontalLayerSample, VerticalLayerSample
from pymontecarlo.options.detector import PhotonDetector
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.model import \
    (ElasticCrossSectionModel, IonizationCrossSectionModel,
     IonizationPotentialModel, RandomNumberGeneratorModel,
     DirectionCosineModel, EnergyLossModel)
from pymontecarlo.options.program.exporter import ExporterBase

# Globals and constants variables.
ELASTIC_CROSS_SECTION_MODEL_LOOKUP = \
    {ElasticCrossSectionModel.MOTT_CZYZEWSKI1990: CROSS_SECTION_MOTT_JOY,
     ElasticCrossSectionModel.MOTT_DROUIN1993: CROSS_SECTION_MOTT_EQUATION,
     ElasticCrossSectionModel.MOTT_BROWNING1994: CROSS_SECTION_MOTT_BROWNING,
     ElasticCrossSectionModel.RUTHERFORD: CROSS_SECTION_MOTT_RUTHERFORD}

# Casino 2.5.1 seems to have removed Gauvin ionization cross section and the
# first ionization cross section is Pouchou
IONIZATION_CROSS_SECTION_MODEL_LOOKUP = \
    {IonizationCrossSectionModel.POUCHOU1996: IONIZATION_CROSS_SECTION_POUCHOU - 1,
     IonizationCrossSectionModel.BROWN_POWELL: IONIZATION_CROSS_SECTION_BROWN_POWELL - 1,
     IonizationCrossSectionModel.CASNATI1982: IONIZATION_CROSS_SECTION_CASNATI - 1,
     IonizationCrossSectionModel.GRYZINSKY: IONIZATION_CROSS_SECTION_GRYZINSKI - 1,
     IonizationCrossSectionModel.JAKOBY: IONIZATION_CROSS_SECTION_JAKOBY - 1}

IONIZATION_POTENTIAL_MODEL_LOOKUP = \
    {IonizationPotentialModel.JOY_LUO1989: IONIZATION_POTENTIAL_JOY,
     IonizationPotentialModel.BERGER_SELTZER1983: IONIZATION_POTENTIAL_BERGER,
     IonizationPotentialModel.HOVINGTON: IONIZATION_POTENTIAL_HOVINGTON}

RANDOM_NUMBER_GENERATOR_MODEL_LOOKUP = \
    {RandomNumberGeneratorModel.PRESS1996_RAND1: RANDOM_NUMBER_GENERATOR_PRESS_ET_AL,
     RandomNumberGeneratorModel.MERSENNE: RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER}

DIRECTION_COSINES_MODEL_LOOKUP = \
    {DirectionCosineModel.SOUM1979: DIRECTION_COSINES_SOUM,
     DirectionCosineModel.DROUIN1996: DIRECTION_COSINES_DROUIN}

ENERGY_LOSS_MODEL_LOOKUP = \
    {EnergyLossModel.JOY_LUO1989: ENERGY_LOSS_JOY_LUO}

class Casino2Exporter(ExporterBase):

    DEFAULT_SIM_FILENAME = 'options.sim'

    def __init__(self):
        super().__init__()

        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian

        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate
        self.sample_export_methods[HorizontalLayerSample] = self._export_sample_horizontallayers
        self.sample_export_methods[VerticalLayerSample] = self._export_sample_verticallayers

        self.detector_export_methods[PhotonDetector] = self._export_detector_photon

        self.analysis_export_methods[PhotonIntensityAnalysis] = self._export_analysis_photonintensity
        self.analysis_export_methods[KRatioAnalysis] = self._export_analysis_kratio

    async def _export(self, options, dirpath, erracc, dry_run=False):
        casfile = File()

        # Load template (from geometry)
        fileobj = self._get_sim_template(options.sample, erracc)
        if fileobj is not None:
            casfile.readFromFileObject(fileobj)

        # Run exporters
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        if simdata is None or simops is None:
            erracc.add_exception(IOError('Could not open .sim template file'))

        self._run_exporters(options, erracc, simdata, simops)

        # Write to disk
        if not dry_run:
            filepath = os.path.join(dirpath, self.DEFAULT_SIM_FILENAME)
            casfile.write(filepath)

    def _get_sim_template(self, sample, erracc):
        if isinstance(sample, SubstrateSample):
            return resource_stream(__name__, "templates/Substrate.sim")

        elif isinstance(sample, HorizontalLayerSample):
            regions_count = len(sample.layers)

            if sample.has_substrate():
                regions_count += 1

            filename = "HorizontalLayers{0:d}.sim".format(regions_count)
            buffer = resource_stream(__name__, "templates/" + filename)
            if buffer is None:
                exc = IOError('No template for "{0}" with {1:d} regions'
                              .format(sample, regions_count))
                erracc.add_exception(exc)

            return buffer

        elif isinstance(sample, VerticalLayerSample):
            regions_count = len(sample.layers)
            regions_count += 2 # left and right regions

            filename = "VerticalLayers{0:d}.sim".format(regions_count)
            buffer = resource_stream(__name__, "templates/" + filename)
            if buffer is None:
                exc = IOError('No template for "{0}" with {1:d} regions'
                              .format(sample, regions_count))
                erracc.add_exception(exc)

            return buffer

        else:
            exc = IOError('Unknown geometry: {0}'.format(sample))
            erracc.add_exception(exc)

    def _export_program(self, program, options, erracc, simdata, simops):
        # Trajectories
        number_trajectories = program.number_trajectories

        if number_trajectories < 25:
            exc = ValueError('Number of showers ({0}) must be greater or equal to 25.'
                             .format(number_trajectories))
            erracc.add_exception(exc)

        if number_trajectories > 1e9:
            exc = ValueError('Number of showers ({0}) must be less than 1e9.'
                             .format(number_trajectories))
            erracc.add_exception(exc)

        simops.setNumberElectrons(number_trajectories)

        # Elastic cross section
        model = program.elastic_cross_section_model
        self._export_model(model, ELASTIC_CROSS_SECTION_MODEL_LOOKUP.keys(), erracc)
        simops.setElasticCrossSectionType(ELASTIC_CROSS_SECTION_MODEL_LOOKUP[model])

        # Ionization cross section
        model = program.ionization_cross_section_model
        self._export_model(model, IONIZATION_CROSS_SECTION_MODEL_LOOKUP.keys(), erracc)
        simops.setIonizationCrossSectionType(IONIZATION_CROSS_SECTION_MODEL_LOOKUP[model])

        # Ionization potential
        model = program.ionization_potential_model
        self._export_model(model, IONIZATION_POTENTIAL_MODEL_LOOKUP.keys(), erracc)
        simops.setIonizationPotentialType(IONIZATION_POTENTIAL_MODEL_LOOKUP[model])

        # Random number generator
        model = program.random_number_generator_model
        self._export_model(model, RANDOM_NUMBER_GENERATOR_MODEL_LOOKUP.keys(), erracc)
        simops.setRandomNumberGeneratorType(RANDOM_NUMBER_GENERATOR_MODEL_LOOKUP[model])

        # Direction cosines
        model = program.direction_cosine_model
        self._export_model(model, DIRECTION_COSINES_MODEL_LOOKUP.keys(), erracc)
        simops.setDirectionCosines(DIRECTION_COSINES_MODEL_LOOKUP[model])

        # Energy loss
        model = program.energy_loss_model
        self._export_model(model, ENERGY_LOSS_MODEL_LOOKUP.keys(), erracc)
        simops.setEnergyLossType(ENERGY_LOSS_MODEL_LOOKUP[model])

    def _export_beam_gaussian(self, beam, options, erracc, simdata, simops):
        super()._export_beam_gaussian(beam, options, erracc, simdata, simops)

        # Particle
        particle = beam.particle

        if particle is not Particle.ELECTRON:
            exc = ValueError('Particle {0} is not supported. Only ELECTRON.'
                             .format(particle))
            erracc.add_exception(exc)

        # Energy
        simops.setIncidentEnergy_keV(beam.energy_eV / 1000.0) # keV

        # Position
        if beam.y0_m != 0.0:
            exc = ValueError("Beam initial y position ({0:g}) must be 0.0"
                             .format(beam.y0_m))
            erracc.add_exception(exc)

        simops.setPosition(beam.x0_m * 1e9) # nm

        # Diameter
        # Casino's beam diameter contains 99.9% of the electrons (n=3.290)
        # d_{CASINO} = 2 (3.2905267 \sigma)
        # d_{FWHM} = 2 (1.177411 \sigma)
        # d_{CASINO} = 2.7947137 d_{FWHM}
        # NOTE: The attribute Beam_Diameter corresponds in fact to the beam
        # radius.
        simops.Beam_Diameter = 2.7947137 * beam.diameter_m * 1e9 / 2.0 # nm

        simops.Beam_angle = 0.0

    def _export_material(self, material, options, erracc, region):
        super()._export_material(material, options, erracc)

        region.removeAllElements()

        for z, fraction in material.composition.items():
            region.addElement(pyxray.element_symbol(z), weight_fraction=fraction)

        region.update() # Calculate number of elements, mean atomic number

        region.User_Density = True
        region.Rho = material.density_g_per_cm3
        region.Name = material.name

    def _export_layer(self, layer, options, erracc, region):
        if layer.material is VACUUM:
            exc = ValueError('Layer with VACUUM material is not supported.')
            erracc.add_exception(exc)

        super()._export_layer(layer, options, erracc, region)

    def _export_sample(self, sample, options, erracc, simdata, simops):
        if sample.tilt_rad != 0.0:
            exc = ValueError('Sample tilt is not supported.')
            erracc.add_exception(exc)

        if sample.azimuth_rad != 0.0:
            exc = ValueError('Sample azimuth is not supported.')
            erracc.add_exception(exc)

        super()._export_sample(sample, options, erracc, simdata, simops)

    def _export_sample_substrate(self, sample, options, erracc, simdata, simops):
        super()._export_sample_substrate(sample, options, erracc, simdata, simops)

        regionops = simdata.getRegionOptions()
        region = regionops.getRegion(0)
        self._export_material(sample.material, options, erracc, region)

    def _export_sample_horizontallayers(self, sample, options, erracc, simdata, simops):
        super()._export_sample_horizontallayers(sample, options, erracc, simdata, simops)

        regionops = simdata.getRegionOptions()
        layers = sample.layers
        zpositions_m = sample.layers_zpositions_m

        for i, (layer, zposition_m) in enumerate(zip(layers, zpositions_m)):
            region = regionops.getRegion(i)
            self._export_layer(layer, options, erracc, region)

            zmin_m, zmax_m = zposition_m
            parameters = [abs(zmax_m) * 1e9, abs(zmin_m) * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        if sample.has_substrate():
            region = regionops.getRegion(regionops.getNumberRegions() - 1)
            self._export_material(sample.substrate_material, options, erracc, region)

            zmin_m, _zmax_m = zpositions_m[-1]
            parameters = region.getParameters()
            parameters[0] = abs(zmin_m) * 1e9
            parameters[2] = parameters[0] + 10.0
            region.setParameters(parameters)
        else:
            zmin_m, _zmax_m = zpositions_m[-1]
            simops.setTotalThickness_nm(abs(zmin_m) * 1e9)

    def _export_sample_verticallayers(self, sample, options, erracc, simdata, simops):
        super()._export_sample_verticallayers(sample, options, erracc, simdata, simops)

        regionops = simdata.getRegionOptions()
        layers = sample.layers
        xpositions_m = sample.layers_xpositions_m
        assert len(layers) == regionops.getNumberRegions() - 2 # without substrates

        # Left substrate
        region = regionops.getRegion(0)
        self._export_material(sample.left_material, options, erracc, region)

        xmin_m, _xmax_m = xpositions_m[0] if xpositions_m else (0.0, 0.0)
        parameters = region.getParameters()
        parameters[1] = xmin_m * 1e9
        parameters[2] = parameters[1] - 10.0
        region.setParameters(parameters)

        # Layers
        for i, (layer, xposition_m) in enumerate(zip(layers, xpositions_m)):
            region = regionops.getRegion(i + 1)
            self._export_layer(layer, options, erracc, region)

            xmin_m, xmax_m = xposition_m
            parameters = [xmin_m * 1e9, xmax_m * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        # Right substrate
        region = regionops.getRegion(regionops.getNumberRegions() - 1)
        self._export_material(sample.right_material, options, erracc, region)

        _xmin_m, xmax_m = xpositions_m[-1] if xpositions_m else (0.0, 0.0)
        parameters = region.getParameters()
        parameters[0] = xmax_m * 1e9
        parameters[2] = parameters[0] + 10.0
        region.setParameters(parameters)

    def _export_detectors(self, detectors, options, erracc, simdata, simops):
        simops.FEmissionRX = 0 # Do not simulate x-rays

        super()._export_detectors(detectors, options, erracc, simdata, simops)

    def _export_detector_photon(self, detector, options, erracc, simdata, simops):
        super()._export_detector_photon(detector, options, erracc, simdata, simops)

        simops.TOA = detector.elevation_deg
        simops.PhieRX = detector.azimuth_deg
        simops.FEmissionRX = 1 # Simulate x-rays

    def _export_analyses(self, analyses, options, erracc, simdata, simops):
        simops.RangeFinder = 0 # Simulated range
        simops.Memory_Keep = 0 # Do not save trajectories

        super()._export_analyses(analyses, options, erracc, simdata, simops)

    def _export_analysis_photonintensity(self, analysis, options, erracc, simdata, simops):
        super()._export_analysis_photonintensity(analysis, options, erracc, simdata, simops)

    def _export_analysis_kratio(self, analysis, options, erracc, simdata, simops):
        super()._export_analysis_kratio(analysis, options, erracc, simdata, simops)
