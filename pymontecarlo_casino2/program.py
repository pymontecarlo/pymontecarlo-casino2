""""""

__all__ = ["Casino2Program", "Casino2ProgramBuilder"]

# Standard library modules.
import os
import sys
import functools
import operator
import itertools

# Third party modules.

# Local modules.
import pymontecarlo.options.base as base
from pymontecarlo.options.program.base import ProgramBase, ProgramBuilderBase
from pymontecarlo.util.sysutil import is_64bits
from pymontecarlo.exceptions import ProgramNotFound
from pymontecarlo.options.model import (
    convert_models_document,
    ElasticCrossSectionModel,
    IonizationCrossSectionModel,
    IonizationPotentialModel,
    RandomNumberGeneratorModel,
    DirectionCosineModel,
    EnergyLossModel,
)

from pymontecarlo_casino2.expander import Casino2Expander
from pymontecarlo_casino2.exporter import Casino2Exporter
from pymontecarlo_casino2.importer import Casino2Importer
from pymontecarlo_casino2.worker import Casino2Worker

# Globals and constants variables.


class Casino2Program(ProgramBase):
    def __init__(
        self,
        number_trajectories=10000,
        elastic_cross_section_model=ElasticCrossSectionModel.MOTT_CZYZEWSKI1990,
        ionization_cross_section_model=IonizationCrossSectionModel.CASNATI1982,
        ionization_potential_model=IonizationPotentialModel.JOY_LUO1989,
        random_number_generator_model=RandomNumberGeneratorModel.PRESS1996_RAND1,
        direction_cosine_model=DirectionCosineModel.DROUIN1996,
        energy_loss_model=EnergyLossModel.JOY_LUO1989,
    ):
        super().__init__("Casino 2")

        self._expander = Casino2Expander()
        self._exporter = Casino2Exporter()
        self._importer = Casino2Importer()
        self._worker = Casino2Worker()

        self.number_trajectories = number_trajectories
        self.elastic_cross_section_model = elastic_cross_section_model
        self.ionization_cross_section_model = ionization_cross_section_model
        self.ionization_potential_model = ionization_potential_model
        self.random_number_generator_model = random_number_generator_model
        self.direction_cosine_model = direction_cosine_model
        self.energy_loss_model = energy_loss_model

    def __repr__(self):
        return "<{classname}({name}, {ntrajectories} trajectories)>".format(
            classname=self.__class__.__name__,
            name=self.name,
            ntrajectories=self.number_trajectories,
        )

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and base.isclose(self.number_trajectories, other.number_trajectories)
            and self.elastic_cross_section_model == other.elastic_cross_section_model
            and self.ionization_cross_section_model
            == other.ionization_cross_section_model
            and self.ionization_potential_model == other.ionization_potential_model
            and self.random_number_generator_model
            == other.random_number_generator_model
            and self.direction_cosine_model == other.direction_cosine_model
            and self.energy_loss_model == other.energy_loss_model
        )

    @property
    def expander(self):
        return self._expander

    @property
    def exporter(self):
        return self._exporter

    @property
    def worker(self):
        return self._worker

    @property
    def importer(self):
        return self._importer

    @property
    def executable(self):
        """
        Executable of Casino2, either wincasino2.exe on 32-bit system. or
        wincasino2_64.exe on 64-bit systems.

        Raises
            ProgramNotFound: if the executable cannot be found
        """
        basedir = os.path.abspath(os.path.dirname(__file__))
        casino2dir = os.path.join(basedir, "casino2")

        if not os.path.exists(casino2dir):
            raise ProgramNotFound("Casino 2 program cannot be found")

        if sys.platform == "darwin":  # Wine only works with 32-bit
            filename = "wincasino2.exe"
        else:
            filename = "wincasino2_64.exe" if is_64bits() else "wincasino2.exe"
        filepath = os.path.join(casino2dir, filename)

        if not os.path.exists(filepath):
            raise ProgramNotFound(
                "Cannot find {}. Installation might be corrupted.".format(filepath)
            )

        if os.path.getsize(filepath) < 1000000:  # < 1Mb
            raise ProgramNotFound(
                "{} is not the right file. Maybe Git LFS was not run.".format(filepath)
            )

        return filepath

    # region HDF5

    ATTR_NUMBER_TRAJECTORIES = "number trajectories"
    ATTR_ELASTIC_CROSS_SECTION_MODEL = "elastic cross section model"
    ATTR_IONIZATION_CROSS_SECTION_MODEL = "ionization cross section model"
    ATTR_IONIZATION_POTENTIAL_MODEL = "ionization potential model"
    ATTR_RANDOM_NUMBER_GENERATOR_MODEL = "random number generator model"
    ATTR_DIRECTION_COSINE_MODEL = "direction cosine model"
    ATTR_ENERGY_LOSS_MODEL = "energy loss model"

    @classmethod
    def parse_hdf5(cls, group):
        number_trajectories = cls._parse_hdf5(group, cls.ATTR_NUMBER_TRAJECTORIES, int)
        elastic_cross_section_model = cls._parse_hdf5(
            group, cls.ATTR_ELASTIC_CROSS_SECTION_MODEL, ElasticCrossSectionModel
        )
        ionization_cross_section_model = cls._parse_hdf5(
            group, cls.ATTR_IONIZATION_CROSS_SECTION_MODEL, IonizationCrossSectionModel
        )
        ionization_potential_model = cls._parse_hdf5(
            group, cls.ATTR_IONIZATION_POTENTIAL_MODEL, IonizationPotentialModel
        )
        random_number_generator_model = cls._parse_hdf5(
            group, cls.ATTR_RANDOM_NUMBER_GENERATOR_MODEL, RandomNumberGeneratorModel
        )
        direction_cosine_model = cls._parse_hdf5(
            group, cls.ATTR_DIRECTION_COSINE_MODEL, DirectionCosineModel
        )
        energy_loss_model = cls._parse_hdf5(
            group, cls.ATTR_ENERGY_LOSS_MODEL, EnergyLossModel
        )
        return cls(
            number_trajectories,
            elastic_cross_section_model,
            ionization_cross_section_model,
            ionization_potential_model,
            random_number_generator_model,
            direction_cosine_model,
            energy_loss_model,
        )

    def convert_hdf5(self, group):
        super().convert_hdf5(group)
        self._convert_hdf5(
            group, self.ATTR_NUMBER_TRAJECTORIES, self.number_trajectories
        )
        self._convert_hdf5(
            group,
            self.ATTR_ELASTIC_CROSS_SECTION_MODEL,
            self.elastic_cross_section_model,
        )
        self._convert_hdf5(
            group,
            self.ATTR_IONIZATION_CROSS_SECTION_MODEL,
            self.ionization_cross_section_model,
        )
        self._convert_hdf5(
            group, self.ATTR_IONIZATION_POTENTIAL_MODEL, self.ionization_potential_model
        )
        self._convert_hdf5(
            group,
            self.ATTR_RANDOM_NUMBER_GENERATOR_MODEL,
            self.random_number_generator_model,
        )
        self._convert_hdf5(
            group, self.ATTR_DIRECTION_COSINE_MODEL, self.direction_cosine_model
        )
        self._convert_hdf5(group, self.ATTR_ENERGY_LOSS_MODEL, self.energy_loss_model)

    # endregion

    # region Series

    def convert_series(self, builder):
        super().convert_series(builder)

        builder.add_column("number of trajectories", "ntraj", self.number_trajectories)
        builder.add_column(
            "elastic cross section model", "elastic", self.elastic_cross_section_model
        )
        builder.add_column(
            "ionization cross section model",
            "ionization",
            self.ionization_cross_section_model,
        )
        builder.add_column(
            "ionization potential model", "potential", self.ionization_potential_model
        )
        builder.add_column(
            "random number generator model",
            "random",
            self.random_number_generator_model,
        )
        builder.add_column(
            "direction cosine model", "cosine", self.direction_cosine_model
        )
        builder.add_column("energy loss model", "loss", self.energy_loss_model)

    # endregion

    # region Document

    def convert_document(self, builder):
        super().convert_document(builder)

        description = builder.require_description(self.DESCRIPTION_PROGRAM)
        description.add_item("Number of trajectories", self.number_trajectories)

        section = builder.add_section()
        section.add_title("Models")

        convert_models_document(
            builder,
            self.elastic_cross_section_model,
            self.ionization_cross_section_model,
            self.ionization_potential_model,
            self.random_number_generator_model,
            self.direction_cosine_model,
            self.energy_loss_model,
        )


