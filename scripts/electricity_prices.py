"""
Convert Temoa commodity-balance duals into electricity prices ($/MWh).

What the duals are (verified against temoa/components/commodities.py and costs.py):

* Electricity commodities (flag 'p', not annual, not waste) are balanced per
  (region, period, season, tod) by ``commodity_balance_constraint`` as an
  equality: produced == consumed.  (Annual commodities use
  ``annual_commodity_balance_constraint[r,p,c]``; waste commodities use >=.)
* Flows in a slice are energy over that slice for one representative year
  (capacity constraint: FO <= CF * C2A * SEG * CAP), so a dual is the change in
  the objective from one extra unit of energy consumed in that slice in every
  year of the period.  No division by segment fraction is needed.
* The objective (minimize) discounts annual costs in period p by
      DF_p = annuity_to_pv(GDR, LEN_p) * (1 + GDR) ** -(p - P0)
           = sum_{k=1..LEN_p} (1 + GDR) ** -(p - P0 + k)
  i.e. end-of-year convention (no mid-year), P0 = first optimized period
  (or myopic_discounting_year), LEN_p = next period - p, and the last
  period's length is set by the final 'f' row in time_period.
* With Pyomo's convention (dual = d obj / d rhs for body = produced - consumed),
  a positive dual is the marginal cost of serving more load, so no sign flip is
  needed.  The script checks this and warns if the sample looks flipped.
* Duals are stored raw (discounted objective units per commodity unit) in
  ``output_dual_variable(scenario, constraint_name, dual)``.

Usage:
    python scripts/electricity_prices.py temoa_power.sqlite [--commodity ELC ELCP]
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

# Multipliers to convert a commodity unit to MWh and a cost unit to dollars.
ENERGY_TO_MWH = {
    'PJ': 1e15 / 3.6e9,
    'TJ': 1e12 / 3.6e9,
    'GJ': 1 / 3.6,
    'TWH': 1e6,
    'GWH': 1e3,
    'MWH': 1.0,
}
COST_TO_USD = {
    'MUSD': 1e6,
    'M$': 1e6,
    'MDOLLAR': 1e6,
    'BUSD': 1e9,
    'KUSD': 1e3,
    'USD': 1.0,
    '$': 1.0,
}

NAME_RE = re.compile(r'^(?P<con>\w+)\[(?P<idx>.*)\]$')


def connect(path: Path) -> sqlite3.Connection:
    # immutable=1 lets us read WAL-mode databases without write access to the -shm file;
    # mode=ro stops sqlite from creating an empty file when the path is wrong
    if not path.is_file() or path.stat().st_size == 0:
        sys.exit(f'{path} does not exist or is empty.')
    return sqlite3.connect(f'file:{path}?mode=ro&immutable=1', uri=True)


def discount_factors(
    con: sqlite3.Connection, base_year: int | None
) -> tuple[pd.DataFrame, float, int]:
    row = con.execute(
        "SELECT value FROM metadata_real WHERE element = 'global_discount_rate'"
    ).fetchone()
    if row is None:
        sys.exit('global_discount_rate missing from metadata_real (Temoa requires it).')
    gdr = float(row[0])
    future = [
        r[0] for r in con.execute("SELECT period FROM time_period WHERE flag = 'f' ORDER BY period")
    ]
    p0 = base_year if base_year is not None else future[0]
    rows = []
    for p, p_next in zip(future[:-1], future[1:]):
        length = int(p_next - p)
        if gdr == 0:
            df = float(length)
        else:
            annuity = ((1 + gdr) ** length - 1) / (gdr * (1 + gdr) ** length)
            df = annuity / (1 + gdr) ** int(p - p0)
        rows.append({'period': p, 'period_length': length, 'discount_factor': df})
    return pd.DataFrame(rows), gdr, p0


def unit_conversion(
    con: sqlite3.Connection, commodity: str, cost_scale: float | None, energy_to_mwh: float | None
) -> tuple[float, str]:
    """Return multiplier taking (cost unit / commodity unit) to $/MWh."""
    c_units = con.execute('SELECT units FROM commodity WHERE name = ?', (commodity,)).fetchone()
    c_units = (c_units[0] or '').strip() if c_units else ''
    cost_units = con.execute(
        'SELECT units FROM output_cost WHERE units IS NOT NULL LIMIT 1'
    ).fetchone()
    cost_units = (cost_units[0] or '').strip() if cost_units else ''

    if energy_to_mwh is None:
        energy_to_mwh = ENERGY_TO_MWH.get(c_units.upper())
        if energy_to_mwh is None:
            sys.exit(f'Unknown energy unit {c_units!r} for {commodity}; pass --energy-to-mwh.')
    if cost_scale is None:
        cost_scale = COST_TO_USD.get(cost_units.upper().replace(' ', ''))
        if cost_scale is None:
            sys.exit(
                f'Unknown cost unit {cost_units!r}; pass --cost-scale (dollars per cost unit).'
            )
    note = f'{cost_units or "?"}/{c_units or "?"} -> $/MWh (x{cost_scale / energy_to_mwh:g})'
    return cost_scale / energy_to_mwh, note


def window_year(dual_scenario: str, scenario: str) -> int:
    """Myopic runs save each window's duals as '<scenario>-<base_year>'; perfect foresight uses
    '<scenario>' alone (treated as one window starting before every period)."""
    return -1 if dual_scenario == scenario else int(dual_scenario[len(scenario) + 1 :])


def load_duals(
    con: sqlite3.Connection, scenario: str, commodities: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (per-slice duals for the requested commodities, all commodity-balance duals).

    For myopic runs, each period's dual is taken from the latest window whose base year is
    <= that period: the window whose solution was kept in the output tables (later windows
    clear and rewrite results from their base year on, but output_dual_variable is never
    cleared, so look-ahead periods of earlier windows are still in it)."""
    raw = con.execute(
        'SELECT scenario, constraint_name, dual FROM output_dual_variable '
        "WHERE (scenario = ? OR scenario GLOB ? || '-[0-9][0-9][0-9][0-9]') "
        "AND (constraint_name LIKE 'commodity_balance_constraint[%' "
        "OR constraint_name LIKE 'annual_commodity_balance_constraint[%')",
        (scenario, scenario),
    ).fetchall()
    slice_rows, annual_rows = [], []
    for dual_scenario, name, dual in raw:
        w = window_year(dual_scenario, scenario)
        m = NAME_RE.match(name)
        idx = m['idx'].split(',')
        if m['con'] == 'commodity_balance_constraint':
            r, p, s, d, c = idx
            if w <= int(p):
                slice_rows.append((w, r, int(p), s, d, c, dual))
        else:
            r, p, c = idx
            if w <= int(p):
                annual_rows.append((w, r, int(p), c, dual))
    cols = ['window', 'region', 'period', 'season', 'tod', 'commodity', 'dual']
    all_slice = pd.DataFrame(slice_rows, columns=cols)
    all_slice = all_slice.sort_values('window').drop_duplicates(cols[1:6], keep='last')
    annual = pd.DataFrame(annual_rows, columns=['window', 'region', 'period', 'commodity', 'dual'])
    hit = annual[annual.commodity.isin(commodities)]
    if not hit.empty:
        print(
            f'NOTE: {sorted(hit.commodity.unique())} are annual commodities; '
            'their duals are annual-balance duals and are not per-slice.',
            file=sys.stderr,
        )
    return all_slice[all_slice.commodity.isin(commodities)].copy(), all_slice


