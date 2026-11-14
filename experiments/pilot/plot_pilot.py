"""Plot the H1 pilot outcome composition per baseline tool.

Usage: python experiments/pilot/plot_pilot.py docs/pilot/h1_pilot_joined.csv docs/pilot/figures/pilot_outcomes.png
Reads only the joined CSV produced by join_tool_outputs.py; no numbers are typed in by hand.
"""
import csv, sys, collections
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

joined, out = Path(sys.argv[1]), Path(sys.argv[2])
rows = [r for r in csv.DictReader(open(joined, encoding="utf-8")) if r["eligible"] == "yes"]
tools = list(dict.fromkeys(r["tool"] for r in rows))
order = ["CORRECT", "INCORRECT", "UNDECIDED", "DETECTED_ONLY", "MISSED"]
labels = {"CORRECT": "Correct", "INCORRECT": "Harmful (incorrect)", "UNDECIDED": "Undecided (dual target)",
          "DETECTED_ONLY": "Detected, no target", "MISSED": "Missed"}
# status colours (good / critical / warning) + two neutrals; identity is also carried by direct labels and the legend
colors = {"CORRECT": "#0ca30c", "INCORRECT": "#d03b3b", "UNDECIDED": "#fab219", "DETECTED_ONLY": "#898781", "MISSED": "#c3c2b7"}
counts = {t: collections.Counter(r["judgment"] for r in rows if r["tool"] == t) for t in tools}
n = len({r["site_id"] for r in rows})

fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=200)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
y = list(range(len(tools)))[::-1]
left = [0] * len(tools)
for cls in order:
    vals = [counts[t].get(cls, 0) for t in tools]
    bars = ax.barh(y, vals, left=left, color=colors[cls], edgecolor="#fcfcfb", linewidth=2, height=0.62, label=labels[cls])
    for b, v in zip(bars, vals):
        if v >= 2:
            ax.text(b.get_x() + b.get_width() / 2, b.get_y() + b.get_height() / 2, str(v), ha="center", va="center",
                    fontsize=8, color="#0b0b0b" if cls in ("UNDECIDED", "MISSED", "DETECTED_ONLY") else "#ffffff")
    left = [l + v for l, v in zip(left, vals)]
ax.set_yticks(y); ax.set_yticklabels(tools, fontsize=9, color="#0b0b0b")
ax.set_xlim(0, n); ax.set_xlabel(f"eligible pilot call sites (n = {n})", fontsize=8.5, color="#52514e")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#c3c2b7"); ax.tick_params(colors="#898781", labelsize=8)
ax.xaxis.grid(True, color="#e1e0d9", linewidth=0.6); ax.set_axisbelow(True)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=5, frameon=False, fontsize=7.5)
ax.set_title("H1 pilot: recommendation outcome per baseline (policy v1.1)", fontsize=10, color="#0b0b0b", pad=26, loc="left")
out.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout(); fig.savefig(out, facecolor=fig.get_facecolor())
print("wrote", out, {t: dict(counts[t]) for t in tools})
