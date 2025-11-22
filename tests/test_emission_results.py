"""
Test some emissions and curtailment results for some basic technology archetypes

"""

import logging
import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import TypedDict, cast

import pytest

# Import TemoaConfig, which is now needed to set up the sequencer
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig

logger = logging.getLogger(__name__)

type SolvedConnection = tuple[sqlite3.Connection, str, str, float]


# Define a TypedDict for the test parameters to provide better type hints
class TechTestParams(TypedDict):
    name: str
    tech: str
    target: float


@pytest.fixture(scope='module')
def solved_connection(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Generator[SolvedConnection, None, None]:
    """
    Spins up the model, solves it, and hands over a connection to the results db.
    This fixture is now updated to use the refactored TemoaSequencer API.
    """
    param = cast('TechTestParams', request.param)
    logger.info('Setting up and solving for test case: %s', param['name'])

    config_file = Path(__file__).parent / 'testing_configs' / 'config_emissions.toml'
    tmp_path = tmp_path_factory.mktemp('data')

    config = TemoaConfig.build_config(config_file=config_file, output_path=tmp_path, silent=True)
    sequencer = TemoaSequencer(config=config)

    # Step 3: Run the sequencer to completion.
    sequencer.start()

    con = sqlite3.connect(sequencer.config.output_database)
    try:
        yield con, param['name'], param['tech'], param['target']
    finally:
        con.close()


# List of tech archetypes to test and their correct emission value
emissions_tests: list[TechTestParams] = [
    {'name': 'ordinary archetype', 'tech': 'TechOrdinary', 'target': 0.3},
    {'name': 'curtailment archetype', 'tech': 'TechCurtailment', 'target': 0.3},
    {'name': 'annual archetype', 'tech': 'TechAnnual', 'target': 1.0},
    {'name': 'flex archetype', 'tech': 'TechFlex', 'target': 1.0},
    {'name': 'annual flex archetype', 'tech': 'TechAnnualFlex', 'target': 1.0},
    {'name': 'total', 'tech': '%', 'target': 3.6},
]
embodied_tests: list[TechTestParams] = [
    {'name': 'embodied archetype', 'tech': 'TechEmbodied', 'target': 0.3},
]
eol_tests: list[TechTestParams] = [
    {'name': 'end of life archetype', 'tech': 'TechEndOfLife', 'target': 0.3},
]


# Emissions
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions(solved_connection: SolvedConnection) -> None:
    """
    Test that the emissions from each technology archetype are correct, and check total emissions
    """
    con, name, tech, emis_target = solved_connection
    emis = (
        con.cursor()
        .execute(
            f"SELECT SUM(emission) FROM main.output_emission WHERE tech LIKE '{tech}' AND "
            f"tech != 'TechEmbodied' AND period == 2000"
        )
        .fetchone()[0]
    )
    assert emis == pytest.approx(emis_target), (
        f'{name} emissions were incorrect. Should be {emis_target}, got {emis}'
    )


# Emission costs undiscounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions_costs_undiscounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that the undiscounted emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND "
            f"tech != 'TechEmbodied' AND period == 2000"
        )
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target * 5  # emission cost x emissions x 5y
    assert ec == pytest.approx(cost_target), (
        f'{name} undiscounted emission costs were incorrect. Should be {cost_target}, got {ec}'
    )


# Emission costs discounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions_costs_discounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that the discounted emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(d_emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND "
            f"tech != 'TechEmbodied' AND period == 2000"
        )
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target * 4.32947667063082  # emission cost x emissions x P/A(5%, 5y, 1)
    assert ec == pytest.approx(cost_target), (
        f'{name} discounted emission costs were incorrect. Should be {cost_target}, got {ec}'
    )


# Embodied emissions
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions(solved_connection: SolvedConnection) -> None:
    """
    Test that the embodied emissions from each technology archetype are correct, and check total
    emissions
    """
    con, name, tech, emis_target = solved_connection
    emis = (
        con.cursor()
        .execute(
            f"SELECT SUM(emission) FROM main.output_emission WHERE tech LIKE '{tech}' AND "
            f'period == 2000'
        )
        .fetchone()[0]
    )
    assert emis == pytest.approx(
        emis_target / 5  # embodied emissions are distributed over vintage period
    ), f'{name} embodied emissions were incorrect. Should be {emis_target}, got {emis}'


