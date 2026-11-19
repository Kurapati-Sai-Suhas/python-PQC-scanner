"""G10 additional pre-F1 calibration of the signed coverage-gap guard (owner decision G10, 19 Nov 2026;
analysis plan v1.0.1-r3 Sec. 11.7).

    python scripts/g10_calibration.py           # full run -> docs/implementation/acceptance/g10_calibration.{json,md}
    python scripts/g10_calibration.py --quick   # smoke run -> *_quick files

Procedure under test: UNCHANGED production H2 single-comparison procedure, through the acceptance driver's
`task_single` (scripts/phase3_acceptance.py; pqscan.bench.h2 bootstrap with random tie keys, signed repository-balanced
coverage-gap guard g < 1/10 -> min(1, 2p), B = 1,000). Simulator: the archived planning model (calib_matching_v4), as in
acceptance. Nothing in the E30 calibration closure is modified; the existing acceptance outputs are not touched.

Scenarios (pre-specified before running): repositories with HETEROGENEOUS coverage gaps, each repository calibrated to
delta_r = 0 (null) with the acceptance tuning (qF):
  G10a  positive mean gap, two repositories near zero (kink)               mean population gap about +0.21
  G10b  positive mean gap, one repository with a negative gap               about +0.20
  G10c  opposite-direction gaps that cancel (3 positive, 3 negative, 1 zero) about  0.00
  G10d  plausible heterogeneous coverage (F 0.60-0.95, M 0.30-0.75 on T; one negative, one zero gap)
  G10e  positive mean near the threshold (5 positive, 2 negative)           about +0.11
Power cells (delta_r = +0.04 in every repository, the largest effect the qF tuning reaches in every repository of these patterns): G10a, G10b, G10d.
Criterion (as acceptance, plan Sec. 11.2): every Type I rate at a/3, a/2, a <= level + 3 * sqrt(level (1 - level) / n).
If any null cell fails: work stops before F1 and a formally versioned correction is proposed; nothing is changed here.
Random streams: numpy default_rng([20261113, 21, tid, chunk]) with tid 9001-9008 (disjoint from acceptance's tids).
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import phase3_acceptance as ACC  # noqa: E402  (read-only: task_single, guarded_p, LEVELS, TAGS, mcse)

C = ACC.C
OUT = ROOT / "docs" / "implementation" / "acceptance"
TID0 = 9001


def _pos():
    return C.repo(C.base_F(), C.base_M())                                       # gap about +0.29 (acceptance S01)


def _zero():
    return C.repo(C.base_F(), C.base_M(rT=0.85, rN=0.10, rI=0.30))              # gap about 0 (acceptance S04 kink)


def _neg():
    return C.repo(C.base_F(rT=0.50, rI=0.10), C.base_M(rT=0.90, rI=0.30))       # gap about -0.33 (acceptance S05)


def scenarios() -> list[dict]:
    het = [(0.95, 0.40), (0.85, 0.45), (0.80, 0.30), (0.70, 0.65), (0.60, 0.70), (0.90, 0.60), (0.75, 0.75)]
    S = [
        dict(id="G10a", desc="positive mean gap; two repositories near zero (kink)", repos=[_pos()] * 5 + [_zero()] * 2),
        dict(id="G10b", desc="positive mean gap; one repository with a negative gap", repos=[_pos()] * 6 + [_neg()]),
        dict(id="G10c", desc="opposite-direction gaps that cancel (3 positive, 3 negative, 1 zero)",
             repos=[_pos()] * 3 + [_neg()] * 3 + [_zero()]),
        dict(id="G10d", desc="plausible heterogeneous coverage (one negative, one zero gap)",
             repos=[C.repo(C.base_F(rT=a), C.base_M(rT=c)) for a, c in het]),
        dict(id="G10e", desc="positive mean near the guard threshold (5 positive, 2 negative)", repos=[_pos()] * 5 + [_neg()] * 2),
    ]
    for sc in S:
        sc.update(targets=[0.0] * 7, tunes=["qF"] * 7, d0=0.0, mode="fixed", tau=0.0)
    return S


def power_scenarios() -> list[dict]:
    out = []
    for sc in scenarios():
        if sc["id"] in ("G10a", "G10b", "G10d"):
            p = dict(sc, id=sc["id"] + "-power", desc=sc["desc"] + "; delta_r = +0.04 everywhere (power; larger effects are unreachable by the qF tuning in some repositories of these patterns)", targets=[0.04] * 7)
            out.append(p)
    return out


def population_gaps(sc: dict) -> list[float]:
    return [round(float(C.coverage(r, r["F"]) - C.coverage(r, r["M"])), 4) for r in sc["repos"]]


def run(reps_null: int, reps_power: int, B: int, chunks: int) -> dict:
    t0 = time.time()
    tasks, meta, tid = [], {}, TID0
    for kind, scs, reps in (("null", scenarios(), reps_null), ("power", power_scenarios(), reps_power)):
        for sc in scs:
            gaps = population_gaps(sc)
            meta[sc["id"]] = {"kind": kind, "desc": sc["desc"], "tid": tid, "population_gaps": gaps,
                              "population_mean_gap": round(sum(gaps) / len(gaps), 4)}
            for ch in range(chunks):
                tasks.append(("type1", tid, sc, reps // chunks, B, ch))
            tid += 1
    with ProcessPoolExecutor(max_workers=16) as ex:
        rows = list(ex.map(ACC.task_single, tasks))
    res = {}
    for r in rows:
        a = res.setdefault(r["id"], {"n": 0, "guard": 0, **{f"rej_{t}": 0 for t in ACC.TAGS}})
        for k in a:
            a[k] += r[k]
    fails = []
    for k, a in res.items():
        n = a["n"]
        rates = [a[f"rej_{t}"] / n for t in ACC.TAGS]
        a.update(meta[k], rates=dict(zip(ACC.TAGS, rates)), guard_share=a["guard"] / n,
                 limits=dict(zip(ACC.TAGS, [lv + 3 * ACC.mcse(lv, n) for lv in ACC.LEVELS])))
        if meta[k]["kind"] == "null":
            a["pass"] = all(r <= lim for r, lim in zip(rates, a["limits"].values()))
            if not a["pass"]:
                fails.append(k)
    worst = max(((k, a["rates"][ACC.TAGS[-1]]) for k, a in res.items() if a["kind"] == "null"), key=lambda x: x[1])
    import numpy, scipy, platform  # noqa: E401
    return {"procedure": "production H2 single comparison via scripts/phase3_acceptance.py task_single (guard unchanged)",
            "B": B, "reps_null": reps_null, "reps_power": reps_power, "levels": dict(zip(ACC.TAGS, ACC.LEVELS)),
            "criterion": "rate <= level + 3*sqrt(level*(1-level)/n) at a/3, a/2, a (plan Sec. 11.2)",
            "seed_rule": "numpy default_rng([20261113, 21, tid, chunk]); tid listed per scenario",
            "results": res, "worst_null_rate_at_a": {"scenario": worst[0], "rate": worst[1]},
            "all_null_pass": not fails, "failed": fails,
            "environment": {"python": sys.version.split()[0], "numpy": numpy.__version__, "scipy": scipy.__version__,
                            "platform": platform.platform()},
            "runtime_minutes": round((time.time() - t0) / 60, 1)}


def write(res: dict, quick: bool) -> None:
    sfx = "_quick" if quick else ""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"g10_calibration{sfx}.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    L = [f"# G10 additional calibration of the signed coverage-gap guard{' (quick)' if quick else ''}", "",
         f"Procedure: {res['procedure']}. B = {res['B']}. Criterion: {res['criterion']}. Seeds: {res['seed_rule']}.", "",
         f"**Overall (null cells): {'PASS' if res['all_null_pass'] else 'FAIL: ' + ', '.join(res['failed']) + ' (stop before F1)'}**", "",
         "| id | kind | description | population repository gaps (F − M) | mean gap | n | a/3 | a/2 | a | P(guard on) | result |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, a in res["results"].items():
        r = a["rates"]
        L.append(f"| {k} | {a['kind']} | {a['desc']} | {', '.join(f'{g:+.2f}' for g in a['population_gaps'])} | "
                 f"{a['population_mean_gap']:+.3f} | {a['n']} | {r['a3']:.4f} | {r['a2']:.4f} | {r['a1']:.4f} | "
                 f"{a['guard_share']:.3f} | {('pass' if a['pass'] else 'FAIL') if a['kind'] == 'null' else 'power'} |")
    L += ["", f"Worst null rate at a = 0.025: {res['worst_null_rate_at_a']['rate']:.4f} ({res['worst_null_rate_at_a']['scenario']}).",
          f"Environment: {res['environment']}; runtime {res['runtime_minutes']} min.",
          "Planning-model simulation: evidence about the procedure under assumed configurations, not about scanner accuracy."]
    (OUT / f"g10_calibration{sfx}.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if any(a != "--quick" for a in args):
        print(__doc__)
        return 0 if set(args) <= {"-h", "--help", "--quick"} else 2
    quick = "--quick" in args
    res = run(40, 20, 100, 1) if quick else run(10_000, 2_000, 1_000, 4)
    write(res, quick)
    print("PASS" if res["all_null_pass"] else f"FAIL {res['failed']}", f"in {res['runtime_minutes']} min")
    return 0


if __name__ == "__main__":
    sys.exit(main())
