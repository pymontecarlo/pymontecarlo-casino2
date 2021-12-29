""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pymontecarlo_gui.widgets.field import MultiValueFieldBase
from pymontecarlo_gui.widgets.lineedit import ColoredMultiFloatLineEdit
from pymontecarlo_gui.options.program.base import ProgramFieldBase
from pymontecarlo_gui.options.model.elastic_cross_section import (
    ElasticCrossSectionModelField,
)
from pymontecarlo_gui.options.model.ionization_cross_section import (
    IonizationCrossSectionModelField,
)
from pymontecarlo_gui.options.model.ionization_potential import (
    IonizationPotentialModelField,
)
from pymontecarlo_gui.options.model.random_number_generator import (
    RandomNumberGeneratorModelField,
)
from pymontecarlo_gui.options.model.direction_cosine import DirectionCosineModelField
from pymontecarlo_gui.options.model.energy_loss import EnergyLossModelField

from pymontecarlo_casino2.program import Casino2Program, Casino2ProgramBuilder
from pymontecarlo_casino2.exporter import (
    ELASTIC_CROSS_SECTION_MODEL_LOOKUP,
    IONIZATION_CROSS_SECTION_MODEL_LOOKUP,
    IONIZATION_POTENTIAL_MODEL_LOOKUP,
    RANDOM_NUMBER_GENERATOR_MODEL_LOOKUP,
    DIRECTION_COSINES_MODEL_LOOKUP,
    ENERGY_LOSS_MODEL_LOOKUP,
)

# Globals and constants variables.


class NumberTrajectoriesField(MultiValueFieldBase):
    def __init__(self):
        super().__init__()

        # widgets
        self._widget = ColoredMultiFloatLineEdit()
        self._widget.setRange(25, 1e9, 0)
        self._widget.setValues([10000])

        # Signals
        self._widget.valuesChanged.connect(self.fieldChanged)

    def title(self):
        return "Number of trajectories"

    def widget(self):
        return self._widget

    def numbersTrajectories(self):
        return self._widget.values()

    def setNumbersTrajectories(self, numbers_trajectories):
        self._widget.setValues(numbers_trajectories)


class Casino2ProgramField(ProgramFieldBase):
    def __init__(self, model):
        super().__init__(model)

        self.field_number_trajectories = NumberTrajectoriesField()
        self.addLabelField(self.field_number_trajectories)

        default_program = Casino2Program()

        self.field_elastic_cross_section_model = ElasticCrossSectionModelField()
        for model in ELASTIC_CROSS_SECTION_MODEL_LOOKUP:
            checked = model == default_program.elastic_cross_section_model
            self.field_elastic_cross_section_model.addModel(model, checked)
        self.addGroupField(self.field_elastic_cross_section_model)

        self.field_ionization_cross_section_model = IonizationCrossSectionModelField()
        for model in IONIZATION_CROSS_SECTION_MODEL_LOOKUP:
            checked = model == default_program.ionization_cross_section_model
            self.field_ionization_cross_section_model.addModel(model, checked)
        self.addGroupField(self.field_ionization_cross_section_model)

        self.field_ionization_potential_model = IonizationPotentialModelField()
        for model in IONIZATION_POTENTIAL_MODEL_LOOKUP:
            checked = model == default_program.ionization_potential_model
            self.field_ionization_potential_model.addModel(model, checked)
        self.addGroupField(self.field_ionization_potential_model)

        self.field_random_number_generator_model = RandomNumberGeneratorModelField()
        for model in RANDOM_NUMBER_GENERATOR_MODEL_LOOKUP:
            checked = model == default_program.random_number_generator_model
            self.field_random_number_generator_model.addModel(model, checked)
        self.addGroupField(self.field_random_number_generator_model)

        self.field_direction_cosine_model = DirectionCosineModelField()
        for model in DIRECTION_COSINES_MODEL_LOOKUP:
            checked = model == default_program.direction_cosine_model
            self.field_direction_cosine_model.addModel(model, checked)
        self.addGroupField(self.field_direction_cosine_model)

        self.field_energy_loss_model = EnergyLossModelField()
        for model in ENERGY_LOSS_MODEL_LOOKUP:
            checked = model == default_program.energy_loss_model
            self.field_energy_loss_model.addModel(model, checked)
        self.addGroupField(self.field_energy_loss_model)

    def title(self):
        return "Casino 2"

    def description(self):
        return "Version 2.5.0\nCopyright 1997-2017: Drouin, Couture, Gauvin, Hovington, Horney, Demers, Joly, Drouin and Poirier-Demers"

    def programs(self):
        builder = Casino2ProgramBuilder()

        for number_trajectories in self.field_number_trajectories.numbersTrajectories():
            builder.add_number_trajectories(number_trajectories)

        for model in self.field_elastic_cross_section_model.selectedModels():
            builder.add_elastic_cross_section_model(model)

        for model in self.field_ionization_cross_section_model.selectedModels():
            builder.add_ionization_cross_section_model(model)

        for model in self.field_ionization_potential_model.selectedModels():
            builder.add_ionization_potential_model(model)

        for model in self.field_random_number_generator_model.selectedModels():
            builder.add_random_number_generator_model(model)

        for model in self.field_direction_cosine_model.selectedModels():
            builder.add_direction_cosine_model(model)

        for model in self.field_energy_loss_model.selectedModels():
            builder.add_energy_loss_model(model)

        return super().programs() + builder.build()
