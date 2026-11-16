"""Owner workload model for protocol v1.0.4 revision 3 (PROPOSED). Every parameter is an ASSUMPTION; nothing
here is measured. Writes ../results/workload_rev3.md.

Repositories: 6 development/validation (quota 25) + 7 test (quota 30), from benchmark/real/manifest.json.
"""
import math
from pathlib import Path

REPOS = {"dev_val": (6, 25), "test": (7, 30)}
S = {   # low / expected / high
    "yield_S1":            (0.50, 0.40, 0.30),   # share of issued S1 candidates that are eligible
    "overshoot_per_repo":  (3, 5, 9),            # candidates issued past the quota in the last batch
    "b0_per_repo":         (10, 10, 10),
    "min_ineligible":      (0.75, 1.0, 1.5),     # owner minutes per ineligible candidate
    "min_eligible":        (2.0, 3.0, 4.0),      # owner minutes per eligible candidate (evidence lines)
    "s2_yield":            (0.05, 0.10, 0.20),
    "min_ai_handling":     (0.5, 1.0, 2.0),      # packet copy, Temporary Chat run, export, per candidate
    "disagree_rate":       (0.10, 0.20, 0.30),
    "min_adjudicate":      (3.0, 4.0, 6.0),
    "min_relabel":         (2.0, 2.5, 3.5),
    "h_frame_audit":       (3, 5, 8),            # >= 6 files to >= 60 eligible sites, owner reading whole files
    "h_pilot":             (2, 3, 4),            # 31 sites, primary + AI handling + adjudication
    "h_synthetic":         (2, 3, 5),            # 78 instances
    "h_spec_review":       (2, 4, 8),            # running the ChatGPT specification review + owner sign-off
    "h_eval_reporting":    (8, 16, 32),          # owner review of E outputs, limitations, report text
}


def scenario(i: int) -> dict:
    g = {k: v[i] for k, v in S.items()}
    out = {}
    phase_candidates = {}
    for phase, (k, q) in REPOS.items():
        s1 = min(math.ceil(q / g["yield_S1"]) + g["overshoot_per_repo"], 4 * q)
        elig = s1 * g["yield_S1"] + g["b0_per_repo"] * g["s2_yield"]
        cand = s1 + g["b0_per_repo"]
        phase_candidates[phase] = k * cand
        out[f"{phase}: candidates"] = k * cand
        out[f"{phase}: primary h"] = k * (elig * g["min_eligible"] + (cand - elig) * g["min_ineligible"]) / 60
        out[f"{phase}: AI review h"] = k * cand * g["min_ai_handling"] / 60 * 1.10      # +10% self-consistency repeats
        out[f"{phase}: adjudication h"] = k * cand * g["disagree_rate"] * g["min_adjudicate"] / 60
        n_rel = max(50, math.ceil(0.10 * k * cand))
        out[f"{phase}: intra-rater h"] = n_rel * g["min_relabel"] / 60
    for key in ("h_frame_audit", "h_pilot", "h_synthetic", "h_spec_review", "h_eval_reporting"):
        out[key[2:] + " h"] = g[key]
    out["TOTAL h"] = sum(v for k, v in out.items() if k.endswith(" h"))
    return out


if __name__ == "__main__":
    names = ("low", "expected", "high")
    res = [scenario(i) for i in range(3)]
    lines = ["# Owner workload (ASSUMED parameters; not measured)", "", "| Item | low | expected | high |", "|---|---|---|---|"]
    for k in res[0]:
        lines.append(f"| {k} | " + " | ".join(f"{r[k]:.0f}" for r in res) + " |")
    lines += ["", "Parameters (low / expected / high):", ""] + [f"- {k}: {v}" for k, v in S.items()]
    out = Path(__file__).resolve().parents[1] / "results" / "workload_rev3.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:len(res[0]) + 4]))