def load_weights(con: sqlite3.Connection, scenario: str, commodities: list[str]) -> pd.DataFrame:
    """Energy consumed from the commodity node in each region/slice (excludes storage charging
    and exports, which are recorded under 'A-B' exchange regions)."""
    q = (
        'SELECT f.region, f.period, f.season, f.tod, f.input_comm AS commodity, SUM(f.flow) AS load '
        'FROM output_flow_in f JOIN technology t ON t.tech = f.tech '
        f'WHERE f.scenario = ? AND f.input_comm IN ({",".join("?" * len(commodities))}) '
        "AND t.flag NOT LIKE '%s%' AND f.input_comm != f.output_comm "
        'GROUP BY f.region, f.period, f.season, f.tod, f.input_comm'
    )
    return pd.read_sql_query(q, con, params=[scenario, *commodities])


def segment_fractions(con: sqlite3.Connection) -> pd.DataFrame:
    seasons = pd.read_sql_query(
        'SELECT season, segment_fraction AS sf_season FROM time_season', con
    )
    tods = pd.read_sql_query('SELECT tod, hours FROM time_of_day', con)
    tods['tod_frac'] = tods.hours / tods.hours.sum()
    seg = seasons.merge(tods[['tod', 'tod_frac']], how='cross')
    seg['segment_fraction'] = seg.sf_season * seg.tod_frac
    return seg[['season', 'tod', 'segment_fraction']]


