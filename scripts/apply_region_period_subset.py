#!/usr/bin/env python3
"""
Strip a v4 Temoa SQLite DB down to a subset of regions and periods.

Written for the 26-zone US power-system DB (usp_26z_*) but should work on any
v4 Temoa DB that uses:
  - a single `region` column per table (with optional compound regions
    "A-B" for transmission and "A+B+..." for region groups),
  - a single `period` / `vintage` scheme,
  - fuel-price import techs named `import_{census_division}_reference_{fuel}`
    (if your fuel-tech naming is different, pass --fuel-census-division
    to match your convention or the fuel-pruning step will be a no-op).

Example (Texas, 2027 - 2045):
  python apply_region_period_subset.py \\
      --source ../data/usp_26z_base.sqlite \\
      --out    ../data/texasp_base.sqlite \\
      --regions TRE TREW \\
      --periods 2027 2030 2035 2040\\
      --horizon-boundary 2045 \\
      --fuel-census-division west_south_central \\
      --overwrite

Strategy:
  1. Copy source DB to out path.
  2. For every table that has a `region` column, delete rows where region is
     NOT in the keep-set AND is not a compound region whose endpoints/members
     are all in the keep-set.
  3. For every table with a `period` column, delete rows where period not in
     (2000, *future_keep). The existing-vintage placeholder period 2000 is
     always kept. In `time_period` itself we also keep the horizon boundary
     so the last optimized period gets a nonzero period_length.
  4. Drop process-level rows (via vintage) whose vintage is a future period
     we dropped.
  5. Drop fuel-price import techs for non-kept Census divisions.
  6. Drop orphan commodities (fuel commodities with no producer, demand-flag
     commodities with no rows in `demand`).
  7. Drop unused technologies (no remaining efficiency rows).
  8. VACUUM.

Only modifies the copy; source is untouched.

Requires: Python 3.9+, stdlib only.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
from pathlib import Path

# Tables that store per-region data where region may be a single region
# OR a compound region "A-B" (transmission) OR a "+-joined" regional group.
# We handle all three cases with `is_region_kept`.
REGION_TABLES: list[str] = []  # filled at runtime by introspection
PERIOD_TABLES: list[str] = []  # filled at runtime by introspection


FUEL_CENSUS_DIVISIONS = {
    'east_north_central',
    'east_south_central',
    'middle_atlantic',
    'mountain',
    'new_england',
    'pacific',
    'south_atlantic',
    'west_north_central',
    'west_south_central',
}


def introspect(conn: sqlite3.Connection) -> tuple[list[str], list[str]]:
    """Return (tables_with_region_col, tables_with_period_col)."""
    tables = [
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]
    region_tabs, period_tabs = [], []
    for t in tables:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")').fetchall()]
        if 'region' in cols:
            region_tabs.append(t)
        if 'period' in cols:
            period_tabs.append(t)
    return region_tabs, period_tabs


def make_region_filter(keep_regions: set[str]):
    """Return a function that decides whether a region string should be kept.

    Rules:
      - single region: kept iff in keep_regions
      - transmission pair 'A-B': kept iff BOTH A and B are in keep_regions
      - group 'A+B+...': kept iff ALL members are in keep_regions
    """

    def keep(region: str) -> bool:
        if region in keep_regions:
            return True
        if '+' in region:
            members = region.split('+')
            return all(m in keep_regions for m in members)
        if '-' in region:
            a, b = region.split('-', 1)
            return a in keep_regions and b in keep_regions
        return False

    return keep


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument(
        '--regions', nargs='+', required=True, help='Region codes to keep (e.g. TRE TREW)'
    )
    parser.add_argument(
        '--periods',
        type=int,
        nargs='+',
        required=True,
        help='Future periods to OPTIMIZE over (e.g. 2027 2030). '
        'Existing-vintage period 2000 is kept automatically.',
    )
    parser.add_argument(
        '--horizon-boundary',
        type=int,
        default=None,
        help='Horizon-boundary period for time_optimize math '
        '(e.g. 2035 so 2030 gets a nonzero period_length). '
        'Kept only in time_period table; all other tables are '
        'pruned to --periods only.',
    )
    parser.add_argument(
        '--fuel-census-division',
        default='west_south_central',
        help='Census division whose import_* fuel techs should be kept',
    )
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    if not args.source.exists():
        sys.exit(f'Source not found: {args.source}')
    if args.out.exists() and not args.overwrite:
        sys.exit(f'Output exists (use --overwrite): {args.out}')

    if args.fuel_census_division not in FUEL_CENSUS_DIVISIONS:
        sys.exit(f'Unknown fuel census division: {args.fuel_census_division}')

    keep_regions = set(args.regions)
    keep_future_periods = set(args.periods)
    keep_periods = keep_future_periods | {2000}  # always keep existing-vintage period
    # The horizon boundary is kept ONLY in time_period, not in data tables.
    boundary = args.horizon_boundary
    if boundary is not None and boundary in keep_future_periods:
        boundary = None  # already covered

    print(f'Source:  {args.source}')
    print(f'Target:  {args.out}')
    print(f'Regions: {sorted(keep_regions)}')
    print(f'Periods: {sorted(keep_future_periods)} (+ vintage period 2000)')
    print(f'Fuel census division kept: {args.fuel_census_division}')
    print()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    print(f'Copying source DB ({args.source.stat().st_size / 1e6:.0f} MB)...')
    shutil.copy2(args.source, args.out)

    conn = sqlite3.connect(args.out)
    conn.execute('PRAGMA foreign_keys = OFF')

    region_tabs, period_tabs = introspect(conn)
    is_region_kept = make_region_filter(keep_regions)

    # ---- 1. Sanity: verify regions and periods exist in source ----
    src_regions = {r[0] for r in conn.execute('SELECT region FROM region').fetchall()}
    missing = keep_regions - src_regions
    if missing:
        sys.exit(f'Regions not found in source: {sorted(missing)}')

    src_periods = {r[0] for r in conn.execute('SELECT period FROM time_period').fetchall()}
    missing_p = keep_future_periods - src_periods
    if missing_p:
        sys.exit(f'Periods not found in source: {sorted(missing_p)}')

    # ---- 2. Prune regions across all tables with a `region` column ----
    print('=== Region pruning ===')
    total_deleted = 0
    for tab in region_tabs:
        regions_in_tab = [
            r[0] for r in conn.execute(f'SELECT DISTINCT region FROM "{tab}"').fetchall()
        ]
        drop = [r for r in regions_in_tab if not is_region_kept(r)]
        if not drop:
            continue
        before = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        # Delete in chunks of placeholders
        placeholders = ','.join('?' * len(drop))
        conn.execute(f'DELETE FROM "{tab}" WHERE region IN ({placeholders})', drop)
        after = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        deleted = before - after
        total_deleted += deleted
        print(f'  {tab:<40} {before:>10,} -> {after:>10,}  (-{deleted:,})')
    conn.commit()
    print(f'  TOTAL region rows deleted: {total_deleted:,}')

    # ---- 3. Prune periods ----
    print('\n=== Period pruning ===')
    keep_periods_sql = ','.join('?' * len(keep_periods))
    keep_periods_list = sorted(keep_periods)
    total_deleted = 0
    for tab in period_tabs:
        if tab == 'time_period':
            # Handled below: remove non-kept rows but preserve schema
            continue
        before = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        conn.execute(
            f'DELETE FROM "{tab}" WHERE period NOT IN ({keep_periods_sql})',
            keep_periods_list,
        )
        after = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        deleted = before - after
        total_deleted += deleted
        if deleted:
            print(f'  {tab:<40} {before:>10,} -> {after:>10,}  (-{deleted:,})')
    # time_period itself: keep optimize periods AND horizon boundary
    keep_time_period = set(keep_periods)
    if boundary is not None:
        keep_time_period.add(boundary)
    tp_sql = ','.join('?' * len(keep_time_period))
    tp_list = sorted(keep_time_period)
    before = conn.execute('SELECT COUNT(*) FROM time_period').fetchone()[0]
    conn.execute(
        f'DELETE FROM time_period WHERE period NOT IN ({tp_sql})',
        tp_list,
    )
    after = conn.execute('SELECT COUNT(*) FROM time_period').fetchone()[0]
    print(f'  {"time_period":<40} {before:>10,} -> {after:>10,}  (-{before - after:,})')
    # Re-sequence time_period
    for i, p in enumerate(
        sorted([r[0] for r in conn.execute('SELECT period FROM time_period').fetchall()]), start=1
    ):
        conn.execute('UPDATE time_period SET sequence = ? WHERE period = ?', (i, p))
    conn.commit()
    print(f'  TOTAL period rows deleted (excl. time_period): {total_deleted:,}')

    # ---- 4. Drop process-level rows where vintage is a future period we dropped ----
    print('\n=== Vintage pruning (future vintages outside kept periods) ===')
    # Tables with a vintage col
    vintage_tabs = []
    for t in [
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")').fetchall()]
        if 'vintage' in cols:
            vintage_tabs.append(t)

    keep_vintages_sql = ','.join('?' * len(keep_periods))
    total_deleted = 0
    for tab in vintage_tabs:
        before = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        conn.execute(
            f'DELETE FROM "{tab}" WHERE vintage NOT IN ({keep_vintages_sql})',
            keep_periods_list,
        )
        after = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
        deleted = before - after
        total_deleted += deleted
        if deleted:
            print(f'  {tab:<40} {before:>10,} -> {after:>10,}  (-{deleted:,})')
    conn.commit()
    print(f'  TOTAL vintage rows deleted: {total_deleted:,}')

    # ---- 5. Drop fuel-price import techs for non-kept census divisions ----
    print('\n=== Fuel import tech pruning ===')
    keep_div = args.fuel_census_division
    drop_divs = [d for d in FUEL_CENSUS_DIVISIONS if d != keep_div]
    # Find all import_{div}_reference_* techs
    import_techs_drop = set()
    for div in drop_divs:
        pat = f'import_{div}_reference_%'
        for (t,) in conn.execute(
            'SELECT tech FROM technology WHERE tech LIKE ?',
            (pat,),
        ).fetchall():
            import_techs_drop.add(t)
    print(f'  Fuel techs to drop (non-{keep_div}): {len(import_techs_drop)}')

    # Commodities produced by those techs — derive from naming pattern since
    # region pruning may have already deleted the efficiency rows for these
    # techs. Pattern: import_{div}_reference_{fuel} -> {div}_reference_{fuel}
    drop_fuel_commodities = set()
    for tech in import_techs_drop:
        assert tech.startswith('import_')
        drop_fuel_commodities.add(tech[len('import_') :])

    # Drop the techs from every table that references `tech`
    tech_tabs = []
    for t in [
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]:
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")').fetchall()]
        if 'tech' in cols:
            tech_tabs.append(t)

    if import_techs_drop:
        placeholders = ','.join('?' * len(import_techs_drop))
        tech_list = list(import_techs_drop)
        for tab in tech_tabs:
            before = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
            conn.execute(
                f'DELETE FROM "{tab}" WHERE tech IN ({placeholders})',
                tech_list,
            )
            after = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
            if before - after:
                print(f'  {tab:<40} -{before - after:,}')
        # Also remove from technology table
        conn.execute(
            f'DELETE FROM technology WHERE tech IN ({placeholders})',
            tech_list,
        )
    conn.commit()

    # ---- 6. Drop orphan commodities (no longer referenced by any tech) ----
    print('\n=== Orphan commodity pruning ===')
    # Union all commodity refs across relevant tables
    referenced = set()
    ref_queries = [
        'SELECT DISTINCT input_comm FROM efficiency WHERE input_comm IS NOT NULL',
        'SELECT DISTINCT output_comm FROM efficiency WHERE output_comm IS NOT NULL',
        'SELECT DISTINCT commodity FROM demand',
        'SELECT DISTINCT emis_comm FROM emission_activity',
    ]
    for q in ref_queries:
        for (c,) in conn.execute(q).fetchall():
            if c is not None:
                referenced.add(c)

    all_comms = {r[0] for r in conn.execute('SELECT name FROM commodity').fetchall()}
    orphans = all_comms - referenced
    # Only drop fuel-like commodities we no longer need. Keep ethos, DEMAND_*,
    # emission commodities like CO2, etc.
    # Any orphan whose flag is 'p' (physical) or 'd' (demand) and has no
    # producer/consumer is a loader error.
    # Drop any orphan fuel commodities (they were wired to non-TX regions only).
    safe_orphans = {c for c in orphans if c in drop_fuel_commodities}
    # Also drop any demand commodity with no demand rows at all (e.g., Dummy_CO2_Offset_Demand
    # whose producer techs only existed in non-TX regions).
    demand_commodities_with_data = {
        r[0] for r in conn.execute('SELECT DISTINCT commodity FROM demand').fetchall()
    }
    demand_orphans = {
        r[0] for r in conn.execute("SELECT name FROM commodity WHERE flag = 'd'").fetchall()
    } - demand_commodities_with_data
    safe_orphans |= demand_orphans
    # Also kill techs whose output commodity is one of these orphans
    if demand_orphans:
        placeholders_d = ','.join('?' * len(demand_orphans))
        orphan_techs = [
            r[0]
            for r in conn.execute(
                f'SELECT DISTINCT tech FROM efficiency WHERE output_comm IN ({placeholders_d})',
                list(demand_orphans),
            ).fetchall()
        ]
        for tab in tech_tabs:
            if not orphan_techs:
                break
            ph = ','.join('?' * len(orphan_techs))
            conn.execute(f'DELETE FROM "{tab}" WHERE tech IN ({ph})', orphan_techs)
        if orphan_techs:
            ph = ','.join('?' * len(orphan_techs))
            conn.execute(f'DELETE FROM technology WHERE tech IN ({ph})', orphan_techs)
    if safe_orphans:
        placeholders = ','.join('?' * len(safe_orphans))
        # Remove from any other tables referencing commodity by name (none critical
        # since we already dropped refs)
        conn.execute(
            f'DELETE FROM commodity WHERE name IN ({placeholders})',
            list(safe_orphans),
        )
        print(f'  Dropped {len(safe_orphans)} orphan fuel commodities')
    else:
        print('  No orphan fuel commodities to drop')
    conn.commit()

    # ---- 7. Drop unused technologies (not referenced in efficiency table) ----
    # Any tech left in `technology` but with no efficiency rows will fail
    # validate_used_efficiency_indices. Drop them and cascade through all
    # tech-referencing tables.
    used_techs = {r[0] for r in conn.execute('SELECT DISTINCT tech FROM efficiency').fetchall()}
    all_techs = {r[0] for r in conn.execute('SELECT tech FROM technology').fetchall()}
    unused = all_techs - used_techs
    if unused:
        placeholders = ','.join('?' * len(unused))
        ul = list(unused)
        for tab in tech_tabs:
            conn.execute(f'DELETE FROM "{tab}" WHERE tech IN ({placeholders})', ul)
        conn.execute(f'DELETE FROM technology WHERE tech IN ({placeholders})', ul)
        print(f'\n  Dropped {len(unused)} unused technologies (no efficiency rows)')

    # Clean up tech_group_member rows whose tech is gone
    conn.execute("""
        DELETE FROM tech_group_member
        WHERE tech NOT IN (SELECT tech FROM technology)
    """)
    # Drop empty tech groups
    conn.execute("""
        DELETE FROM tech_group
        WHERE group_name NOT IN (SELECT DISTINCT group_name FROM tech_group_member)
    """)
    conn.commit()

    # ---- 8. Summary / sanity check ----
    print('\n=== Summary ===')
    summary_tables = [
        'region',
        'time_period',
        'demand',
        'existing_capacity',
        'efficiency',
        'cost_variable',
        'technology',
        'limit_activity',
        'demand_specific_distribution',
    ]
    for tab in summary_tables:
        try:
            n = conn.execute(f'SELECT COUNT(*) FROM "{tab}"').fetchone()[0]
            print(f'  {tab:<30} {n:>10,}')
        except sqlite3.OperationalError:
            pass  # table not present in this DB

    try:
        eg_regions = [
            r[0] for r in conn.execute('SELECT DISTINCT region FROM existing_capacity').fetchall()
        ]
        print(f'  existing_capacity regions: {sorted(eg_regions)}')
    except sqlite3.OperationalError:
        pass

    # ---- 9. VACUUM ----
    print('\nVacuuming...')
    conn.execute('VACUUM')
    conn.close()
    print(f'\nDone. Output size: {os.path.getsize(args.out) / 1e6:.0f} MB')


if __name__ == '__main__':
    main()
