"""Content-first vector figures for the provisional manuscript (template-neutral; restyle to the IEEE sample later).

    .venv/Scripts/python docs/paper/figures/make_figures.py      # writes fig*.svg and fig*.pdf next to this file

Fig. 1  system architecture (Modules A-G)
Fig. 2  role inference and evidence-tier decision flow (from pqscan/roles/classifier.py and pqscan/policy/engine.py)
Fig. 3  research protocol timeline with current status (no results implied)
Fig. 4  pre-F1 statistical calibration, parsed from docs/implementation/acceptance/statistical_acceptance.md;
        labelled as simulation under the assumed planning model (not scanner accuracy)
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#d9d8d4"
BLUE, BLUE_FILL, PEND = "#2a78d6", "#e6effa", "#ffffff"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none", "pdf.fonttype": 42,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})


def box(ax, x, y, w, h, text, *, fill=BLUE_FILL, edge=BLUE, ls="-", size=8.5, weight="normal", align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012", fc=fill, ec=edge,
                                lw=1.2, ls=ls))
    tx = x + w / 2 if align == "center" else x + 0.01
    ax.text(tx, y + h / 2, text, ha=align, va="center", fontsize=size, color=INK, weight=weight, linespacing=1.25)


def arrow(ax, p, q, *, ls="-", color=INK2, text=None, toff=(0, 0.012)):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=1.0, color=color, ls=ls,
                                 shrinkA=0, shrinkB=0))
    if text:
        ax.text((p[0] + q[0]) / 2 + toff[0], (p[1] + q[1]) / 2 + toff[1], text, ha="center", va="bottom",
                fontsize=7, color=INK2)


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    plt.rcParams["svg.hashsalt"] = "pqscan-paper"                      # stable element ids
    fig.savefig(HERE / f"{name}.svg", facecolor="white", metadata={"Date": None})       # no timestamp: reproducible
    fig.savefig(HERE / f"{name}.pdf", facecolor="white", metadata={"CreationDate": None})
    fig.savefig(HERE / f"{name}_preview.png", dpi=110, facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------- Fig. 1
def fig_architecture():
    fig, ax = canvas(7.2, 4.4)
    box(ax, 0.01, 0.6, 0.15, 0.2, "Python repository\n(parsed only;\nnever imported\nor executed)", fill="#f4f4f2", edge=MUTED, size=8)
    box(ax, 0.21, 0.76, 0.27, 0.15, "A  Detect\nSemgrep CE 1.185.0 rules:\ncandidate sites, rule ids", size=8)
    box(ax, 0.21, 0.46, 0.27, 0.25, "B  Semantic evidence\nimports and aliases, receiver\ntyping, arguments, bounded\nprovenance and consumer tracing\n(≤ 2 call levels, same module)", size=8)
    box(ax, 0.54, 0.55, 0.14, 0.26, "C  Roles\ndecision table:\nrole + evidence\ntier T0–T3\n(4 ablation arms)", size=8)
    box(ax, 0.715, 0.55, 0.13, 0.26, "D  Policy v1.1\nrole → class,\nτ = T2,\nNIST-referenced\nrationale", size=8)
    box(ax, 0.875, 0.55, 0.115, 0.26, "E  Export\nJSON,\nCycloneDX 1.6\n(validated),\nSARIF 2.1.0", size=8)
    arrow(ax, (0.16, 0.74), (0.21, 0.82))
    arrow(ax, (0.16, 0.65), (0.21, 0.6))
    arrow(ax, (0.48, 0.82), (0.54, 0.75))
    ax.text(0.51, 0.835, "rule ids joined by location", ha="left", va="bottom", fontsize=6.8, color=INK2)
    arrow(ax, (0.48, 0.6), (0.54, 0.63))
    arrow(ax, (0.68, 0.68), (0.715, 0.68))
    arrow(ax, (0.845, 0.68), (0.875, 0.68))
    ax.text(0.765, 0.505, "per site: RECOMMEND (SIG / KEM / KEM_DEM)\nFLAG_NO_TARGET (INVENTORY / PROTOCOL_REVIEW /\nNO_ACTION_HYBRID) · ABSTAIN",
            ha="center", va="top", fontsize=6.8, color=INK2)
    ax.add_patch(FancyBboxPatch((0.01, 0.03), 0.98, 0.33, boxstyle="round,pad=0.006,rounding_size=0.01",
                                fc="none", ec=MUTED, lw=1.0, ls=(0, (4, 3))))
    ax.text(0.02, 0.325, "Evaluation tooling (not part of a scan)", fontsize=8, color=INK2, weight="bold")
    box(ax, 0.03, 0.06, 0.45, 0.24, "F  Benchmark and statistics\nsampler (strata, cap, B0) · hash-chained ledger ·\npacket builder · frozen judge · equal-coverage\nmatching · bootstrap, guard, gate, Holm (F-B) ·\nexact McNemar + Holm (F-A) · reliability, frame audit",
        fill="#ffffff", size=7.8)
    box(ax, 0.52, 0.06, 0.45, 0.24, "G  Baselines\nsimple mappings on the same candidate sites\n(algorithm-name, method/argument) ·\nadapters for six pinned external tools ·\nmeasured file-failure profiles",
        fill="#ffffff", size=7.8)
    arrow(ax, (0.61, 0.55), (0.4, 0.3), ls=(0, (3, 2)), color=MUTED)
    arrow(ax, (0.52, 0.18), (0.48, 0.18), ls=(0, (3, 2)), color=MUTED)
    ax.text(0.5, 0.965, "Fig. 1  pqscan architecture (Modules A–E scan; F–G evaluation)", ha="center", fontsize=9.5,
            weight="bold", color=INK)
    save(fig, "fig1_architecture")


# ---------------------------------------------------------------------------- Fig. 2
def fig_flow():
    fig, ax = canvas(7.2, 5.6)
    ax.text(0.5, 0.975, "Fig. 2  Role inference, evidence tier and policy decision (arm `full`)", ha="center",
            fontsize=9.5, weight="bold")
    box(ax, 0.35, 0.88, 0.3, 0.06, "candidate call site (Modules A/B)", size=8.5)
    # operation branch
    box(ax, 0.03, 0.72, 0.42, 0.11, "Operation site\n<recv>.sign / verify / exchange / encrypt / decrypt\nrole ← method name", size=7.8)
    box(ax, 0.03, 0.47, 0.42, 0.21,
        "Tier from evidence:\nT0  receiver unresolved, no algorithm-specific arg.\nT1  receiver typed as a key OR algorithm-specific arg.\nT2  both\nT3  T2 + receiver origin resolved to a concrete\n       provenance, without conflict\nany conflict → capped at T1",
        size=7.4, align="left")
    # key-material branch
    box(ax, 0.55, 0.72, 0.42, 0.11, "Key-material site (keygen / loader / construct)\nbounded consumer tracing: aliases, attributes,\n≤ 2 call levels within the module", size=7.8)
    box(ax, 0.55, 0.47, 0.42, 0.21,
        "Consumers found:\n1 family, no escape → that role, T3\n1 family, escape → that role, T2\n≥ 2 families → UNKNOWN, T2\nnone, no escape → KEY_MATERIAL_ONLY, T2\nnone, escape → single-purpose algorithm's role,\n   T2 (X25519/X448/DH; Ed/DSA); else UNKNOWN, T1",
        size=7.4, align="left")
    arrow(ax, (0.45, 0.88), (0.24, 0.82))
    arrow(ax, (0.55, 0.88), (0.76, 0.82))
    arrow(ax, (0.24, 0.72), (0.24, 0.68))
    arrow(ax, (0.76, 0.72), (0.76, 0.68))
    # policy
    box(ax, 0.18, 0.255, 0.64, 0.155,
        "Policy v1.1 (threshold τ = T2), in order:\n1. role UNKNOWN → ABSTAIN (possible roles listed)\n2. tier < τ → ABSTAIN (missing evidence stated)\n3. approved PQ/T hybrid component → FLAG_NO_TARGET (NO_ACTION_HYBRID)\n4. otherwise class by role (table below)",
        size=7.4)
    arrow(ax, (0.24, 0.47), (0.35, 0.4))
    arrow(ax, (0.76, 0.47), (0.65, 0.4))
    rows = [("SIGN, VERIFY", "SIG", "RECOMMEND: ML-DSA (FIPS 204)"),
            ("KEY_ESTABLISHMENT", "KEM", "RECOMMEND: ML-KEM-based redesign (FIPS 203, SP 800-227)"),
            ("PK_ENCRYPT, PK_DECRYPT", "KEM_DEM", "RECOMMEND: KEM + KDF + AEAD redesign, not a drop-in"),
            ("KEY_MATERIAL_ONLY", "INVENTORY", "FLAG_NO_TARGET: inventory, find downstream role"),
            ("PROTOCOL_CONFIG*", "PROTOCOL_REVIEW", "FLAG_NO_TARGET: protocol-library review")]
    y = 0.2
    for r, c, a in rows:
        ax.text(0.1, y, r, fontsize=7.6, color=INK)
        ax.text(0.34, y, c, fontsize=7.6, color=INK, family="DejaVu Sans Mono")
        ax.text(0.52, y, a, fontsize=7.6, color=INK2)
        y -= 0.035
    ax.text(0.1, 0.03, "* PROTOCOL_CONFIG is in the taxonomy and policy but is not emitted by Module C (stated limitation).",
            fontsize=7, color=INK2)
    save(fig, "fig2_role_tier_flow")


# ---------------------------------------------------------------------------- Fig. 3
def fig_timeline():
    steps = [
        ("Protocol v1.0.4 and annotation guide v1.1 adopted (16 Nov 2026)", "DONE", "done"),
        ("R4-19 tooling implemented and verified (489 tests; differential tests)", "DONE", "done"),
        ("Pre-F1 statistical acceptance (simulation under the planning model)", "DONE", "done"),
        ("Record the AI-review identity (V8)", "PENDING · owner", "owner"),
        ("Isolated ChatGPT specification review and owner sign-off", "PENDING · owner", "owner"),
        ("Pilot (31) and synthetic (78) validation loops (D2)", "PENDING · owner", "owner"),
        ("Development/validation annotation; intra-rater re-label after ≥ 14 days", "PENDING · owner", "owner"),
        ("F1: pre-test freeze record + tag (test split stays unopened until then)", "GATE · approval", "gate"),
        ("Test fetch; Phase T annotation; re-label after ≥ 14 days", "PENDING · owner", "owner"),
        ("F2: label freeze", "GATE · approval", "gate"),
        ("E: single evaluation run (H1–H4, F-B, F-A)", "GATE · approval", "gate"),
        ("Results: accuracy, hypothesis outcomes (none exist yet)", "NOT AVAILABLE", "none"),
    ]
    fig, ax = canvas(7.2, 5.0)
    ax.text(0.5, 0.965, "Fig. 3  Pre-registered research protocol: stages and status on 18 Nov 2026", ha="center",
            fontsize=9.5, weight="bold")
    top, step = 0.88, 0.068
    ax.plot([0.1, 0.1], [top - (len(steps) - 1) * step, top], color=GRID, lw=2, zorder=0)
    for i, (label, tag, kind) in enumerate(steps):
        y = top - i * step
        if kind == "done":
            ax.plot(0.1, y, marker="o", ms=8, color=BLUE, mec=BLUE)
        elif kind == "gate":
            ax.plot(0.1, y, marker="D", ms=7, color="white", mec=INK, mew=1.4)
        elif kind == "owner":
            ax.plot(0.1, y, marker="o", ms=8, color="white", mec=INK2, mew=1.2)
        else:
            ax.plot(0.1, y, marker="o", ms=8, color="#f4f4f2", mec=MUTED, mew=1.0, ls="")
        ax.text(0.04, y, f"{i + 1:>2}", ha="right", va="center", fontsize=7.5, color=INK2)
        ax.text(0.13, y, label, ha="left", va="center", fontsize=8, color=INK if kind != "none" else INK2)
        ax.text(0.97, y, tag, ha="right", va="center", fontsize=7.4, color=INK2,
                weight="bold" if kind in ("done", "gate") else "normal")
    yc = top - 2.5 * step
    ax.plot([0.06, 0.97], [yc, yc], color=INK, lw=0.9, ls=(0, (2, 2)))
    ax.text(0.62, yc, "current position (above: done; below: not started)", ha="center", va="center",
            fontsize=6.8, color=INK, style="italic", bbox=dict(fc="white", ec="none", pad=1.0))
    ax.text(0.04, 0.035, "● done   ○ owner action   ◇ explicit approval gate.   No labels, accuracy figures or hypothesis "
            "outcomes exist; held-out\nrepositories stay unopened until the F1 freeze record and tag exist.",
            fontsize=7, color=INK2, va="bottom")
    save(fig, "fig3_protocol_timeline")


# ---------------------------------------------------------------------------- Fig. 4
def parse_acceptance():
    md = (ROOT / "docs/implementation/acceptance/statistical_acceptance.md").read_text(encoding="utf-8")
    rows = {}
    for m in re.finditer(r"^\| (S\d\d|N[+-]\d\.\d\d) \| (.*?) \| (\d+) \| (0\.\d+) \| (0\.\d+) \| (0\.\d+) \((0\.\d+)\)", md, re.M):
        rows[m.group(1)] = dict(n=int(m.group(3)), v=[float(m.group(4)), float(m.group(5)), float(m.group(6))])
    fam = {m.group(1): (int(m.group(2)), float(m.group(3))) for m in
           re.finditer(r"^\| (C\d) \| .*? \| (\d+) \| (0\.\d+) \(", md, re.M)}
    ts = {}
    for m in re.finditer(r"^\| (TS\d) \| .*? \| (\d+) \| (0\.\d+) / (0\.\d+) / (0\.\d+) \|", md, re.M):
        ts[m.group(1)] = (int(m.group(2)), [float(m.group(i)) for i in (3, 4, 5)])
    return rows, fam, ts


def fig_calibration():
    rows, fam, ts = parse_acceptance()
    assert len(rows) == 26 and len(fam) == 8 and len(ts) == 3, (len(rows), len(fam), len(ts))
    alpha = 0.025
    levels = [("α/3", alpha / 3), ("α/2", alpha / 2), ("α", alpha)]
    order = [k for k in rows if k.startswith("S") and k != "S16"] + [k for k in rows if k.startswith("N")] + ["S16"]
    fig = plt.figure(figsize=(7.2, 7.4))
    fig.text(0.5, 0.988, "Fig. 4  Pre-F1 calibration of the production H2 procedure\n"
             "SIMULATION under the assumed planning model — not evidence of scanner accuracy",
             ha="center", va="top", fontsize=9, weight="bold", linespacing=1.3)
    fig.text(0.5, 0.945, "Rejection rates when the null hypothesis is true; points ± 3 Monte Carlo SE; dashed line = nominal "
             "level; B = 1,000; code aa9d6b0.", ha="center", va="top", fontsize=7, color=INK2)
    gs = fig.add_gridspec(1, 3, left=0.2, right=0.98, top=0.9, bottom=0.39, wspace=0.12)
    gs2 = fig.add_gridspec(1, 2, width_ratios=[2.2, 1], left=0.2, right=0.98, top=0.27, bottom=0.08, wspace=0.28)
    ys = list(range(len(order)))[::-1]
    for j, (lab, nom) in enumerate(levels):
        ax = fig.add_subplot(gs[0, j])
        for y, k in zip(ys, order):
            p, n = rows[k]["v"][j], rows[k]["n"]
            se = (p * (1 - p) / n) ** 0.5
            gen = k == "S16"
            ax.errorbar(p, y, xerr=3 * se, fmt="o", ms=4.2, color=MUTED if gen else BLUE,
                        mfc="white" if gen else BLUE, ecolor=MUTED if gen else BLUE, elinewidth=1, capsize=0)
        ax.axvline(nom, color=INK, lw=1, ls=(0, (3, 2)))
        ax.set_title(f"Type I error at {lab} = {nom:.4f}", fontsize=8)
        ax.set_yticks(ys)
        ax.set_yticklabels([("S16 (random repos)" if k == "S16" else k) for k in order] if j == 0 else [], fontsize=6.6)
        ax.set_xlim(0, max(0.045, nom * 1.9))
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.tick_params(axis="x", labelsize=6.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.axhspan(ys[len(order) - 1] - 0.5, ys[len(order) - 1] + 0.5, color="#f4f4f2", zorder=0)
        ax.axhline(ys[16] - 0.5, color=GRID, lw=0.8)
    fig.text(0.03, 0.735, "17 fixed-repository\nscenarios", fontsize=6.6, color=INK2, rotation=90, va="center",
             ha="center")
    fig.text(0.03, 0.48, "8 near-equal-\ncoverage cells", fontsize=6.6, color=INK2, rotation=90, va="center", ha="center")
    fig.text(0.2, 0.335, "Grey open marker, S16: repositories redrawn per data set. Generalisation beyond fixed "
             "repositories is NOT calibrated\nand is not claimed. x-axis: rejection rate under the null.",
             fontsize=6.6, color=INK2, va="top")
    ax = fig.add_subplot(gs2[0, 0])
    keys = list(fam)
    for i, k in enumerate(keys):
        n, p = fam[k]
        se = (p * (1 - p) / n) ** 0.5
        ax.errorbar(i, p, yerr=3 * se, fmt="o", ms=4.2, color=BLUE, elinewidth=1)
    ax.axhline(alpha, color=INK, lw=1, ls=(0, (3, 2)))
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, fontsize=6.8)
    ax.set_ylim(0, 0.03)
    ax.set_title("Family-wise error, Holm m = 3 (8 configurations)", fontsize=8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.tick_params(axis="y", labelsize=6.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax2 = fig.add_subplot(gs2[0, 1])
    for i, (k, (n, v)) in enumerate(ts.items()):
        p = v[2]
        se = (p * (1 - p) / n) ** 0.5
        ax2.errorbar(i, p, yerr=3 * se, fmt="o", ms=4.2, color=BLUE, elinewidth=1)
    ax2.axhline(alpha, color=INK, lw=1, ls=(0, (3, 2)))
    ax2.set_xticks(range(len(ts)))
    ax2.set_xticklabels(list(ts), fontsize=6.8)
    ax2.set_ylim(0, 0.03)
    ax2.set_title("Two-stratum, unstratified (at α)", fontsize=8)
    ax2.grid(axis="y", color=GRID, lw=0.6)
    ax2.tick_params(axis="y", labelsize=6.6)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.text(0.03, 0.012, "Source: docs/implementation/acceptance/statistical_acceptance.md (parsed by make_figures.py).\n"
             "Acceptance criterion: each cell ≤ nominal + 3 MC-SE; all cells passed.", fontsize=6.4, color=INK2,
             va="bottom")
    save(fig, "fig4_calibration")


if __name__ == "__main__":
    fig_architecture()
    fig_flow()
    fig_timeline()
    fig_calibration()
