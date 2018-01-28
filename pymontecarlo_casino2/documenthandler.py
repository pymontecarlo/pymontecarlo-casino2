""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo.formats.document.options.program.base import ProgramDocumentHandlerBase

from pymontecarlo_casino2.program import Casino2Program

# Globals and constants variables.

class Casino2ProgramDocumentHandler(ProgramDocumentHandlerBase):

    def convert(self, program, builder):
        super().convert(program, builder)

        description = builder.require_description('program')
        description.add_item('Number of trajectories', program.number_trajectories)

        section = builder.add_section()
        section.add_title('Models')
        section.add_object(program.elastic_cross_section_model)
        section.add_object(program.ionization_cross_section_model)
        section.add_object(program.ionization_potential_model)
        section.add_object(program.random_number_generator_model)
        section.add_object(program.direction_cosine_model)
        section.add_object(program.energy_loss_model)

    @property
    def CLASS(self):
        return Casino2Program