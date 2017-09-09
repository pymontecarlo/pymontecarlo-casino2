""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.series.options.program.base import ProgramSeriesHandler

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramSeriesHandler(ProgramSeriesHandler):

    def convert(self, program, builder):
        super().convert(program, builder)

        builder.add_column('number of trajectories', 'ntraj', program.number_trajectories)
        builder.add_object(program.elastic_cross_section_model)
        builder.add_object(program.ionization_cross_section_model)
        builder.add_object(program.ionization_potential_model)
        builder.add_object(program.random_number_generator_model)
        builder.add_object(program.direction_cosine_model)
        builder.add_object(program.energy_loss_model)

    @property
    def CLASS(self):
        return Casino2Program