# Embodied emission costs undiscounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions_costs_undiscounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that the undiscounted embodied emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND period == 2000"
        )
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target  # emission cost x embodied emissions
    assert ec == pytest.approx(cost_target), (
        f'{name} undiscounted embodied emission costs were incorrect. Should be {cost_target}, '
        f'got {ec}'
    )


# Embodied emission costs discounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions_costs_discounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that discounted embodied emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(d_emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND period == 2000"
        )
        .fetchone()[0]
    )
    cost_target = (
        0.7 * emis_target * 1 / 5 * (1.05**5 - 1) / (0.05 * 1.05**5)
    )  # emission cost x embodied emissions x annual distribution x P/A(5%, 5y, 1)
    assert ec == pytest.approx(cost_target), (
        f'{name} discounted emission costs were incorrect. Should be {cost_target}, got {ec}'
    )


# End of life emissions
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=eol_tests,
    indirect=True,
    ids=[t['name'] for t in eol_tests],
)
def test_endoflife_emissions(solved_connection: SolvedConnection) -> None:
    """
    Test that the end of life emissions from each technology archetype are correct, and check total
    emissions
    """
    con, name, tech, emis_target = solved_connection
    emis = (
        con.cursor()
        .execute(
            f"SELECT SUM(emission) FROM main.output_emission WHERE tech LIKE '{tech}' AND "
            f'period == 2005'
        )
        .fetchone()[0]
    )
    assert emis == pytest.approx(
        emis_target / 5  # end of life emissions are distributed over vintage period
    ), f'{name} end of life emissions were incorrect. Should be {emis_target}, got {emis}'


# End of life emission costs undiscounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=eol_tests,
    indirect=True,
    ids=[t['name'] for t in eol_tests],
)
def test_endoflife_emissions_costs_undiscounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that the undiscounted end of life emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND period == 2005"
        )
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target  # emission cost x end of life emissions
    assert ec == pytest.approx(cost_target), (
        f'{name} undiscounted end of life emission costs were incorrect. Should be {cost_target}, '
        f'got {ec}'
    )


# End of life emission costs discounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=eol_tests,
    indirect=True,
    ids=[t['name'] for t in eol_tests],
)
def test_endoflife_emissions_costs_discounted(
    solved_connection: SolvedConnection,
) -> None:
    """
    Test that discounted end of life emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(
            f"SELECT SUM(d_emiss) FROM main.output_cost WHERE tech LIKE '{tech}' AND period == 2005"
        )
        .fetchone()[0]
    )
    cost_target = (
        0.7 * emis_target * 1 / 5 * (1.05**5 - 1) / (0.05 * 1.05**5) / 1.05**5
    )  # emission cost x end of life emissions x annual distribution x P/A(5%, 5y, 1) x P/F(5%, 1y)
    assert ec == pytest.approx(cost_target), (
        f'{name} discounted emission costs were incorrect. Should be {cost_target}, got {ec}'
    )


# Curtailment
# List of tech archetypes to test and their correct curtailment value
curtailment_tests: list[TechTestParams] = [
    {'name': 'curtailment archetype', 'tech': 'TechCurtailment', 'target': 0.45},
    {'name': 'flex archetype', 'tech': 'TechFlex', 'target': 0.7},
    {'name': 'annual flex archetype', 'tech': 'TechAnnualFlex', 'target': 0.7},
    {'name': 'total', 'tech': '%', 'target': 1.85},
]


@pytest.mark.parametrize(
    'solved_connection',
    argvalues=curtailment_tests,
    indirect=True,
    ids=[t['name'] for t in curtailment_tests],
)
def test_curtailment(solved_connection: SolvedConnection) -> None:
    con, name, tech, curt_target = solved_connection
    logger.info('Curtailment test: %s %s target=%s', name, tech, curt_target)
    curt = (
        con.cursor()
        .execute(
            f"SELECT SUM(curtailment) FROM main.output_curtailment WHERE tech LIKE '{tech}' AND "
            f'period == 2000'
        )
        .fetchone()[0]
    )
    assert curt == pytest.approx(curt_target), (
        f'{name} curtailment was incorrect. Should be {curt_target}, got {curt}'
    )