# endregion


class Casino2ProgramBuilder(ProgramBuilderBase):
    def __init__(self):
        self.number_trajectories = set()
        self.elastic_cross_section_models = set()
        self.ionization_cross_section_models = set()
        self.ionization_potential_models = set()
        self.random_number_generator_models = set()
        self.direction_cosine_models = set()
        self.energy_loss_models = set()

    def __len__(self):
        it = [
            super().__len__(),
            len(self.number_trajectories) or 1,
            len(self.elastic_cross_section_models) or 1,
            len(self.ionization_cross_section_models) or 1,
            len(self.ionization_potential_models) or 1,
            len(self.random_number_generator_models) or 1,
            len(self.direction_cosine_models) or 1,
            len(self.energy_loss_models) or 1,
        ]
        return functools.reduce(operator.mul, it)

    def add_number_trajectories(self, number_trajectories):
        self.number_trajectories.add(number_trajectories)

    def add_elastic_cross_section_model(self, model):
        self.elastic_cross_section_models.add(model)

    def add_ionization_cross_section_model(self, model):
        self.ionization_cross_section_models.add(model)

    def add_ionization_potential_model(self, model):
        self.ionization_potential_models.add(model)

    def add_random_number_generator_model(self, model):
        self.random_number_generator_models.add(model)

    def add_direction_cosine_model(self, model):
        self.direction_cosine_models.add(model)

    def add_energy_loss_model(self, model):
        self.energy_loss_models.add(model)

    def build(self):
        default = Casino2Program()
        number_trajectories = self.number_trajectories or [default.number_trajectories]
        elastic_cross_section_models = self.elastic_cross_section_models or [
            default.elastic_cross_section_model
        ]
        ionization_cross_section_models = self.ionization_cross_section_models or [
            default.ionization_cross_section_model
        ]
        ionization_potential_models = self.ionization_potential_models or [
            default.ionization_potential_model
        ]
        random_number_generator_models = self.random_number_generator_models or [
            default.random_number_generator_model
        ]
        direction_cosine_models = self.direction_cosine_models or [
            default.direction_cosine_model
        ]
        energy_loss_models = self.energy_loss_models or [default.energy_loss_model]

        product = itertools.product(
            number_trajectories,
            elastic_cross_section_models,
            ionization_cross_section_models,
            ionization_potential_models,
            random_number_generator_models,
            direction_cosine_models,
            energy_loss_models,
        )

        programs = []
        for args in product:
            program = Casino2Program(*args)
            programs.append(program)

        return programs
