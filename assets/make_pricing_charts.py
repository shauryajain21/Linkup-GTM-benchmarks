#!/usr/bin/env python3
"""Single pricing line chart for the GTM benchmarks README.

One line per engine across all benchmarks; y-axis is $/request (list prices for the
exact endpoint/config each engine used). Linkup is highlighted.

Run: python3 assets/make_pricing_charts.py  ->  assets/pricing_overview.png

NOTE: two points are estimates —
  * Exa enrichment/freshness ran at numResults=100 (base $0.007 + ~90x$0.001 ≈ $0.097).
  * Parallel funding assumes the `lite-fast` processor ($0.005); `base` would be $0.010.
"""
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
INK = "#0F172A"
SUBTLE = "#94A3B8"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "figure.dpi": 200,
    "savefig.dpi": 200,
})

# Benchmarks (x-axis) and per-request cost (USD) for each engine.
BENCHMARKS = ["Enrichment", "Richness", "Freshness", "Company\nresearch", "Funding"]
SERIES = {
    "Linkup":     [0.006, 0.005, 0.006, 0.005, 0.006],
    "Exa":        [0.097, 0.017, 0.097, 0.007, 0.007],
    "Parallel":   [0.005, 0.015, 0.005, 0.005, 0.005],
    "Perplexity": [0.008, 0.005, 0.008, 0.005, 0.008],
}
STYLE = {  # color, linewidth, marker size, zorder
    "Linkup":     ("#2F6BFF", 3.0, 8, 5),
    "Exa":        ("#F59E0B", 1.8, 5, 3),
    "Parallel":   ("#10B981", 1.8, 5, 3),
    "Perplexity": ("#8B5CF6", 1.8, 5, 3),
}

fig, ax = plt.subplots(figsize=(8.6, 4.8))
x = range(len(BENCHMARKS))
for name, vals in SERIES.items():
    color, lw, ms, z = STYLE[name]
    ax.plot(x, vals, color=color, linewidth=lw, marker="o", markersize=ms,
            label=name, zorder=z,
            markeredgecolor="white", markeredgewidth=1.0)
    # value label at each point (above the marker)
    for xi, v in zip(x, vals):
        ax.annotate(f"${v:.3f}", (xi, v), textcoords="offset points",
                    xytext=(0, 7), ha="center", fontsize=7, color=color, zorder=z + 1)

# Log scale so the $0.005-$0.10 range (a 20x spread) is all visible.
ax.set_yscale("log")
ax.set_ylim(0.004, 0.13)
ticks = [0.005, 0.01, 0.02, 0.05, 0.10]
ax.set_yticks(ticks)
ax.set_yticklabels([f"${v:.3f}".rstrip("0").rstrip(".") for v in ticks],
                   fontsize=10, color=SUBTLE)
ax.minorticks_off()

ax.set_xticks(list(x))
ax.set_xticklabels(BENCHMARKS, fontsize=10.5, color=INK)
ax.set_ylabel("Cost per request (log scale)", fontsize=11, color=INK)
ax.set_title("Cost per request, by benchmark", fontsize=14, fontweight="bold",
             color=INK, pad=12, loc="left")

ax.grid(axis="y", color="#EEF1F5", zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(length=0)
ax.legend(frameon=False, fontsize=10, loc="upper center", ncol=4,
          bbox_to_anchor=(0.5, -0.12))

fig.tight_layout()
path = os.path.join(OUT, "pricing_overview.png")
fig.savefig(path, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("wrote", path)
