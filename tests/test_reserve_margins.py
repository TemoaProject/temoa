from __future__ import annotations

import contextlib
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pyomo.core.base.constraint import ConstraintData

    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel

    type ReserveRun = tuple[UnitCommitmentModel, Path]

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
def reserve_run(tmp_path_factory: pytest.TempPathFactory) -> ReserveRun:
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
    return cast('UnitCommitmentModel', instance), lp_files[0]


def test_planning_ab_group_includes_exchange(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for prm, r_g, t_g, p in model.planning_reserve_processes
        if prm == 'cap_AB'
        for r, _t, _v in model.planning_reserve_processes[prm, r_g, t_g, p]
        if '-' in r
    }
    assert all(r in exchange_regions for r in ['A-C', 'C-A', 'B-C', 'C-B']), (
        'Exchange regions A-C / C-A / B-C / C-B not auto-included in planning reserve group A+B'
    )


def test_single_region_a_includes_exchange(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for orm, r_g, t_g, p in model.operating_reserve_processes
        if orm == 'spin_A'
        for r, _t, _v in model.operating_reserve_processes[orm, r_g, t_g, p]
        if '-' in r
    }
    assert all(r in exchange_regions for r in ['A-C', 'C-A', 'B-A', 'A-B']), (
        'Exchange regions A-C / C-A / B-A / A-B not auto-included in operating reserve group A'
    )


def test_stacked_planning_reserves(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    con = model.planning_reserve_margin_constraint
    stacked = [
        (r_g, t_g, p, s, d)
        for prm, r_g, t_g, p, s, d in model.planning_reserve_nrtpsd
        if prm == 'cap_A'
    ]
    assert stacked
    for r_g, t_g, p, s, d in stacked:
        base = cast('ConstraintData', con['cap_A', r_g, t_g, p, s, d])
        derate = cast('ConstraintData', con['cap_A_derate', r_g, t_g, p, s, d])
        assert str(base.body) != str(derate.body), 'Stacked reserves should use their own data'


def test_online_headroom_only_for_credited_non_exchange(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    credited = {(orm, t) for orm, r, p, s, d, t, v in model.operating_reserve_online_nrpsdtv}
    assert credited == {
        ('spin_A', 'NGCC'),
        ('spin_A', 'SOLPV'),
        ('spin_A', 'E_BATT'),
        ('spin_A', 'E_LDES'),
        ('spin_A', 'E_TRANS'),
        ('reg_B', 'NGCC'),
        ('reg_B', 'E_BATT'),
        ('reg_B', 'E_TRANS'),
        ('spin_AB', 'NGCC'),
        ('spin_AB', 'SOLPV'),
        ('spin_AB', 'E_BATT'),
        ('spin_AB', 'E_LDES'),
        ('spin_AB', 'E_TRANS'),
    }, 'Online headroom should be indexed for every tech (incl. exchange) with a nonzero credit'


def test_storage_energy_requires_sustain_hours(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    products = {
        (orm, t) for orm, r_g, t_g, r, p, s, d, t, v in model.operating_reserve_storage_nrtrpsdtv
    }
    assert products == {
        ('spin_A', 'E_BATT'),
        ('spin_A', 'E_LDES'),
        ('spin_AB', 'E_BATT'),
        ('spin_AB', 'E_LDES'),
    }


def test_offline_credit_only_for_uc_techs(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    for orm, r_g, t_g, p, s, d in model.operating_reserve_nrtpsd:
        con = cast(
            'ConstraintData', model.operating_reserve_margin_constraint[orm, r_g, t_g, p, s, d]
        )
        body = str(con.body)
        assert ('v_uc_online' in body) == (orm == 'spin_AB'), (
            f'Offline UC credit should only appear in spin_AB, found mismatch in {orm}'
        )


def test_single_tech_region_a_not_includes_exchange(reserve_run: ReserveRun) -> None:
    model, _ = reserve_run
    exchange_regions = {
        r
        for prm, r_g, t_g, p in model.planning_reserve_processes
        if prm == 'cap_A'
        for r, t, v in model.planning_reserve_processes[prm, r_g, t_g, p]
        if '-' in r
    }
    assert not exchange_regions, (
        'Single-region planning margin on A should '
        f'not include exchange regions: {exchange_regions}'
    )


def test_lp_matches(reserve_run: ReserveRun) -> None:
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


def test_output_operating_reserve(tmp_path: Path) -> None:
    config = TemoaConfig.build_config(config_file=TEST_CONFIG, output_path=tmp_path, silent=True)
    TemoaSequencer(config=config).start()

    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        products = {
            row[0]
            for row in con.execute(
                'SELECT reserve FROM output_operating_reserve WHERE scenario = ?',
                (config.scenario,),
            )
        }
    assert products == {'spin_A_A_elec_A', 'reg_B_B_elec_B', 'spin_AB_A+B_elec_AB'}
