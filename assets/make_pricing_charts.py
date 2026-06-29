#!/usr/bin/env python3
"""Pricing charts for the GTM benchmarks README.

Per-request list-price comparison for the exact endpoint/config each engine used
in each benchmark. Bars are shown in a FIXED order (Linkup, Exa, Parallel,
Perplexity) — not sorted — so the comparison reads the same across charts. Linkup
is highlighted; value labels are the dollar cost per request.

Run: python3 assets/make_pricing_charts.py  ->  assets/pricing_*.png

Sources: each provider's public rate card (Linkup sourcedAnswer $0.005 / structured
$0.006; Exa search $0.007 base /+$0.001 per result >10; Parallel Task `lite` $0.005 /
Search $0.005 +$0.001 per result >10; Perplexity Search $0.005, base Sonar ~$0.008).
"""
import os
import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

OUT = os.path.dirname(os.path.abspath(__file__))
LOGODIR = os.path.join(OUT, "logos")

LINKUP = "#2F6BFF"
MUTED = "#D7DBE2"
INK = "#0F172A"
SUBTLE = "#94A3B8"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "figure.dpi": 200,
    "savefig.dpi": 200,
})

# Fixed display order requested: Linkup, Exa, Parallel, Perplexity.
ORDER = ["Linkup", "Exa", "Parallel", "Perplexity"]

_LOGO_CACHE = {}


def logo(name, px=96):
    key = (name.lower(), px)
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]
    img = Image.open(os.path.join(LOGODIR, f"{name.lower()}.png")).convert("RGBA")
    side = max(img.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    sq = sq.resize((px, px), Image.LANCZOS)
    arr = np.asarray(sq).astype(float) / 255.0
    _LOGO_CACHE[key] = arr
    return arr


def chart(fname, title, subtitle, prices):
    """prices: dict engine -> $/request. Bars drawn in fixed ORDER (no sort)."""
    labels = [e for e in ORDER if e in prices]
    vals = [prices[e] for e in labels]

    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    y = range(len(labels))
    colors = [LINKUP if l == "Linkup" else MUTED for l in labels]
    ax.barh(y, vals, color=colors, height=0.62, zorder=3)
    ax.invert_yaxis()

    vmax = max(vals)
    for i, (l, v) in enumerate(zip(labels, vals)):
        ax.text(v + vmax * 0.015, i, f"${v:.3f}", va="center", ha="left",
                fontsize=11, fontweight="bold" if l == "Linkup" else "normal",
                color=INK if l == "Linkup" else SUBTLE)

    ax.set_yticks([])
    blend = blended_transform_factory(ax.transAxes, ax.transData)
    for i, l in enumerate(labels):
        ab = AnnotationBbox(OffsetImage(logo(l), zoom=0.30), (-0.30, i),
                            xycoords=blend, frameon=False, box_alignment=(0, 0.5),
                            clip_on=False)
        ax.add_artist(ab)
        ax.text(-0.175, i, l, transform=blend, va="center", ha="left",
                fontsize=11, color=INK,
                fontweight="bold" if l == "Linkup" else "normal")

    ax.set_xlim(0, vmax * 1.18)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)

    ax.text(-0.34, 1.30, title, transform=ax.transAxes, fontsize=13.5,
            fontweight="bold", color=INK, ha="left", va="bottom")
    ax.text(-0.34, 1.10, subtitle, transform=ax.transAxes, fontsize=10,
            color=SUBTLE, ha="left", va="bottom")

    fig.subplots_adjust(top=0.74, left=0.34, right=0.97, bottom=0.06)
    path = os.path.join(OUT, fname)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


# ---- Per-benchmark per-request cost (USD, list prices) --------------------
# NOTE: two cells are estimates pending confirmation —
#   * Exa enrichment/freshness ran at numResults=100 (base $0.007 + ~90x$0.001).
#   * Parallel funding processor (lite-fast $0.005 vs base $0.010) not stored in data.

chart("pricing_company_research.png",
      "Cost per search request — company research",
      "Same search-only retrieval for every engine  ·  per request",
      {"Linkup": 0.005, "Exa": 0.007, "Parallel": 0.005, "Perplexity": 0.005})

chart("pricing_richness.png",
      "Cost per request — richness / meeting briefs",
      "Raw web results, 20 per query  ·  per request",
      {"Linkup": 0.005, "Exa": 0.017, "Parallel": 0.015, "Perplexity": 0.005})

chart("pricing_funding.png",
      "Cost per request — funding retrieval",
      "Structured extraction  ·  per request",
      {"Linkup": 0.006, "Exa": 0.007, "Parallel": 0.005, "Perplexity": 0.008})

chart("pricing_enrichment.png",
      "Cost per request — enrichment (structured extract)",
      "Structured profile extraction  ·  per request  ·  Exa at numResults=100",
      {"Linkup": 0.006, "Exa": 0.097, "Parallel": 0.005, "Perplexity": 0.008})

chart("pricing_freshness.png",
      "Cost per request — freshness (structured extract)",
      "Structured job-change extraction  ·  per request  ·  Exa at numResults=100",
      {"Linkup": 0.006, "Exa": 0.097, "Parallel": 0.005, "Perplexity": 0.008})
