"""Tests for the myopic evolution_updater template module."""

import logging

import pytest

from temoa.extensions.myopic.evolution_updater import iterate
from temoa.extensions.myopic.myopic_index import MyopicIndex


def test_iterate_logs_base_year(caplog: pytest.LogCaptureFixture) -> None:
    idx = MyopicIndex(base_year=2020, step_year=2025, last_demand_year=2024, last_year=2030)

    with caplog.at_level(logging.INFO):
        iterate(idx=idx, prev_base_year=2015, last_instance_status='optimal', db_con=None)

    assert 'base year 2020' in caplog.text
