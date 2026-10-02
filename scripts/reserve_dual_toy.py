"""Toy capacity-expansion LP with Temoa's discounting, to show where a 2025 turbine's capital
shows up in later reserve-margin duals. One region, one peak slice, gas turbines only."""

import highspy
import numpy as np

g, p0, periods, p_end = 0.02, 2020, [2025, 2030, 2035, 2040, 2045, 2050], 2055
A, F = 26.77, 20.527  # yearly capital-equivalent and fixed O&M, M$/GW-yr
cc, prm = 0.9, 0.35  # capacity credit, reserve margin
pa = lambda n: ((1 + g) ** n - 1) / (g * (1 + g) ** n)
DF = {p: pa(5) / (1 + g) ** (p - p0) for p in periods}  # same factor as my script
# Temoa: loan payments from vintage v to horizon end, FOM every active period -> both sum DF_p, p>=v
cost = {v: (A + F) * sum(DF[p] for p in periods if p >= v) for v in periods}


def solve(load, existing, allow_build):
    h = highspy.Highs()
    h.setOptionValue('output_flag', False)
    n = len(periods)
    for v in periods:  # N_v >= 0
        h.addVar(0, highspy.kHighsInf if allow_build(v) else 0)
        h.changeColCost(periods.index(v), cost[v])
    for i, p in enumerate(periods):  # cc*(E + sum_{v<=p} N_v) >= (1+prm)*load_p
        idx = [j for j, v in enumerate(periods) if v <= p]
        h.addRow(
            (1 + prm) * load[p] - cc * existing,
            highspy.kHighsInf,
            len(idx),
            np.array(idx, dtype=np.int32),
            np.full(len(idx), cc),
        )
    h.run()
    sol = h.getSolution()
    N = sol.col_value
    rho = sol.row_dual
    print(
        ' period  build_GW  dual(disc.)  dual/DF=M$/GW-yr of requirement   $/MWh adder in 57-h slice'
    )
    for i, p in enumerate(periods):
        d = (1 + prm) * rho[i]  # d obj / d (1 GW more peak load)
        print(
            f'  {p}   {N[i]:7.2f}   {d:9.2f}        {d / DF[p]:7.2f}                        {d / DF[p] * 1e6 / 57000:7.0f}'
        )
    print(
        '  check: cost of 2025 turbine =',
        round(cost[2025] * cc / cc, 2),
        ' = sum of cc*rho_p over periods it is active:',
        round(sum(cc * rho[i] for i in range(len(periods))), 2) if N[0] > 1e-9 else '(not built)',
    )


print('DF: ' + ', '.join(f'{p}:{DF[p]:.3f}' for p in periods))
print(
    f'(A+F)={A + F:.2f} M$/GW-yr; with reserve factor (1+prm)/cc={(1 + prm) / cc:.2f} -> {(A + F) * (1 + prm) / cc:.1f} M$/GW-yr of load\n'
)
base = 10.0
print('CASE 1: peak load grows 1 GW every period -> a new turbine every period')
solve({p: base + i + 1 for i, p in enumerate(periods)}, base * (1 + prm) / cc, lambda v: True)
print('\nCASE 2: peak steps up 1 GW in 2025 and then stays flat -> only the 2025 turbine')
solve(dict.fromkeys(periods, base + 1), base * (1 + prm) / cc, lambda v: True)
print(
    '\nCASE 3: 2025 has spare capacity, peak steps up 1 GW in 2030, but 2030+ builds are not allowed'
)
solve(
    {p: base if p == 2025 else base + 1 for p in periods},
    base * (1 + prm) / cc,
    lambda v: v == 2025,
)