def weighted(g: pd.DataFrame, w: str) -> float:
    tot = g[w].sum()
    return float((g.price * g[w]).sum() / tot) if tot > 0 else float('nan')


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument('database', type=Path)
    ap.add_argument('--scenario', help='scenario name (default: the only one with duals)')
    ap.add_argument(
        '--commodity', nargs='+', default=['ELC'], help='commodities to price (default ELC)'
    )
    ap.add_argument('--base-year', type=int, help='override P0 (default: first future period)')
    ap.add_argument(
        '--cost-scale', type=float, help='dollars per objective cost unit (default from units)'
    )
    ap.add_argument(
        '--energy-to-mwh', type=float, help='MWh per commodity unit (default from units)'
    )
    ap.add_argument(
        '--flip-sign', action='store_true', help='negate duals (only if your solver flips them)'
    )
    ap.add_argument('--spike', type=float, default=500.0, help='flag slice prices above this $/MWh')
    ap.add_argument('--out-dir', type=Path, default=Path('.'), help='where to write CSVs')
    args = ap.parse_args()

    con = connect(args.database)

    scenarios = [r[0] for r in con.execute('SELECT DISTINCT scenario FROM output_dual_variable')]
    if not scenarios:
        flows = [r[0] for r in con.execute('SELECT DISTINCT scenario FROM output_cost')]
        found = f'results exist for scenarios {flows}' if flows else 'no model results at all'
        sys.exit(
            f'output_dual_variable is empty in {args.database.name} ({found}). '
            'Run Temoa with save_duals = true and a solver that returns duals '
            '(e.g. gurobi; not appsi_highs), then run this script again.'
        )
    # strip myopic window suffixes ('-2020', ...) to get the scenario the flows are stored under
    bases = sorted({re.sub(r'-\d{4}$', '', s) for s in scenarios})
    scenario = args.scenario or (bases[0] if len(bases) == 1 else None)
    if scenario is None:
        sys.exit(f'Multiple scenarios with duals: {bases}. Pass --scenario.')
    windows = sorted(s for s in scenarios if s != scenario and s.startswith(scenario + '-'))
    if windows:
        print(f'Myopic run: stitching duals from windows {windows}', file=sys.stderr)

    dfs, gdr, p0 = discount_factors(con, args.base_year)
    duals, all_balance = load_duals(con, scenario, args.commodity)
    if duals.empty:
        sys.exit(
            f'No commodity_balance_constraint duals for {args.commodity} in scenario {scenario}.'
        )

    # Sign sanity check: across all commodity balances, nonzero duals should be mostly positive.
    nz = all_balance.dual[all_balance.dual.abs() > 1e-9]
    if len(nz) and (nz < 0).mean() > 0.5 and not args.flip_sign:
        print(
            f'WARNING: {100 * (nz < 0).mean():.0f}% of nonzero commodity-balance duals are negative; '
            'your solver may report the opposite sign convention (see --flip-sign).',
            file=sys.stderr,
        )

    duals = duals.merge(dfs, on='period', how='left')
    if duals.discount_factor.isna().any():
        sys.exit('Duals found for periods without a discount factor; check time_period.')
    sign = -1.0 if args.flip_sign else 1.0

    pieces = []
    for c, g in duals.groupby('commodity'):
        mult, note = unit_conversion(con, c, args.cost_scale, args.energy_to_mwh)
        g = g.copy()
        g['price'] = sign * g.dual / g.discount_factor * mult
        pieces.append(g)
        print(f'{c}: units {note}')
    prices = pd.concat(pieces)

    weights = load_weights(con, scenario, args.commodity)
    seg = segment_fractions(con)
    keys = ['region', 'period', 'season', 'tod', 'commodity']
    prices = prices.merge(weights, on=keys, how='left').merge(seg, on=['season', 'tod'], how='left')
    prices['load'] = prices['load'].fillna(0.0)

    # annual summaries
    rows = []
    for (c, r, p), g in prices.groupby(['commodity', 'region', 'period']):
        rows.append(
            {
                'commodity': c,
                'region': r,
                'period': p,
                'load_weighted': weighted(g, 'load'),
                'time_weighted': weighted(g, 'segment_fraction'),
                'min': g.price.min(),
                'median': g.price.median(),
                'max': g.price.max(),
                'load_PJ': g['load'].sum(),
                'n_slices': len(g),
                'n_negative': int((g.price < -1e-6).sum()),
                'n_zero': int((g.price.abs() <= 1e-6).sum()),
                'n_zero_with_load': int(((g.price.abs() <= 1e-6) & (g['load'] > 0)).sum()),
                'n_spike': int((g.price > args.spike).sum()),
            }
        )
    annual = pd.DataFrame(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f'{args.database.stem}_{scenario}'
    slice_cols = [
        'commodity',
        'region',
        'period',
        'season',
        'tod',
        'window',
        'dual',
        'discount_factor',
        'price',
        'load',
        'segment_fraction',
    ]
    prices.sort_values(keys)[slice_cols].rename(
        columns={'price': 'price_usd_per_mwh', 'load': 'load_PJ'}
    ).to_csv(args.out_dir / f'{stem}_prices_by_slice.csv', index=False)
    annual.to_csv(args.out_dir / f'{stem}_prices_annual.csv', index=False)

    pd.set_option('display.width', 200)
    print(f'\nScenario {scenario}: GDR={gdr}, P0={p0}')
    print(dfs.to_string(index=False))
    for c, g in annual.groupby('commodity'):
        print(f'\n{c}: load-weighted average price ($/MWh), region x period')
        print(
            g.pivot(index='region', columns='period', values='load_weighted').round(1).to_string()
        )

    # diagnostics
    print('\nDiagnostics')
    neg = prices[prices.price < -1e-6]
    print(
        f'  negative slice prices: {len(neg)} of {len(prices)}'
        + (f' (min {neg.price.min():.1f} $/MWh)' if len(neg) else '')
    )
    zero_load = prices[(prices.price.abs() <= 1e-6) & (prices['load'] > 0)]
    print(f'  zero prices in slices with load: {len(zero_load)}')
    spikes = prices[prices.price > args.spike]
    print(
        f'  slice prices > {args.spike:g} $/MWh: {len(spikes)}'
        + (f' (max {spikes.price.max():.0f})' if len(spikes) else '')
    )
    # Degeneracy hint: duals that jump between adjacent slices with nearly identical load,
    # or many slices sharing one exact price with a few far-off outliers.
    ratio = annual.load_weighted / annual.time_weighted
    off = annual[(ratio > 1.5) | (ratio < 0.67)]
    print(f'  region-periods where load- and time-weighted averages differ >1.5x: {len(off)}')
    no_load = annual[annual.load_PJ <= 0]
    if len(no_load):
        print(
            f'  region-periods with no recorded load (load-weighted average undefined): {len(no_load)}'
        )
    print(f'\nWrote {args.out_dir / (stem + "_prices_by_slice.csv")}')
    print(f'Wrote {args.out_dir / (stem + "_prices_annual.csv")}')


if __name__ == '__main__':
    main()
