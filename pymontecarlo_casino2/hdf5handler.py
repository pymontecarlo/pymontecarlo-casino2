""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.hdf5.options.program.base import ProgramHDF5HandlerBase

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramHDF5Handler(ProgramHDF5HandlerBase):

    ATTR_NUMBER_TRAJECTORIES = 'number'
    ATTR_ELASTIC_CROSS_SECTION_MODEL = 'elastic_cross_section_model'
    ATTR_IONIZATION_CROSS_SECTION_MODEL = 'ionization_cross_section_model'
    ATTR_IONIZATION_POTENTIAL_MODEL = 'ionization_potential_model'
    ATTR_RANDOM_NUMBER_GENERATOR_MODEL = 'random_number_generator_model'
    ATTR_DIRECTION_COSINE_MODEL = 'direction_cosine_model'
    ATTR_ENERGY_LOSS_MODEL = 'energy_loss_model'

    def _parse_number_trajectories(self, group):
        return int(group.attrs[self.ATTR_NUMBER_TRAJECTORIES])

    def _parse_elastic_cross_section_model(self, group):
        ref_model = group.attrs[self.ATTR_ELASTIC_CROSS_SECTION_MODEL]
        return self._parse_model_internal(group, ref_model)

    def _parse_ionization_cross_section_model(self, group):
        ref_model = group.attrs[self.ATTR_IONIZATION_CROSS_SECTION_MODEL]
        return self._parse_model_internal(group, ref_model)

    def _parse_ionization_potential_model(self, group):
        ref_model = group.attrs[self.ATTR_IONIZATION_POTENTIAL_MODEL]
        return self._parse_model_internal(group, ref_model)

    def _parse_random_number_generator_model(self, group):
        ref_model = group.attrs[self.ATTR_RANDOM_NUMBER_GENERATOR_MODEL]
        return self._parse_model_internal(group, ref_model)

    def _parse_direction_cosine_model(self, group):
        ref_model = group.attrs[self.ATTR_DIRECTION_COSINE_MODEL]
        return self._parse_model_internal(group, ref_model)

    def _parse_energy_loss_model(self, group):
        ref_model = group.attrs[self.ATTR_ENERGY_LOSS_MODEL]
        return self._parse_model_internal(group, ref_model)

    def parse(self, group):
        program = super().parse(group)
        program.number_trajectories = self._parse_number_trajectories(group)
        program.elastic_cross_section_model = self._parse_elastic_cross_section_model(group)
        program.ionization_cross_section_model = self._parse_ionization_cross_section_model(group)
        program.ionization_potential_model = self._parse_ionization_potential_model(group)
        program.random_number_generator_model = self._parse_random_number_generator_model(group)
        program.direction_cosine_model = self._parse_direction_cosine_model(group)
        program.energy_loss_model = self._parse_energy_loss_model(group)
        return program

    def _convert_number_trajectories(self, number_trajectories, group):
        group.attrs[self.ATTR_NUMBER_TRAJECTORIES] = number_trajectories

    def _convert_elastic_cross_section_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_ELASTIC_CROSS_SECTION_MODEL] = group_model.ref

    def _convert_ionization_cross_section_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_IONIZATION_CROSS_SECTION_MODEL] = group_model.ref

    def _convert_ionization_potential_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_IONIZATION_POTENTIAL_MODEL] = group_model.ref

    def _convert_random_number_generator_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_RANDOM_NUMBER_GENERATOR_MODEL] = group_model.ref

    def _convert_direction_cosine_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_DIRECTION_COSINE_MODEL] = group_model.ref

    def _convert_energy_loss_model(self, model, group):
        group_model = self._convert_model_internal(model, group)
        group.attrs[self.ATTR_ENERGY_LOSS_MODEL] = group_model.ref

    def convert(self, program, group):
        super().convert(program, group)
        self._convert_number_trajectories(program.number_trajectories, group)
        self._convert_elastic_cross_section_model(program.elastic_cross_section_model, group)
        self._convert_ionization_cross_section_model(program.ionization_cross_section_model, group)
        self._convert_ionization_potential_model(program.ionization_potential_model, group)
        self._convert_random_number_generator_model(program.random_number_generator_model, group)
        self._convert_direction_cosine_model(program.direction_cosine_model, group)
        self._convert_energy_loss_model(program.energy_loss_model, group)

    @property
    def CLASS(self):
        return Casino2Program
