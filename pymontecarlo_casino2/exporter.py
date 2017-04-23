"""
Exporter to CAS file
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
     IONIZATION_CROSS_SECTION_GAUVIN, IONIZATION_CROSS_SECTION_POUCHOU,
     IONIZATION_CROSS_SECTION_BROWN_POWELL, IONIZATION_CROSS_SECTION_CASNATI,
     IONIZATION_CROSS_SECTION_GRYZINSKI, IONIZATION_CROSS_SECTION_JAKOBY,
     IONIZATION_POTENTIAL_JOY, IONIZATION_POTENTIAL_BERGER,
     IONIZATION_POTENTIAL_HOVINGTON,
     RANDOM_NUMBER_GENERATOR_PRESS_ET_AL, RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER,
     ENERGY_LOSS_JOY_LUO)

# Local modules.
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import  \
    SubstrateSample, HorizontalLayerSample, VerticalLayerSample
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis
from pymontecarlo.options.model import \
    (ElasticCrossSectionModel, IonizationCrossSectionModel,
     IonizationPotentialModel, RandomNumberGeneratorModel,
     DirectionCosineModel, EnergyLossModel)

from pymontecarlo.program.exporter import Exporter

# Globals and constants variables.

def _setup_region_material(region, material):
    region.removeAllElements()

    for z, fraction in material.composition.items():
        region.addElement(pyxray.element_symbol(z), weightFraction=fraction)

    region.update() # Calculate number of elements, mean atomic number

    region.User_Density = True
    region.Rho = material.density_g_per_cm3
    region.Name = material.name

def _find_model_type(lookup, model, errors):
    if model not in lookup:
        exc = ValueError('Unknown model: {0}'.format(model))
        errors.add(exc)
        return None

    return lookup[model]

class Casino2Exporter(Exporter):

    DEFAULT_SIM_FILENAME = 'options.sim'

    def __init__(self):
        super().__init__()

        self.beam_export_methods[GaussianBeam] = self._export_beam_gaussian

        self.sample_export_methods[SubstrateSample] = self._export_sample_substrate
        self.sample_export_methods[HorizontalLayerSample] = self._export_sample_horizontallayers
        self.sample_export_methods[VerticalLayerSample] = self._export_sample_verticallayers

        self.analysis_export_methods[PhotonIntensityAnalysis] = self._export_analysis_photonintensity
        self.analysis_export_methods[KRatioAnalysis] = self._export_analysis_kratio

        self.limit_export_methods[ShowersLimit] = self._export_limit_showers

        self.model_export_methods[ElasticCrossSectionModel] = self._export_model_elasticcrosssection
        self.model_export_methods[IonizationCrossSectionModel] = self._export_model_ionizationcrosssection
        self.model_export_methods[IonizationPotentialModel] = self._export_model_ionizationpotential
        self.model_export_methods[RandomNumberGeneratorModel] = self._export_model_randomnumbergenerator
        self.model_export_methods[DirectionCosineModel] = self._export_model_directioncosine
        self.model_export_methods[EnergyLossModel] = self._export_model_energyloss
        #self.model_export_methods[MassAbsorptionCoefficientModel] = self._export_model_massabsorptioncoefficient

    def _export(self, options, dirpath, errors):
        casfile = File()

        # Load template (from geometry)
        fileobj = self._get_sim_template(options.sample, errors)
        if fileobj is None:
            return
        casfile.readFromFileObject(fileobj)

        # Run exporters
        simdata = casfile.getOptionSimulationData()
        simops = simdata.getSimulationOptions()
        self._run_exporters(options, errors, simdata, simops)

        # Write to disk
        filepath = os.path.join(dirpath, self.DEFAULT_SIM_FILENAME)
        casfile.write(filepath)

    def _get_sim_template(self, sample, errors):
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
                errors.add(exc)
                return None

            return buffer

        elif isinstance(sample, VerticalLayerSample):
            regions_count = len(sample.layers)
            regions_count += 2 # left and right regions

            filename = "VerticalLayers{0:d}.sim".format(regions_count)
            buffer = resource_stream(__name__, "templates/" + filename)
            if buffer is None:
                exc = IOError('No template for "{0}" with {1:d} regions'
                              .format(sample, regions_count))
                errors.add(exc)
                return None

            return buffer

        else:
            exc = IOError('Unknown geometry: {0}'.format(sample))
            errors.add(exc)
            return None

    def _export_beam_gaussian(self, beam, errors, simdata, simops):
        simops.setIncidentEnergy_keV(beam.energy_eV / 1000.0) # keV
        simops.setPosition(beam.x0_m * 1e9) # nm

        # Beam diameter
        # Casino's beam diameter contains 99.9% of the electrons (n=3.290)
        # d_{CASINO} = 2 (3.2905267 \sigma)
        # d_{FWHM} = 2 (1.177411 \sigma)
        # d_{CASINO} = 2.7947137 d_{FWHM}
        # NOTE: The attribute Beam_Diameter corresponds in fact to the beam
        # radius.
        simops.Beam_Diameter = 2.7947137 * beam.diameter_m * 1e9 / 2.0 # nm

        simops.Beam_angle = 0.0

    def _export_sample_substrate(self, sample, errors, simdata, simops):
        regionops = simdata.getRegionOptions()

        region = regionops.getRegion(0)
        _setup_region_material(region, sample.material)

    def _export_sample_horizontallayers(self, sample, errors, simdata, simops):
        regionops = simdata.getRegionOptions()
        layers = sample.layers
        zpositions_m = sample.layers_zpositions_m

        for i, (layer, zposition_m) in enumerate(zip(layers, zpositions_m)):
            region = regionops.getRegion(i)
            _setup_region_material(region, layer.material)

            zmin_m, zmax_m = zposition_m
            parameters = [abs(zmax_m) * 1e9, abs(zmin_m) * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        if sample.has_substrate():
            region = regionops.getRegion(regionops.getNumberRegions() - 1)
            _setup_region_material(region, sample.substrate_material)

            zmin_m, _zmax_m = zpositions_m[-1]
            parameters = region.getParameters()
            parameters[0] = abs(zmin_m) * 1e9
            parameters[2] = parameters[0] + 10.0
            region.setParameters(parameters)

    def _export_sample_verticallayers(self, sample, errors, simdata, simops):
        regionops = simdata.getRegionOptions()
        layers = sample.layers
        xpositions_m = sample.layers_xpositions_m
        assert len(layers) == regionops.getNumberRegions() - 2 # without substrates

        # Left substrate
        region = regionops.getRegion(0)
        _setup_region_material(region, sample.left_material)

        xmin_m, _xmax_m = xpositions_m[0] if xpositions_m else (0.0, 0.0)
        parameters = region.getParameters()
        parameters[1] = xmin_m * 1e9
        parameters[2] = parameters[1] - 10.0
        region.setParameters(parameters)

        # Layers
        for i, (layer, xposition_m) in enumerate(zip(layers, xpositions_m)):
            region = regionops.getRegion(i + 1)
            _setup_region_material(region, layer.material)

            xmin_m, xmax_m = xposition_m
            parameters = [xmin_m * 1e9, xmax_m * 1e9, 0.0, 0.0]
            region.setParameters(parameters)

        # Right substrate
        region = regionops.getRegion(regionops.getNumberRegions() - 1)
        _setup_region_material(region, sample.right_material)

        _xmin_m, xmax_m = xpositions_m[-1] if xpositions_m else (0.0, 0.0)
        parameters = region.getParameters()
        parameters[0] = xmax_m * 1e9
        parameters[2] = parameters[0] + 10.0
        region.setParameters(parameters)

    def _export_detector_photon(self, detector, errors, simdata, simops):
        simops.TOA = detector.elevation_deg
        simops.PhieRX = detector.azimuth_deg
        simops.FEmissionRX = 1 # Simulate x-rays

    def _export_analyses(self, analyses, errors, simdata, simops):
        simops.RangeFinder = 3 # Fixed range
        simops.FEmissionRX = 0 # Do not simulate x-rays
        simops.Memory_Keep = 0 # Do not save trajectories

        super()._export_analyses(analyses, errors, simdata, simops)

    def _export_analysis_photonintensity(self, analysis, errors, simdata, simops):
        self._export_detector_photon(analysis.photon_detector, errors, simdata, simops)

    def _export_analysis_kratio(self, analysis, errors, simdata, simops):
        # Do nothing. The setup is taken care of by the photon intensity analysis.
        pass

    def _export_limit_showers(self, limit, errors, simdata, simops):
        simops.setNumberElectrons(limit.number_trajectories)

    def _export_model_elasticcrosssection(self, model, errors, simdata, simops):
        if model == ElasticCrossSectionModel.MOTT_CZYZEWSKI1990:
            value = CROSS_SECTION_MOTT_JOY
        elif model == ElasticCrossSectionModel.MOTT_DROUIN1993:
            value = CROSS_SECTION_MOTT_EQUATION
        elif model == ElasticCrossSectionModel.MOTT_BROWNING1994:
            value = CROSS_SECTION_MOTT_BROWNING
        elif model == ElasticCrossSectionModel.RUTHERFORD:
            value = CROSS_SECTION_MOTT_RUTHERFORD
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setElasticCrossSectionType(value)

    def _export_model_ionizationcrosssection(self, model, errors, simdata, simops):
        if model == IonizationCrossSectionModel.GAUVIN:
            value = IONIZATION_CROSS_SECTION_GAUVIN
        elif model == IonizationCrossSectionModel.POUCHOU1996:
            value = IONIZATION_CROSS_SECTION_POUCHOU
        elif model == IonizationCrossSectionModel.BROWN_POWELL:
            value = IONIZATION_CROSS_SECTION_BROWN_POWELL
        elif model == IonizationCrossSectionModel.CASNATI1982:
            value = IONIZATION_CROSS_SECTION_CASNATI
        elif model == IonizationCrossSectionModel.GRYZINSKY:
            value = IONIZATION_CROSS_SECTION_GRYZINSKI
        elif model == IonizationCrossSectionModel.JAKOBY:
            value = IONIZATION_CROSS_SECTION_JAKOBY
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setIonizationCrossSectionType(value)

    def _export_model_ionizationpotential(self, model, errors, simdata, simops):
        if model == IonizationPotentialModel.JOY_LUO1989:
            value = IONIZATION_POTENTIAL_JOY
        elif model == IonizationPotentialModel.BERGER_SELTZER1983:
            value = IONIZATION_POTENTIAL_BERGER
        elif model == IonizationPotentialModel.HOVINGTON:
            value = IONIZATION_POTENTIAL_HOVINGTON
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setIonizationPotentialType(value)

    def _export_model_randomnumbergenerator(self, model, errors, simdata, simops):
        if model == RandomNumberGeneratorModel.PRESS1996_RAND1:
            value = RANDOM_NUMBER_GENERATOR_PRESS_ET_AL
        elif model == RandomNumberGeneratorModel.MERSENNE:
            value = RANDOM_NUMBER_GENERATOR_MERSENNE_TWISTER
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setRandomNumberGeneratorType(value)

    def _export_model_directioncosine(self, model, errors, simdata, simops):
        if model == DirectionCosineModel.SOUM1979:
            value = DIRECTION_COSINES_SOUM
        elif model == DirectionCosineModel.DROUIN1996:
            value = DIRECTION_COSINES_DROUIN
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setDirectionCosines(value)

    def _export_model_energyloss(self, model, errors, simdata, simops):
        if model == EnergyLossModel.JOY_LUO1989:
            value = ENERGY_LOSS_JOY_LUO
        else:
            exc = ValueError('Unknown model: {0}'.format(model))
            errors.add(exc)
            return

        simops.setEnergyLossType(value)
