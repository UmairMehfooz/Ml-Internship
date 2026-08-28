"""Regenerates every figure embedded in the deployed research paper (index.html).

Every number below is transcribed from an executed cell output in
work/notebooks/*.ipynb. The provenance is named in the comment above each
constant. Nothing here is simulated, smoothed, or estimated.

    python work/figures/make_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- style -----
INK = "#20242b"
MUTED = "#6d7280"
GRID = "#dcd8ce"
MODEL = "#1f4f82"
BASELINE = "#a39a8c"
REFERENCE = "#b4472e"
POSITIVE = "#2f6b4f"
WARN = "#c98a2b"

plt.rcParams.update({
    "svg.fonttype": "path",          # text -> outlines: identical in every browser
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": False,
    "figure.dpi": 110,
})


def frame(ax, keep=("left", "bottom")):
    for side, spine in ax.spines.items():
        spine.set_visible(side in keep)
    ax.tick_params(length=0)


def save(fig, name):
    path = OUT / name
    fig.savefig(path, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------- 1. Precision@50 -------
# Source: w05_model.ipynb, cells 13-14 (executed output)
#   W04 Baseline Precision@50: 0.42
#   Logistic Regression Precision@50: 0.66
#   Test-set base rate: 0.525742
def precision_at_50():
    fig, ax = plt.subplots(figsize=(7.4, 3.1))
    labels = ["Week-4 rule baseline", "Logistic Regression"]
    values = [0.42, 0.66]
    hits = ["21 of the top 50", "33 of the top 50"]
    colors = [BASELINE, MODEL]

    bars = ax.barh(labels, values, height=0.5, color=colors, zorder=3)
    ax.axvline(0.525742, color=REFERENCE, lw=1.4, ls=(0, (5, 3)), zorder=4)
    ax.text(0.5378, -0.45, "test-set base rate  0.526",
            color=REFERENCE, fontsize=9.5, va="center")

    for bar, value, hit in zip(bars, values, hits):
        y = bar.get_y() + bar.get_height() / 2
        ax.text(value + 0.012, y, "%.2f" % value, va="center", fontsize=13,
                color=INK, weight="bold")
        ax.text(value + 0.108, y, hit, va="center", fontsize=9.5, color=MUTED)

    ax.set_xlim(0, 0.92)
    ax.set_ylim(-0.72, 1.6)
    ax.set_xlabel("Precision@50 - share of the 50 highest-ranked test pages that did decline")
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: "%.1f" % v))
    frame(ax)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    save(fig, "fig-precision-at-50.svg")


# ------------------------------------------------ 2. Feature coefficients ---
# Source: w05_model.ipynb, cell 20 (executed output) - standardized coefficients
def coefficients():
    data = [
        ("gsc_clicks", -0.765112),
        ("sessions_organic", 0.240358),
        ("gsc_impressions", 0.145894),
        ("ga4_engaged_sessions", 0.064926),
        ("gsc_avg_position", -0.051644),
    ]
    names = [d[0] for d in data][::-1]
    vals = [d[1] for d in data][::-1]

    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    colors = [POSITIVE if v > 0 else MODEL for v in vals]
    ax.barh(names, vals, height=0.55, color=colors, zorder=3)
    ax.axvline(0, color=INK, lw=1.1, zorder=4)

    for i, v in enumerate(vals):
        offset = 0.028 if v > 0 else -0.028
        ax.text(v + offset, i, "%+.4f" % v, va="center",
                ha="left" if v > 0 else "right", fontsize=10, color=INK)

    ax.set_xlim(-1.06, 0.5)
    ax.set_xlabel("Standardized Logistic Regression coefficient (association, not a causal effect)")
    ax.text(-1.03, 4.62, "lower estimated decline risk", fontsize=9, color=MUTED)
    ax.text(0.48, 4.62, "higher estimated decline risk",
            fontsize=9, color=MUTED, ha="right")
    ax.set_ylim(-0.7, 5.1)
    frame(ax, keep=("bottom",))
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    save(fig, "fig-feature-coefficients.svg")


# ------------------------------------------------- 3. Validation design -----
# Source: w06_validation_audit.ipynb, cells 13/16/18 (executed output)
#   Random split Precision@50: 0.68 | Grouped split Precision@50: 0.66 | shared clients 0
def validation():
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    labels = ["Random row split\n(clients appear on both sides)",
              "Grouped by client\n(0 shared clients)"]
    values = [0.68, 0.66]
    colors = [WARN, MODEL]
    bars = ax.bar(labels, values, width=0.42, color=colors, zorder=3)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.012, "%.2f" % v,
                ha="center", fontsize=13, weight="bold", color=INK)
    ax.set_ylim(0, 0.82)
    ax.set_ylabel("Precision@50")
    frame(ax)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.tick_params(axis="x", labelsize=9.5)
    save(fig, "fig-validation-design.svg")


# ----------------------------------------------------- 4. Leakage audit -----
# Source: w03_feature_leakage_check.ipynb, cells 17/19 (executed output)
#   Accuracy WITH leakage: 1.0 | Accuracy WITHOUT leakage: 0.5529
def leakage():
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    labels = ["Depth-3 tree WITH the\ndeliberately leaked future label",
              "Same tree, leaked\ncolumn removed"]
    values = [1.0, 0.5529]
    texts = ["1.0000", "0.5529"]
    bars = ax.bar(labels, values, width=0.42, color=[REFERENCE, MODEL], zorder=3)
    for bar, v, t in zip(bars, values, texts):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.018, t,
                ha="center", fontsize=13, weight="bold", color=INK)
    ax.set_ylim(0, 1.19)
    ax.set_ylabel("Accuracy on held-out rows")
    frame(ax)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.tick_params(axis="x", labelsize=9.5)
    save(fig, "fig-leakage-audit.svg")


# ------------------------------------------------------ 5. Label balance ----
# Source: w03_feature_leakage_check.ipynb, cell 15 (executed output)
#   Rows with March + April data: 158549 | 0: 82738 (0.522) | 1: 75811 (0.478)
def label_balance():
    fig, ax = plt.subplots(figsize=(7.4, 1.5))
    ax.barh([0], [52.2], color=BASELINE, height=0.5, zorder=3)
    ax.barh([0], [47.8], left=[52.2], color=MODEL, height=0.5, zorder=3)
    ax.text(26.1, 0, "label 0 - no >20% decline\n82,738 pages  |  52.2%",
            ha="center", va="center", color="white", fontsize=10)
    ax.text(76.1, 0, "label 1 - declined >20%\n75,811 pages  |  47.8%",
            ha="center", va="center", color="white", fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("Share of the 158,549 matched March-to-April page rows")
    frame(ax, keep=("bottom",))
    save(fig, "fig-label-balance.svg")


# -------------------------------------------------------- 6. Missingness ----
# Source: w03_feature_leakage_check.ipynb, cell 8 (executed output)
def missingness():
    data = [
        ("ga4_engaged_sessions", 27.57),
        ("sessions_organic", 27.57),
        ("gsc_impressions", 0.00),
        ("gsc_avg_position", 0.00),
        ("gsc_clicks", 0.00),
    ]
    names = [d[0] for d in data][::-1]
    vals = [d[1] for d in data][::-1]
    fig, ax = plt.subplots(figsize=(7.4, 2.9))
    ax.barh(names, vals, height=0.5, color=[MODEL if v else GRID for v in vals], zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + 0.6, i, "%.2f%%" % v, va="center", fontsize=10,
                color=INK if v else MUTED)
    ax.set_xlim(0, 34)
    ax.set_xlabel("Missing values in the March feature table (%)")
    frame(ax)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    save(fig, "fig-missingness.svg")


# --------------------------------------------------- 7. Baseline signals ----
# Source: w04_baseline_score.ipynb, cells 3 and 7 (executed output)
def baseline_signals():
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2))

    buckets = ["1-3", "4-5", "6-10", "11-20", "21+"]
    counts = [16144, 26593, 55395, 32203, 44969]
    med_pos = [2.21, 4.08, 7.00, 13.94, 34.56]
    ax = axes[0]
    ax.bar(buckets, counts, width=0.6, color=MODEL, zorder=3)
    for i, (c, p) in enumerate(zip(counts, med_pos)):
        ax.text(i, c + 1400, "med %.2f" % p, ha="center", fontsize=8, color=MUTED)
    ax.set_title("Signal 1 - search position", fontsize=10.5, color=INK, pad=10)
    ax.set_ylabel("March pages")
    ax.set_xlabel("Average position bucket")
    ax.set_ylim(0, 63000)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "%dk" % (v / 1000)))
    frame(ax)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)

    q = ["Q1", "Q2", "Q3", "Q4"]
    med_imp = [4, 67, 419, 3012]
    med_clicks = [0, 0, 0, 6]
    ax = axes[1]
    ax.bar(q, med_imp, width=0.6, color=POSITIVE, zorder=3)
    ax.set_yscale("log")
    for i, (m, c) in enumerate(zip(med_imp, med_clicks)):
        ax.text(i, m * 1.35, "%d clicks" % c, ha="center", fontsize=8, color=MUTED)
    ax.set_title("Signal 2 - search impressions", fontsize=10.5, color=INK, pad=10)
    ax.set_ylabel("Median March impressions (log)")
    ax.set_xlabel("Impression quartile")
    ax.set_ylim(1, 20000)
    frame(ax)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)

    fig.tight_layout()
    save(fig, "fig-baseline-signals.svg")


# ------------------------------------------------------- 8. Row funnel ------
# Sources: w03_data_contract.ipynb cell 12 (9,841,378 March daily rows),
#          w04_baseline_score.ipynb cell 2 (176,738 March page rows),
#          w03_feature_leakage_check.ipynb cell 15 (158,549 matched rows),
#          w05_model.ipynb cell 8 (93,206 train + 20,647 test after dropna)
def funnel():
    steps = [
        ("March 2026 daily rows\nin the performance fact table", 9841378),
        ("March page-level rows\nwith Search Console available", 176738),
        ("Matched to the April\noutcome window", 158549),
        ("Complete on all five features\n(93,206 train + 20,647 test)", 113853),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    names = [s[0] for s in steps][::-1]
    vals = [s[1] for s in steps][::-1]
    ax.barh(names, vals, height=0.52, color=["#8fa7bd", "#3f6f9f", MODEL, MODEL], zorder=3)
    ax.set_xscale("log")
    for i, v in enumerate(vals):
        ax.text(v * 1.15, i, "{:,}".format(v), va="center", fontsize=10.5, color=INK)
    ax.set_xlim(5e4, 4e7)
    ax.set_xlabel("Rows (log scale)")
    ax.tick_params(axis="y", labelsize=9)
    frame(ax)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    save(fig, "fig-row-funnel.svg")


# ------------------------------------------------- 9. Starter slice mix -----
# Source: w01_research_question.ipynb cell 8 / w02_ml_task_framing.ipynb cell 6
def starter_mix():
    data = [("down", 16262, 54.21), ("stable", 5962, 19.87), ("up", 4388, 14.63),
            ("new", 2236, 7.45), ("flat", 1152, 3.84)]
    fig, ax = plt.subplots(figsize=(7.4, 2.7))
    names = [d[0] for d in data]
    pct = [d[2] for d in data]
    counts = [d[1] for d in data]
    colors = [REFERENCE, BASELINE, POSITIVE, MUTED, "#cfc8b8"]
    bars = ax.bar(names, pct, width=0.55, color=colors, zorder=3)
    for bar, p, c in zip(bars, pct, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, p + 1.2,
                "%.2f%%\n%s" % (p, "{:,}".format(c)), ha="center", fontsize=9, color=INK)
    ax.set_ylim(0, 68)
    ax.set_ylabel("Share of pages (%)")
    ax.set_xlabel("Observed trend_direction label")
    frame(ax)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    save(fig, "fig-starter-trend-mix.svg")


if __name__ == "__main__":
    precision_at_50()
    coefficients()
    validation()
    leakage()
    label_balance()
    missingness()
    baseline_signals()
    funnel()
    starter_mix()
