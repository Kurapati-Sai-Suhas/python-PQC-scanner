"""H4 flip-rate analysis (run specification H-6; owner decisions G08, TA04, TA05). Pre-specified secondary/descriptive
analysis; no confirmatory or family-wise claim. The frozen tool registry is pqscan/bench/h4.py (not changed here).

Data: Dataset A base-variant pairs (b, o): base case b's identity instance and its variant under operator o.
Outcomes per tool and site: a classification outcome (None = no finding, else the tool's reported category) and a
recommendation outcome (action, rec_class) in the common vocabulary; EXECUTION_FAILURE marks a failed run.

* N(o, j): pairs on which tool j ran on both instances; failure pairs are counted separately and excluded.
* FR_cls(o, j), FR_rec(o, j) with Wilson 95% intervals; the same N(o, j) for both.
* Part 1 (TA04: per-tool quantifier): for every baseline j in PART1_BASELINES, some operator o (loaded-key included)
  has FR_cls >= 0.30 or FR_rec >= 0.30. Reported descriptively: whether ONE operator meets this for all eight.
  Population: all pairs (TA05).
* Prediction (loaded-key, cross-function): reported per operator as confirmed or not (threshold met for every
  Part 1 baseline under that operator).
* Part 2: proposed analyser, alias-import and wrapper-function separately; a pair is invariant only if neither
  outcome flipped; met iff the invariant share >= 0.90 for both operators. TA05: primary population = the
  synthetic-holdout base cases; all pairs reported as well. loaded-key never enters invariance.
* Eligible-only recommendation-flip sensitivity FR_rec^elig, reported separately, never substituted.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Mapping, Sequence

from .h4 import PART1_BASELINES, PROPOSED_ANALYSER, REPORTED_SEPARATELY
from .stats import wilson

OPERATORS = ("alias-import", "wrapper-function", "class-method", "cross-function", "dict-dispatch", "loaded-key")
PART2_OPERATORS = ("alias-import", "wrapper-function")
PREDICTED = ("loaded-key", "cross-function")
FLIP_THRESHOLD = Fraction(3, 10)
INVARIANCE_THRESHOLD = Fraction(9, 10)
FAIL = "EXECUTION_FAILURE"


def pairs(sites: Sequence[Mapping]) -> list[dict]:
    """Base-variant pairs from Dataset A site records (base_case, transformation, site_id, eligible)."""
    ident = {s["base_case"]: s for s in sites if s["transformation"] == "identity"}
    out = []
    for s in sites:
        o = s["transformation"]
        if o == "identity":
            continue
        if o not in OPERATORS:
            raise ValueError(f"unknown operator {o}")
        b = ident.get(s["base_case"])
        if b is None:
            raise ValueError(f"{s['site_id']}: no identity instance for base case {s['base_case']}")
        out.append({"base_case": s["base_case"], "operator": o, "identity": b["site_id"], "variant": s["site_id"],
                    "eligible": str(b["eligible"]).lower() in ("true", "yes")})
    return out


def _rate(k: int, n: int) -> dict:
    return {"k": k, "n": n, "rate": (k / n) if n else None, "wilson95": list(wilson(k, n)) if n else None}


def flips(prs: Sequence[Mapping], outcomes: Mapping[str, Mapping], op: str) -> dict:
    """`outcomes[site_id]` = {"cls": str | None, "rec": (action, rec_class)} or {"rec": (FAIL, ...)}."""
    sel = [p for p in prs if p["operator"] == op]
    ran, failed = [], 0
    for p in sel:
        a, b = outcomes.get(p["identity"]), outcomes.get(p["variant"])
        if a is None or b is None or a["rec"][0] == FAIL or b["rec"][0] == FAIL:
            failed += 1
        else:
            ran.append((p, a, b))
    cls = sum(1 for _, a, b in ran if a["cls"] != b["cls"])
    rec = sum(1 for _, a, b in ran if tuple(a["rec"]) != tuple(b["rec"]))
    inv = sum(1 for _, a, b in ran if a["cls"] == b["cls"] and tuple(a["rec"]) == tuple(b["rec"]))
    el = [(a, b) for p, a, b in ran if p["eligible"]]
    return {"operator": op, "pairs": len(sel), "execution_failure_pairs": failed,
            "FR_cls": _rate(cls, len(ran)), "FR_rec": _rate(rec, len(ran)), "invariant": _rate(inv, len(ran)),
            "FR_rec_eligible_only": _rate(sum(1 for a, b in el if tuple(a["rec"]) != tuple(b["rec"])), len(el))}


def _meets(f: dict) -> bool | None:
    if f["FR_cls"]["n"] == 0:
        return None
    n = f["FR_cls"]["n"]
    return Fraction(f["FR_cls"]["k"], n) >= FLIP_THRESHOLD or Fraction(f["FR_rec"]["k"], n) >= FLIP_THRESHOLD


def analyse(sites: Sequence[Mapping], outcomes_by_tool: Mapping[str, Mapping[str, Mapping]],
            split_of_base: Mapping[str, str]) -> dict:
    """`split_of_base`: base_case -> 'synthetic-dev' | 'synthetic-holdout' (benchmark/synthetic/manifest.json)."""
    prs = pairs(sites)
    table = {j: {o: flips(prs, outcomes_by_tool[j], o) for o in OPERATORS}
             for j in outcomes_by_tool}
    part1 = {}
    for j in PART1_BASELINES:
        if j not in table:
            part1[j] = {"meets": None, "reason": "no results"}
            continue
        per = {o: _meets(table[j][o]) for o in OPERATORS}
        vals = list(per.values())
        meets = True if any(vals) else (None if any(v is None for v in vals) else False)
        part1[j] = {"meets": meets, "by_operator": per}
    if any(v["meets"] is None for v in part1.values()):
        p1 = "NOT ASSESSABLE"
    else:
        p1 = "MET" if all(v["meets"] for v in part1.values()) else "NOT MET"
    have = all(j in table for j in PART1_BASELINES)
    def _all(o):
        if not have:
            return None
        v = [_meets(table[j][o]) for j in PART1_BASELINES]
        return None if any(x is None for x in v) else all(v)
    one_op = {o: _all(o) for o in OPERATORS}
    pred = {o: one_op[o] for o in PREDICTED}

    def part2(prs_sub):
        if PROPOSED_ANALYSER not in outcomes_by_tool:
            return {"status": "NOT ASSESSABLE", "reason": "no results for the proposed analyser"}
        per = {o: flips(prs_sub, outcomes_by_tool[PROPOSED_ANALYSER], o) for o in PART2_OPERATORS}
        if any(per[o]["invariant"]["n"] == 0 for o in PART2_OPERATORS):
            st = "NOT ESTIMABLE"
        else:
            st = ("MET" if all(Fraction(per[o]["invariant"]["k"], per[o]["invariant"]["n"]) >= INVARIANCE_THRESHOLD
                               for o in PART2_OPERATORS) else "NOT MET")
        return {"status": st, "by_operator": {o: {"invariant_share": per[o]["invariant"],
                                                  "classification_stability": 1 - per[o]["FR_cls"]["rate"]
                                                  if per[o]["FR_cls"]["rate"] is not None else None,
                                                  "recommendation_stability": 1 - per[o]["FR_rec"]["rate"]
                                                  if per[o]["FR_rec"]["rate"] is not None else None}
                                              for o in PART2_OPERATORS}}
    unknown = sorted({p["base_case"] for p in prs} - set(split_of_base))
    if unknown:
        raise ValueError(f"base cases without a split: {unknown[:5]}")
    holdout = [p for p in prs if split_of_base[p["base_case"]] == "synthetic-holdout"]
    return {"hypothesis": "H4 (secondary, descriptive)",
            "part1": {"status": p1, "population": "all pairs (TA05)", "quantifier": "per tool (TA04)",
                      "baselines": part1, "one_operator_for_all_eight_TA04_descriptive": one_op,
                      "prediction_loaded_key_cross_function": pred},
            "part2": {"primary_holdout_TA05": part2(holdout), "all_pairs": part2(prs)},
            "flip_tables": table, "reported_separately": [t for t in REPORTED_SEPARATELY if t in table],
            "note": "loaded-key is an evidence-condition change, not a semantics-preserving transformation"}
