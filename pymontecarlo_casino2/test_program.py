#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pymontecarlo.options.model.elastic_cross_section import ElasticCrossSectionModel
import pymontecarlo.util.testutil as testutil
from pymontecarlo.settings import Settings, XrayNotation
from pymontecarlo.formats.series import SeriesBuilder
from pymontecarlo.formats.document import DocumentBuilder

from pymontecarlo_casino2.program import Casino2Program, Casino2ProgramBuilder

# Globals and constants variables.


@pytest.fixture
def program():
    return Casino2Program()


@pytest.fixture
def settings():
    settings = Settings()
    settings.preferred_xray_notation = XrayNotation.IUPAC
    return settings


@pytest.fixture
def programbuilder():
    return Casino2ProgramBuilder()


def test_program_name(program):
    assert program.name == "Casino 2"


def test_program_hdf5(program, tmp_path):
    testutil.assert_convert_parse_hdf5(program, tmp_path)


def test_program_copy(program):
    testutil.assert_copy(program)


def test_program_pickle(program):
    testutil.assert_pickle(program)


def test_program_series(program, settings):
    seriesbuilder = SeriesBuilder(settings)
    program.convert_series(seriesbuilder)

    s = seriesbuilder.build()

    assert len(s) == 8
    assert s["program"] == program.name
    assert s["number of trajectories"] == 10000


def test_program_document(program, settings):
    documentbuilder = DocumentBuilder(settings)
    program.convert_document(documentbuilder)
    document = documentbuilder.build()
    assert testutil.count_document_nodes(document) == 6


def test_programbuilder(programbuilder):
    programs = programbuilder.build()
    assert len(programs) == 1


def test_programbuilder_two_trajectories_two_models(programbuilder):
    programbuilder.add_number_trajectories(100)
    programbuilder.add_number_trajectories(200)
    programbuilder.add_elastic_cross_section_model(ElasticCrossSectionModel.RUTHERFORD)
    programbuilder.add_elastic_cross_section_model(
        ElasticCrossSectionModel.MOTT_CZYZEWSKI1990
    )

    programs = programbuilder.build()

    assert len(programs) == 4
