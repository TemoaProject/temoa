"""Tests for MyopicProgressMapper, the console progress visualizer for myopic solves."""

import re

import pytest

from temoa.extensions.myopic.myopic_index import MyopicIndex
from temoa.extensions.myopic.myopic_progress_mapper import MyopicProgressMapper

YEARS = [2020, 2025, 2030, 2035]


def _index(base_year: int, step_year: int, last_demand_year: int) -> MyopicIndex:
    return MyopicIndex(
        base_year=base_year,
        step_year=step_year,
        last_demand_year=last_demand_year,
        last_year=YEARS[-1] + 1,
    )


def test_init_computes_tag_width_and_positions() -> None:
    mapper = MyopicProgressMapper(YEARS)

    assert mapper.years == YEARS
    assert mapper.tag_width == max(len(str(y)) for y in YEARS) + 2 * len(mapper.leader)
    # Positions are in increasing order, one per year.
    assert list(mapper.pos.keys()) == YEARS
    assert all(mapper.pos[YEARS[i]] < mapper.pos[YEARS[i + 1]] for i in range(len(YEARS) - 1))


def test_draw_header_prints_years_and_label(capsys: pytest.CaptureFixture[str]) -> None:
    mapper = MyopicProgressMapper(YEARS)
    mapper.draw_header()

    out = capsys.readouterr().out
    assert 'Myopic  Progress' in out
    assert 'HH:MM:SS' in out
    for year in YEARS:
        assert str(year) in out


def test_timestamp_format() -> None:
    mapper = MyopicProgressMapper(YEARS)
    assert re.match(r'^Elapsed: \d{2}:\d{2}:\d{2}\s+$', mapper.timestamp())


@pytest.mark.parametrize(
    'status,tag',
    [
        ('load', 'LOAD'),
        ('solve', 'SOLV'),
        ('check', 'CHEK'),
        ('evolve', 'EVLV'),
    ],
)
def test_report_prints_expected_tag_for_status(
    capsys: pytest.CaptureFixture[str], status: str, tag: str
) -> None:
    mapper = MyopicProgressMapper(YEARS)
    idx = _index(base_year=2020, step_year=2025, last_demand_year=2025)

    mapper.report(idx, status)  # type: ignore[arg-type]

    out = capsys.readouterr().out
    # One tag per year from base_year through last_demand_year (2020, 2025).
    assert out.count(tag) == 2
    assert 'Elapsed:' in out


def test_report_status_report_uses_step_year(capsys: pytest.CaptureFixture[str]) -> None:
    mapper = MyopicProgressMapper(YEARS)
    idx = _index(base_year=2020, step_year=2030, last_demand_year=2025)

    mapper.report(idx, 'report')

    out = capsys.readouterr().out
    # One tag per year from base_year up to (not including) step_year: 2020, 2025.
    assert out.count('RECD') == 2


def test_report_rejects_invalid_status() -> None:
    mapper = MyopicProgressMapper(YEARS)
    idx = _index(base_year=2020, step_year=2025, last_demand_year=2025)

    with pytest.raises(ValueError, match='bad status'):
        mapper.report(idx, 'bogus')  # type: ignore[arg-type]
