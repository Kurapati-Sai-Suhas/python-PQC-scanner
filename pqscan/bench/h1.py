"""H1 analysis (run specification H-2 and H-3; owner decision TA08, revision v1.0.5-r6). Pre-F1 code; never run on the
test split before F2.

H1a: share of eligible primary-set sites whose role does NOT follow from the method/algorithm name. Numerator:
eligible sites with obvious_from_name = false, UNKNOWN/INDETERMINATE included (TA08). Denominator: all eligible sites.
Met iff the point estimate >= 0.25. Reported alongside: the evidence_needed categories of the numerator and a
sensitivity that excludes INDETERMINATE sites.

H1b: for every tool in the H1b set, (harmful + UNDECIDED + UNJUSTIFIED) / n_exec >= 0.10 on point estimates, where
harmful = INCORRECT with a harm category and n_exec = eligible sites on which the tool ran (execution failures are
reported separately by count). Wilson 95% intervals are always reported. Thresholds are the adopted ones (H-2).
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from typing import Iterable, Mapping, Sequence

from .stats import wilson

H1A_THRESHOLD = Fraction(1, 4)
H1B_THRESHOLD = Fraction(1, 10)
H1B_SET = ("pqcheck", "pqc-audit", "PostQuant", "qsafe", "QSA-regex", "pqblocks-scan")
H1B_REPORTED_SEPARATELY = ("pqscan:B1-algorithm", "pqscan:B2-method-args")


def _true(v) -> bool:
    return str(v).strip().lower() in ("true", "yes", "1")


def _rate(k: int, n: int) -> dict:
    if n == 0:
        return {"k": 0, "n": 0, "rate": None, "wilson95": None}
    return {"k": k, "n": n, "rate": k / n, "wilson95": list(wilson(k, n))}


def h1a(sites: Iterable[Mapping]) -> dict:
    """`sites`: owner-final labels of the primary-set candidates (eligible, obvious_from_name, evidence_needed,
    assessability). Ineligible sites are ignored (their obvious_from_name is null by schema v1.1)."""
    elig = [s for s in sites if _true(s["eligible"])]
    for s in elig:
        if not isinstance(s.get("obvious_from_name"), bool):
            raise ValueError(f"{s.get('site_id')}: eligible site without a boolean obvious_from_name")
    beyond = [s for s in elig if s["obvious_from_name"] is False]
    prim = _rate(len(beyond), len(elig))
    det = [s for s in elig if s.get("assessability") != "INDETERMINATE"]
    sens = _rate(sum(1 for s in det if s["obvious_from_name"] is False), len(det))
    status = ("NOT ESTIMABLE" if prim["rate"] is None
              else "MET" if Fraction(prim["k"], prim["n"]) >= H1A_THRESHOLD else "NOT MET")
    return {"hypothesis": "H1a", "threshold": str(H1A_THRESHOLD), "primary": prim, "status": status,
            "evidence_needed_in_numerator": dict(sorted(Counter(str(s.get("evidence_needed")) for s in beyond).items())),
            "sensitivity_excluding_indeterminate": sens,
            "definition": "numerator obvious_from_name = false among eligible sites (TA08, r6)"}


BAD = ("UNDECIDED", "UNJUSTIFIED")


def _bad(row: Mapping) -> bool:
    return (row["judgment"] == "INCORRECT" and bool(row.get("harm_category"))) or row["judgment"] in BAD


def h1b(rows: Sequence[Mapping], tools: Sequence[str] = H1B_SET,
        separately: Sequence[str] = H1B_REPORTED_SEPARATELY) -> dict:
    """`rows`: judged rows (pqscan.bench.run row format). Only eligible sites enter."""
    def one(tool):
        rs = [r for r in rows if r["method"] == tool and _true(r["eligible"])]
        ran = [r for r in rs if r["judgment"] != "EXECUTION_FAILURE"]
        out = _rate(sum(1 for r in ran if _bad(r)), len(ran))
        out["execution_failures"] = len(rs) - len(ran)
        out["breakdown"] = dict(Counter("HARMFUL" if r["judgment"] == "INCORRECT" and r.get("harm_category")
                                        else r["judgment"] for r in ran if _bad(r)))
        out["meets"] = None if out["rate"] is None else Fraction(out["k"], out["n"]) >= H1B_THRESHOLD
        return out
    per = {t: one(t) for t in tools}
    if any(v["meets"] is None for v in per.values()):
        status = "NOT ASSESSABLE"
    else:
        status = "MET" if all(v["meets"] for v in per.values()) else "NOT MET"
    return {"hypothesis": "H1b", "threshold": str(H1B_THRESHOLD), "tools": per, "status": status,
            "reported_separately": {t: one(t) for t in separately}}
