"""
Test some emissions and curtailment results for some basic technology archetypes

Written by:  Ian David Elder
iandavidelder@gmail.com
Created on:  2024/06/03

Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import sqlite3
from pathlib import Path

import pytest

from definitions import PROJECT_ROOT
from temoa.temoa_model.temoa_sequencer import TemoaSequencer

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def solved_connection(request, tmp_path_factory):
    """
    spin up the model, solve it, and hand over a connection to the results db
    """
    data_name = 'emissions'
    logger.info('Setting up and solving: %s', data_name)
    filename = 'config_emissions.toml'
    options = {'silent': True, 'debug': True}
    config_file = Path(PROJECT_ROOT, 'tests', 'testing_configs', filename)
    tmp_path = tmp_path_factory.mktemp('data')
    sequencer = TemoaSequencer(
        config_file=config_file,
        output_path=tmp_path,
        **options,
    )

    sequencer.start()
    # make connection here as in your code...
    con = sqlite3.connect(sequencer.config.output_database)
    yield con, request.param['name'], request.param['tech'], request.param['target']
    con.close()


# List of tech archetypes to test and their correct emission value
emissions_tests = [
    {'name': 'ordinary archetype', 'tech': 'TechOrdinary', 'target': 0.3},
    {'name': 'curtailment archetype', 'tech': 'TechCurtailment', 'target': 0.3},
    {'name': 'annual archetype', 'tech': 'TechAnnual', 'target': 1.0},
    {'name': 'flex archetype', 'tech': 'TechFlex', 'target': 1.0},
    {'name': 'annual flex archetype', 'tech': 'TechAnnualFlex', 'target': 1.0},
    {'name': 'total', 'tech': '%', 'target': 3.6},
]

embodied_tests = [
    {'name': 'embodied archetype', 'tech': 'TechEmbodied', 'target': 0.3},
]


# Emissions
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions(solved_connection):
    """
    Test that the emissions from each technology archetype are correct, and check total emissions
    """
    con, name, tech, emis_target = solved_connection
    emis = (
        con.cursor()
        .execute(f"SELECT SUM(emission) FROM main.OutputEmission WHERE tech LIKE '{tech}' AND tech != 'TechEmbodied'")
        .fetchone()[0]
    )
    assert emis == pytest.approx(
        emis_target
    ), f'{name} emissions were incorrect. Should be {emis_target}, got {emis}'


# Emission costs undiscounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions_costs_undiscounted(solved_connection):
    """
    Test that the undiscounted emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(f"SELECT SUM(emiss) FROM main.OutputCost WHERE tech LIKE '{tech}' AND tech != 'TechEmbodied'")
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target * 5  # emission cost x emissions x 5y
    assert ec == pytest.approx(
        cost_target
    ), f'{name} undiscounted emission costs were incorrect. Should be {cost_target}, got {ec}'


# Emission costs discounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=emissions_tests,
    indirect=True,
    ids=[t['name'] for t in emissions_tests],
)
def test_emissions_costs_discounted(solved_connection):
    """
    Test that the discounted emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(f"SELECT SUM(d_emiss) FROM main.OutputCost WHERE tech LIKE '{tech}' AND tech != 'TechEmbodied'")
        .fetchone()[0]
    )
    cost_target = (
        0.7 * emis_target * 4.32947667063082 * 1.05
    )  # emission cost x emissions x P/A(5%, 5y, 1) [x F/P(5%, 1y) legacy bug?]
    assert ec == pytest.approx(
        cost_target
    ), f'{name} discounted emission costs were incorrect. Should be {cost_target}, got {ec}'


# Embodied emissions
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions(solved_connection):
    """
    Test that the embodied emissions from each technology archetype are correct, and check total emissions
    """
    con, name, tech, emis_target = solved_connection
    emis = (
        con.cursor()
        .execute(f"SELECT SUM(emission) FROM main.OutputEmission WHERE tech LIKE '{tech}'")
        .fetchone()[0]
    )
    assert emis == pytest.approx(
        emis_target
    ), f'{name} embodied emissions were incorrect. Should be {emis_target}, got {emis}'


# Embodied emission costs undiscounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions_costs_undiscounted(solved_connection):
    """
    Test that the undiscounted embodied emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(f"SELECT SUM(emiss) FROM main.OutputCost WHERE tech LIKE '{tech}'")
        .fetchone()[0]
    )
    cost_target = 0.7 * emis_target  # emission cost x embodied emissions
    assert ec == pytest.approx(
        cost_target
    ), f'{name} undiscounted embodied emission costs were incorrect. Should be {cost_target}, got {ec}'


# Embodied emission costs discounted
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=embodied_tests,
    indirect=True,
    ids=[t['name'] for t in embodied_tests],
)
def test_embodied_emissions_costs_discounted(solved_connection):
    """
    Test that discounted embodied emission costs from each technology archetype are correct
    """
    con, name, tech, emis_target = solved_connection
    ec = (
        con.cursor()
        .execute(f"SELECT SUM(d_emiss) FROM main.OutputCost WHERE tech LIKE '{tech}'")
        .fetchone()[0]
    )
    cost_target = (
        0.7 * emis_target / 1.05 * 1.05
    )  # emission cost x embodied emissions x P/A(5%, 1y, 1) [x F/P(5%, 1y) legacy bug?]
    assert ec == pytest.approx(
        cost_target
    ), f'{name} discounted emission costs were incorrect. Should be {cost_target}, got {ec}'


# Curtailment
# List of tech archetypes to test and their correct curtailment value
curtailment_tests = [
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
def test_curtailment(solved_connection):
    con, name, tech, curt_target = solved_connection
    print(name, tech, curt_target)
    curt = (
        con.cursor()
        .execute(f"SELECT SUM(curtailment) FROM main.OutputCurtailment WHERE tech LIKE '{tech}'")
        .fetchone()[0]
    )
    assert curt == pytest.approx(
        curt_target
    ), f'{name} curtailment was incorrect. Should be {curt_target}, got {curt}'
