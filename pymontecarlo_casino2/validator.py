""""""

# Standard library modules.
import os

# Third party modules.

# Local modules.
from pymontecarlo.program.validator import Validator
from pymontecarlo.options.particle import Particle
from pymontecarlo.options.material import VACUUM
from pymontecarlo.options.beam import GaussianBeam
from pymontecarlo.options.sample import \
    SubstrateSample, HorizontalLayerSample, VerticalLayerSample
from pymontecarlo.options.limit import ShowersLimit
from pymontecarlo.options.model import \
    (ElasticCrossSectionModel, IonizationCrossSectionModel,
     IonizationPotentialModel, RandomNumberGeneratorModel,
     DirectionCosineModel, EnergyLossModel,)
from pymontecarlo.options.analysis import PhotonIntensityAnalysis, KRatioAnalysis

# Globals and constants variables.

class Casino2Validator(Validator):

    def __init__(self):
        super().__init__()

        self.beam_validate_methods[GaussianBeam] = self._validate_beam_gaussian

        self.sample_validate_methods[SubstrateSample] = self._validate_sample_substrate
        self.sample_validate_methods[HorizontalLayerSample] = self._validate_sample_horizontallayers
        self.sample_validate_methods[VerticalLayerSample] = self._validate_sample_verticallayers

        self.analysis_validate_methods[PhotonIntensityAnalysis] = self._validate_analysis_photonintensity
        self.analysis_validate_methods[KRatioAnalysis] = self._validate_analysis_kratio

        self.limit_validate_methods[ShowersLimit] = self._validate_limit_showers

        self.model_validate_methods[ElasticCrossSectionModel] = self._validate_model_valid_models
        self.model_validate_methods[IonizationCrossSectionModel] = self._validate_model_valid_models
        self.model_validate_methods[IonizationPotentialModel] = self._validate_model_valid_models
        self.model_validate_methods[RandomNumberGeneratorModel] = self._validate_model_valid_models
        self.model_validate_methods[DirectionCosineModel] = self._validate_model_valid_models
        self.model_validate_methods[EnergyLossModel] = self._validate_model_valid_models
        #self.model_validate_methods[MassAbsorptionCoefficientModel] = self._validate_model_valid_models
        #TODO: Validate MAC from Casino2

        self.valid_models[ElasticCrossSectionModel] = \
            (ElasticCrossSectionModel.MOTT_CZYZEWSKI1990,
             ElasticCrossSectionModel.MOTT_DROUIN1993,
             ElasticCrossSectionModel.MOTT_BROWNING1994,
             ElasticCrossSectionModel.RUTHERFORD)
        self.valid_models[IonizationCrossSectionModel] = \
            (IonizationCrossSectionModel.GAUVIN,
             IonizationCrossSectionModel.POUCHOU1996,
             IonizationCrossSectionModel.BROWN_POWELL,
             IonizationCrossSectionModel.CASNATI1982,
             IonizationCrossSectionModel.GRYZINSKY,
             IonizationCrossSectionModel.JAKOBY)
        self.valid_models[IonizationPotentialModel] = \
            (IonizationPotentialModel.JOY_LUO1989,
             IonizationPotentialModel.BERGER_SELTZER1983,
             IonizationPotentialModel.HOVINGTON)
        self.valid_models[RandomNumberGeneratorModel] = \
            (RandomNumberGeneratorModel.PRESS1996_RAND1,
             RandomNumberGeneratorModel.MERSENNE)
        self.valid_models[DirectionCosineModel] = \
            (DirectionCosineModel.SOUM1979,
             DirectionCosineModel.DROUIN1996)
        self.valid_models[EnergyLossModel] = (EnergyLossModel.JOY_LUO1989,)
        #self.valid_models[MassAbsorptionCoefficientModel] = ()

        self.default_models[ElasticCrossSectionModel] = ElasticCrossSectionModel.MOTT_CZYZEWSKI1990
        self.default_models[IonizationCrossSectionModel] = IonizationCrossSectionModel.CASNATI1982
        self.default_models[IonizationPotentialModel] = IonizationPotentialModel.JOY_LUO1989
        self.default_models[RandomNumberGeneratorModel] = RandomNumberGeneratorModel.PRESS1996_RAND1
        self.default_models[DirectionCosineModel] = DirectionCosineModel.DROUIN1996
        self.default_models[EnergyLossModel] = EnergyLossModel.JOY_LUO1989

    def _validate_program_executable(self, executable, options, errors):
        if not os.path.exists(executable):
            exc = ValueError("Specified executable ({}) does not exist"
                             .format(executable))
            errors.add(exc)

        if not os.access(executable, os.X_OK):
            exc = ValueError("Specified executable ({}) is not executable"
                             .format(executable))
            errors.add(exc)

        return executable

    def _validate_beam_base_energy_eV(self, energy_eV, options, errors):
        #NOTE: Casino does not seem to have an upper energy limit
        return super()._validate_beam_base_energy_eV(energy_eV, options, errors)

    def _validate_beam_base_particle(self, particle, options, errors):
        particle = super()._validate_beam_base_particle(particle, options, errors)

        if particle is not Particle.ELECTRON:
            exc = ValueError('Particle {0} is not supported. Only ELECTRON.'
                             .format(particle))
            errors.add(exc)

        return particle

    def _validate_beam_gaussian_y0_m(self, y0_m, options, errors):
        y0_m = super()._validate_beam_gaussian_y0_m(y0_m, options, errors)

        if y0_m != 0.0:
            exc = ValueError("Beam initial y position ({0:g}) must be 0.0"
                             .format(y0_m))
            errors.add(exc)

        return y0_m

    def _validate_beam_gaussian_azimuth_rad(self, azimuth_rad, options, errors):
        azimuth_rad = super()._validate_beam_gaussian_azimuth_rad(azimuth_rad, options, errors)

        if azimuth_rad != 0.0:
            exc = ValueError('Beam azimuth angle ({0:g}) must be 0.0'
                             .format(azimuth_rad))
            errors.add(exc)

        return azimuth_rad

    def _validate_sample_base_tilt_rad(self, tilt_rad, options, errors):
        tilt_rad = super()._validate_sample_base_tilt_rad(tilt_rad, options, errors)

        if tilt_rad != 0.0:
            exc = ValueError('Sample tilt is not supported.')
            errors.add(exc)

        return tilt_rad

    def _validate_sample_base_rotation_rad(self, rotation_rad, options, errors):
        rotation_rad = \
            super()._validate_sample_base_rotation_rad(rotation_rad, options, errors)

        if rotation_rad != 0.0:
            exc = ValueError('Sample rotation is not supported.')
            errors.add(exc)

        return rotation_rad

    def _validate_sample_layered_layers(self, layers, options, errors):
        layers = super()._validate_sample_layered_layers(layers, options, errors)

        for layer in layers:
            if layer.material is VACUUM:
                exc = ValueError('Layer with VACUUM material is not supported.')
                errors.add(exc)

        return layers

    def _validate_sample_horizontallayers_layers(self, layers, options, errors):
        layers = super()._validate_sample_horizontallayers_layers(layers, options, errors)

        if len(layers) > 5:
            exc = ValueError('Up to 5 layers is supported. {0:d} defined.'
                             .format(len(layers)))
            errors.add(exc)

        return layers

    def _validate_sample_verticallayers_layers(self, layers, options, errors):
        layers = super()._validate_sample_verticallayers_layers(layers, options, errors)

        if len(layers) > 11:
            exc = ValueError('Up to 11 layers is supported. {0:d} defined.'
                             .format(len(layers)))
            errors.add(exc)

        return layers

    def _validate_limit_showers_number_trajectories(self, showers, options, errors):
        number_trajectories = \
            super()._validate_limit_showers_number_trajectories(showers, options, errors)

        if number_trajectories < 25:
            exc = ValueError('Number of showers ({0:d}) must be greater or equal to 25.'
                             .format(number_trajectories))
            errors.add(exc)

        if number_trajectories > 1e9:
            exc = ValueError('Number of showers ({0:d}) must be less than 1e9.'
                             .format(number_trajectories))
            errors.add(exc)

        return number_trajectories
