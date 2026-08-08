from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

import pytest

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from tests.utilities.compare_lp import LpDiff, compare_lp_files

logger = logging.getLogger(__name__)

TEST_CONFIG = Path(__file__).parent / 'testing_configs' / 'config_reserve_margins.toml'
CACHED_LP = Path(__file__).parent / 'testing_data' / 'reserve_margins.lp'


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope='module')
def reserve_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[TemoaModel, Path]:
    """Build, solve, and return (model, lp_path) for the reserve_margins scenario."""
    tmp = tmp_path_factory.mktemp('reserve_margins')
    config = TemoaConfig.build_config(
        config_file=TEST_CONFIG,
        output_path=tmp,
        silent=True,
    )
    config.save_lp_file = True

    seq = TemoaSequencer(config=config, mode_override=TemoaMode.BUILD_ONLY)
    instance = seq.build_model()

    lp_files = list(tmp.glob('*.lp'))
    assert lp_files, 'No LP file was written to the output directory'
    return instance, lp_files[0]


def test_planning_ab_group_includes_exchange(reserve_run: tuple[TemoaModel, Path]) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for r_g, p, t_g in model.planning_reserve_processes
        if r_g == 'A+B'
        for r, t, v in model.planning_reserve_processes[r_g, p, t_g]
        if '-' in r
    }
    assert all(r in exchange_regions for r in ['A-C', 'C-A', 'B-C', 'C-B']), (
        'Exchange regions A-C / C-A / B-C / C-B not auto-included in planning reserve group A+B'
    )


def test_single_region_a_includes_exchange(reserve_run: tuple[TemoaModel, Path]) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for r_g, p, t_g in model.operating_reserve_processes
        if r_g == 'A' and t_g == 'elec_A'
        for r, t, v in model.operating_reserve_processes[r_g, p, t_g]
        if '-' in r
    }
    assert all(r in exchange_regions for r in ['A-C', 'C-A', 'B-A', 'A-B']), (
        'Exchange regions A-C / C-A / B-A / A-B not auto-included in operating reserve group A'
    )


def test_single_tech_region_a_not_includes_exchange(reserve_run: tuple[TemoaModel, Path]) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for r_g, p, t_g in model.planning_reserve_processes
        if r_g == 'A' and t_g == 'NGCC'
        for r, t, v in model.planning_reserve_processes[r_g, p, t_g]
        if '-' in r
    }
    assert not exchange_regions, (
        'Single-region planning margin on A should '
        f'not include exchange regions: {exchange_regions}'
    )


def test_lp_matches(reserve_run: tuple[TemoaModel, Path]) -> None:
    _, lp_path = reserve_run

    if not CACHED_LP.exists():
        import shutil

        shutil.copy(lp_path, CACHED_LP)
        pytest.skip(
            f'No cached LP found — saved current output as new cache: {CACHED_LP}. '
            'Re-run the test to validate against it.'
        )

    diff: LpDiff = compare_lp_files(CACHED_LP, lp_path)
    assert diff.is_identical, f'LP file differs from cached ({CACHED_LP.name}):\n{diff.summary()}'
