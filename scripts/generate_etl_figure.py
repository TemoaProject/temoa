"""
Generates docs/source/images/eos_cost_curve.{png,svg} — a labelled diagram
of the piecewise-linear cost curve shared by all three features of the
economies of scale (EOS) extension: cost_invest_eos, cost_fixed_eos, and
cost_variable_eos.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

matplotlib.rcParams.update(
    {
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'pdf.fonttype': 42,
        'svg.fonttype': 'none',
    }
)

OUT_DIR = Path(__file__).parent.parent / 'docs' / 'source' / 'images'

# ——— Segment data (decreasing marginal cost — economies of scale) —————————————
# Each entry: (q_lower, q_upper, cost_lower, cost_upper)
segments = [
    (0.0, 2.0, 0.0, 6.0),  # n=1  slope = 3.0
    (2.0, 5.0, 6.0, 12.0),  # n=2  slope = 2.0
    (5.0, 9.0, 12.0, 16.0),  # n=3  slope = 1.0
]

PALETTE = {
    'curve': '#1f1f1f',
    'active': '#d44040',
    'inactive': '#aaaaaa',
    'fill': '#fde8e8',
    'grid': '#e8e8e8',
    'annot': '#555555',
    'tick': '#333333',
}

# Active segment (0-indexed) — the one the optimizer has selected in this period
ACTIVE = 1
# Quantity realised in this period (sits inside the active segment)
Q_P = 3.5

fig, ax = plt.subplots(figsize=(8.0, 5.0))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# ——— Shade the active segment background ——————————————————————————————————————
ql_a, qu_a, cl_a, cu_a = segments[ACTIVE]
ax.axvspan(ql_a, qu_a, color=PALETTE['fill'], zorder=0, linewidth=0)

# ——— Draw all segment lines ————————————————————————————————————————————————————
for i, (ql, qu, cl, cu) in enumerate(segments):
    color = PALETTE['active'] if i == ACTIVE else PALETTE['curve']
    lw = 2.2 if i == ACTIVE else 1.6
    ax.plot([ql, qu], [cl, cu], color=color, linewidth=lw, solid_capstyle='round', zorder=3)
    dot_color = PALETTE['active'] if i == ACTIVE else PALETTE['curve']
    ax.plot(ql, cl, 'o', ms=5, color=dot_color, zorder=4)
    ax.plot(qu, cu, 'o', ms=5, color=dot_color, zorder=4)

# ——— Vertical line at current-period quantity —————————————————————————————————
slope_a = (cu_a - cl_a) / (qu_a - ql_a)
cost_p = cl_a + slope_a * (Q_P - ql_a)

# ——— Capacity/activity bound tick labels on x-axis ———————————————————————————
boundaries = []
for i, (ql, _qu, _cl, _cu) in enumerate(segments):
    n = i  # 0-based
    if ql == 0:
        boundaries.append((ql, r'$\underline{Q}_{n=0} = 0$'))
    else:
        boundaries.append((ql, rf'$\bar{{Q}}_{{n={n - 1}}} = \underline{{Q}}_{{n={n}}}$'))

_, qu_last, _, _ = segments[-1]
boundaries.append((qu_last, rf'$\bar{{Q}}_{{n={len(segments) - 1}}}$'))

x_ticks = [b[0] for b in boundaries] + [Q_P]
x_labels = [b[1] for b in boundaries] + [r'$\mathbf{Q}_p$']

ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels, fontsize=8.5, color=PALETTE['tick'])

# ——— Cost bound tick labels on y-axis ————————————————————————————————————————
y_boundaries = []
for i, (_ql, _qu, cl, _cu) in enumerate(segments):
    n = i  # 0-based
    if cl == 0:
        y_boundaries.append((cl, r'$\underline{C}_{n=0} = 0$'))
    else:
        # shared upper bound of prev segment / lower bound of this segment
        y_boundaries.append((cl, rf'$\bar{{C}}_{{n={n - 1}}} = \underline{{C}}_{{n={n}}}$'))

_, _, _, cu_last = segments[-1]
y_boundaries.append((cu_last, rf'$\bar{{C}}_{{n={len(segments) - 1}}}$'))

y_ticks = [b[0] for b in y_boundaries]
y_labels = [b[1] for b in y_boundaries]

ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, fontsize=8.5, color=PALETTE['tick'])

# ——— Dashed reference lines to axes from segment endpoints ———————————————————
dash_kw = {'color': PALETTE['inactive'], 'linewidth': 0.8, 'linestyle': ':', 'zorder': 1}
for ql, qu, cl, cu in segments:
    ax.plot([ql, ql], [0, cl], **dash_kw)
    ax.plot([qu, qu], [0, cu], **dash_kw)
    ax.plot([0, ql], [cl, cl], **dash_kw)
    ax.plot([0, qu], [cu, cu], **dash_kw)

# dashed lines from Q_P up to cost curve, then across to y-axis
ax.plot([Q_P, Q_P], [0, cost_p], color=PALETTE['active'], linewidth=0.9, linestyle='--', zorder=2)
ax.plot(
    [0, Q_P], [cost_p, cost_p], color=PALETTE['active'], linewidth=0.9, linestyle='--', zorder=2
)
ax.plot(0, cost_p, '<', ms=5, color=PALETTE['active'], zorder=4, clip_on=False)
ax.plot(Q_P, 0, 'v', ms=5, color=PALETTE['active'], zorder=4, clip_on=False)

# ——— Slope annotation on active segment ——————————————————————————————————————
mid_q = (ql_a + qu_a) / 2
mid_c = cl_a + slope_a * (mid_q - ql_a)
dq, dc = 0.6, slope_a * 0.6
ax.annotate(
    '',
    xy=(mid_q + dq, mid_c + dc),
    xytext=(mid_q + dq, mid_c),
    arrowprops={'arrowstyle': '-', 'color': PALETTE['annot'], 'lw': 0.9},
)
ax.annotate(
    '',
    xy=(mid_q + dq, mid_c),
    xytext=(mid_q, mid_c),
    arrowprops={'arrowstyle': '-', 'color': PALETTE['annot'], 'lw': 0.9},
)
ax.text(
    mid_q + dq + 0.08,
    mid_c + dc / 2,
    r'$m_n = \frac{\Delta C}{\Delta Q}$  (slope)',
    va='center',
    ha='left',
    fontsize=8.5,
    color=PALETTE['annot'],
)

# ——— Segment labels ———————————————————————————————————————————————————————————
for i, (ql, qu, cl, cu) in enumerate(segments):
    n = i  # 0-based
    mid_q = (ql + qu) / 2
    mid_c = (cl + cu) / 2
    color = PALETTE['active'] if i == ACTIVE else PALETTE['annot']
    weight = 'bold' if i == ACTIVE else 'normal'
    ax.text(
        mid_q,
        mid_c + 0.7,
        f'$n={n}$',
        ha='center',
        va='bottom',
        fontsize=9,
        color=color,
        fontweight=weight,
    )

# ——— Active-segment label —————————————————————————————————————————————————————
ax.text(
    (ql_a + qu_a) / 2,
    1.5,
    'active segment\n' r'$b_{n=1} = 1$',
    ha='center',
    va='bottom',
    fontsize=8.5,
    color=PALETTE['active'],
    bbox={'boxstyle': 'round,pad=0.3', 'fc': PALETTE['fill'], 'ec': PALETTE['active'], 'lw': 0.8},
)

# ——— Axes formatting ——————————————————————————————————————————————————————————
ax.set_xlim(-0.3, 10.2)
ax.set_ylim(-0.3, 18.5)
ax.set_xlabel('Quantity  $Q$  (capacity or activity)', labelpad=8)
ax.set_ylabel('Total cost  $C$', labelpad=8)
ax.set_title('EOS piecewise-linear cost curve', pad=10, fontsize=11)

ax.xaxis.set_minor_locator(ticker.NullLocator())
ax.yaxis.set_minor_locator(ticker.NullLocator())

# ——— Legend ———————————————————————————————————————————————————————————————————
handles = [
    mpatches.Patch(
        facecolor=PALETTE['fill'],
        edgecolor=PALETTE['active'],
        lw=0.8,
        label='Active segment in period $p$',
    ),
    plt.Line2D([0], [0], color=PALETTE['active'], lw=2.2, label='Active segment cost line'),
    plt.Line2D([0], [0], color=PALETTE['curve'], lw=1.6, label='Inactive segment cost line'),
    plt.Line2D(
        [0],
        [0],
        color=PALETTE['active'],
        lw=1.2,
        linestyle='--',
        label=r'$\mathbf{Q}_p$ (current period)',
    ),
]
ax.legend(
    handles=handles, fontsize=8, loc='upper left', frameon=True, framealpha=0.9, edgecolor='#cccccc'
)

fig.tight_layout()

for ext in ('png', 'svg'):
    out = OUT_DIR / f'eos_cost_curve.{ext}'
    fig.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Saved {out}')

plt.close(fig)
