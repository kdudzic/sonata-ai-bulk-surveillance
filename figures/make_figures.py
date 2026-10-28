"""Redraw the three pilot figures as vector graphics (SVG and PDF).

The original PNGs had no surviving source script. This reproduces them so they
can go into a Word manuscript without raster loss: Word 2016+ inserts SVG
natively, and the PDF serves LaTeX or print. Text is converted to outlines, so
the figures look the same on a machine without DejaVu Serif.

Values are stored as integer counts rather than rounded percentages, so bars
sit at their exact heights. Sources:

- Figure 1: KEEP_FOR_REVIEW counts per model (of 96) and over/under-retention
  totals from ``runs/02-pilot-en/*-results.xlsx`` (see docs/pilot-results.md).
  The 38.5-72.9% band is the retention range consistent with minimal
  interference, as given in the paper.
- Figure 2: expert score sums from ``runs/05-results/all-runs-consolidated.xlsx``
  (sheets ``short`` and ``Structured``), 96 rows per model, 480 per format.
  Grok 4.20 structured is 867/96 = 9.03; earlier drafts of the paper and of
  docs/pilot-results.md quoted 9.05 in error.
- Figure 3: counterfactual pairs whose decision flipped, per flipped variable
  (5 models x n pairs), with the expert label-change rate as benchmark.

Run: ``uv run --with matplotlib python figures/make_figures.py``
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

OUT = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "hatch.linewidth": 1.0,
    "svg.fonttype": "path",
    "pdf.fonttype": 42,
})

RATIONALE = dict(facecolor="white", edgecolor="black", hatch="///", linewidth=1.2)
STRUCTURED = dict(facecolor="#737373", edgecolor="black", linewidth=1.2)
LABEL_RATIONALE = "Free-text rationale"
LABEL_STRUCTURED = "Structured contrastive"
W = 0.36


def save(fig, stem: str) -> None:
    for ext in ("svg", "pdf"):
        fig.savefig(OUT / f"{stem}.{ext}", bbox_inches="tight")
    plt.close(fig)


def bar_labels(ax, xs, values, fmt, size=9, pad=2.0):
    for x, v in zip(xs, values):
        ax.text(x, v + pad, fmt(v), ha="center", va="bottom", fontsize=size)


def figure_1() -> None:
    models = ["DeepSeek V4 Pro", "Gemini 3.1 Pro", "Grok 4.20", "GPT-5.5", "Mistral Large 2512"]
    keep_rationale = [54, 63, 69, 75, 81]
    keep_structured = [54, 57, 67, 74, 83]
    rationale = [k / 96 * 100 for k in keep_rationale]
    structured = [k / 96 * 100 for k in keep_structured]
    band = (38.5, 72.9)

    fig, (a, b) = plt.subplots(1, 2, figsize=(9.75, 5.4), gridspec_kw={"width_ratios": [1.8, 1]})

    xs = range(len(models))
    a.axhspan(*band, xmin=0, xmax=1, color="#e0e0e0", zorder=0, linewidth=0)
    for y in band:
        a.axhline(y, color="black", linestyle="--", linewidth=0.9, zorder=1)
        a.text(len(models) - 0.45, y, f"{y:.1f}", fontsize=8, color="#555555",
               va="bottom" if y == band[1] else "top")
    a.bar([x - W / 2 for x in xs], rationale, W, zorder=2, **RATIONALE)
    a.bar([x + W / 2 for x in xs], structured, W, zorder=2, **STRUCTURED)
    bar_labels(a, [x - W / 2 for x in xs], rationale, lambda v: f"{v:.1f}", size=8)
    bar_labels(a, [x + W / 2 for x in xs], structured, lambda v: f"{v:.1f}", size=8)
    a.set_xlim(-0.6, len(models) - 0.4)
    a.set_ylim(0, 112)
    a.set_yticks(range(0, 101, 20))
    a.set_xticks(list(xs))
    a.set_xticklabels(models, rotation=20, ha="right")
    a.set_ylabel("KEEP_FOR_REVIEW rate (%)")
    a.set_title("(a) Retention rate by model", loc="left")
    a.legend(
        handles=[Patch(**RATIONALE, label=LABEL_RATIONALE),
                 Patch(**STRUCTURED, label=LABEL_STRUCTURED),
                 Patch(facecolor="#e0e0e0", label="range consistent with minimal interference")],
        loc="upper left", frameon=False, fontsize=9, borderaxespad=0.1,
    )

    errors = ["Over-\nretention", "Under-\nretention"]
    err_rationale = [160, 3]
    err_structured = [152, 2]
    xs = range(len(errors))
    b.bar([x - W / 2 for x in xs], err_rationale, W, **RATIONALE)
    b.bar([x + W / 2 for x in xs], err_structured, W, **STRUCTURED)
    bar_labels(b, [x - W / 2 for x in xs], err_rationale, str, pad=4)
    bar_labels(b, [x + W / 2 for x in xs], err_structured, str, pad=4)
    b.set_ylim(0, 185)
    b.set_xticks(list(xs))
    b.set_xticklabels(errors, fontsize=9)
    b.set_ylabel("decisions (of 480 per format)")
    b.set_title("(b) Direction of error", loc="left")

    fig.tight_layout()
    save(fig, "figure-1-over-retention")


def figure_2() -> None:
    # Sum of expert 0-12 scores over the model's 96 rows: (rationale, structured).
    sums = {
        "Grok 4.20": (820, 867),
        "GPT-5.5": (764, 819),
        "DeepSeek V4 Pro": (763, 773),
        "Gemini 3.1 Pro": (783, 771),
        "Mistral Large 2512": (726, 717),
    }
    # Label nudges keep near-coincident values readable; the points stay exact.
    nudge_left = {"GPT-5.5": 0.06}
    nudge_right = {"DeepSeek V4 Pro": 0.06, "Gemini 3.1 Pro": -0.03}

    dims = ["Specificity", "Contrastiveness", "Contestability", "Plain language",
            "Evidential grounding", "Proportionality relevance"]
    # Sum of each dimension's 0-2 scores over 480 rows: (rationale, structured).
    dim_sums = [(11, 11), (871, 846), (728, 738), (914, 936), (819, 846), (509, 570)]

    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 5.9), gridspec_kw={"width_ratios": [1, 1.55]})

    for model, (r, s) in sums.items():
        r, s = r / 96, s / 96
        improves = s > r
        style = dict(color="black", linestyle="-") if improves else dict(color="#8c8c8c", linestyle="--")
        a.plot([0, 1], [r, s], marker="o", markersize=5, linewidth=1.6, **style)
        a.text(-0.08, r + nudge_left.get(model, 0), f"{r:.2f}", ha="right", va="center", fontsize=9)
        a.text(1.08, s + nudge_right.get(model, 0), f"{s:.2f}  {model}", ha="left", va="center", fontsize=9)
    a.set_xlim(-0.45, 1.05)
    a.set_ylim(7.4, 9.1)
    a.set_xticks([0, 1])
    a.set_xticklabels(["Free-text\nrationale", "Structured\ncontrastive"])
    a.tick_params(axis="x", length=0)
    a.spines["bottom"].set_visible(False)
    a.set_ylabel("mean expert legal-quality score (0–12)")
    a.set_title("(a) Format effect by model", loc="left")
    a.legend(
        handles=[Line2D([], [], color="black", marker="o", markersize=5, label="improves"),
                 Line2D([], [], color="#8c8c8c", linestyle="--", marker="o", markersize=5, label="declines")],
        loc="upper left", frameon=False, fontsize=9, borderaxespad=0.1,
    )

    rationale = [r / 480 for r, _ in dim_sums]
    structured = [s / 480 for _, s in dim_sums]
    xs = range(len(dims))
    b.bar([x - W / 2 for x in xs], rationale, W, **RATIONALE)
    b.bar([x + W / 2 for x in xs], structured, W, **STRUCTURED)
    for x, r, s in zip(xs, rationale, structured):
        b.text(x, max(r, s) + 0.08, f"{s - r:+.2f}", ha="center", va="bottom", fontsize=9)
    b.set_ylim(0, 2.55)
    b.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    b.set_xticks(list(xs))
    b.set_xticklabels(dims, rotation=25, ha="right", fontsize=9)
    b.set_ylabel("mean score per dimension (0–2)")
    b.set_title("(b) Where the advantage sits", loc="left")
    b.legend(
        handles=[Patch(**RATIONALE, label=LABEL_RATIONALE), Patch(**STRUCTURED, label=LABEL_STRUCTURED)],
        loc="upper left", frameon=False, fontsize=9, borderaxespad=0.1,
    )

    fig.tight_layout(w_pad=3)
    save(fig, "figure-2-format-effect")


def figure_3() -> None:
    # (variable, pairs, flipped decisions rationale, structured, expert label changes)
    rows = [
        ("target\nspecificity", 10, 6, 5, 2),
        ("imminence", 10, 6, 7, 0),
        ("agency\ncue", 10, 4, 6, 0),
        ("speaker\nperspective", 7, 19, 15, 3),
        ("exculpatory\nsignal", 6, 9, 9, 4),
        ("speech\nact", 5, 10, 7, 0),
    ]
    models = 5

    fig, ax = plt.subplots(figsize=(9.3, 5.9))
    for x, (name, n, r, s, e) in enumerate(rows):
        r, s, e = r / (n * models) * 100, s / (n * models) * 100, e / n * 100
        ax.bar(x - W / 2, r, W, **RATIONALE)
        ax.bar(x + W / 2, s, W, **STRUCTURED)
        ax.text(x - W / 2, r + 1.5, f"{r:.0f}", ha="center", va="bottom", fontsize=9)
        ax.text(x + W / 2, s + 1.5, f"{s:.0f}", ha="center", va="bottom", fontsize=9)
        ax.plot([x - W, x + W], [e, e], color="black", linewidth=2.2, solid_capstyle="butt", zorder=3)
        ax.text(x - W - 0.04, e, f"{e:.0f}", ha="right", va="center", fontsize=8)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([f"{name}\n(n={n} pairs)" for name, n, *_ in rows], fontsize=9)
    ax.set_xlim(-0.75, len(rows) - 0.4)
    ax.set_ylim(0, 72)
    ax.set_ylabel("pairs where the decision changed (%)")
    ax.set_title("Decision sensitivity to the single flipped variable", loc="left")
    ax.legend(
        handles=[Patch(**RATIONALE, label=LABEL_RATIONALE),
                 Patch(**STRUCTURED, label=LABEL_STRUCTURED),
                 Line2D([], [], color="black", linewidth=2.2, label="expert benchmark")],
        loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False, fontsize=9,
    )

    fig.tight_layout()
    save(fig, "figure-3-counterfactual-sensitivity")


if __name__ == "__main__":
    figure_1()
    figure_2()
    figure_3()
