"""Equal-coverage matching for H2 (phase3_analysis_plan.md Sec. 3-6; decisions V12, V22; R4-19 items 9 and 12).

Written from the adopted analysis plan. The independent reference implementation lives in
docs/proposals/v1.0.4/rev4/scripts/matching_ref_v4.py; tests/test_h2_differential.py links the two.

Per comparison and repository:
* the common evaluable set C_r = eligible sites where both arms ran (EXECUTION_FAILURE partition, Sec. 6);
* k_r = min(R_F, R_M); the arm with more RECOMMENDs withdraws the excess, lowest evidence tier first, SHA-256 of
  "<seed>|<comparison>|<repository>|<site_id>" within a tier (ranking-free variant: SHA-256 order only);
* a withdrawn RECOMMEND is judged as ABSTAIN by the frozen judge;
* the primary estimate is the exact tie-average: every recommendation in the boundary tier of the withdrawing arm
  is withdrawn with probability j/m (ranking-free: e/R for every recommendation).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

from .judge import judge

TIERS = ("T0", "T1", "T2", "T3")
TIER_INDEX = {t: i for i, t in enumerate(TIERS)}
ACTIONS = ("RECOMMEND", "FLAG_NO_TARGET", "ABSTAIN", "NO_FINDING", "EXECUTION_FAILURE")
PRIMARY_SEED = "20261113"
SENSITIVITY_SEEDS = tuple(f"{PRIMARY_SEED}-S{i:03d}" for i in range(1, 101))


class MatchingError(ValueError):
    pass


@dataclass(frozen=True)
class Output:
    """One arm's decision at one site, in the common vocabulary of scoring_policy.md."""
    action: str
    rec_class: str = "NONE"
    tier: str | None = None


def _check_output(o: Output, where: str) -> None:
    if o.action not in ACTIONS:
        raise MatchingError(f"{where}: unknown action {o.action!r}")
    if o.action == "RECOMMEND":
        if o.tier not in TIER_INDEX:
            raise MatchingError(f"{where}: RECOMMEND without an evidence tier T0-T3")
        if o.rec_class in (None, "NONE"):
            raise MatchingError(f"{where}: RECOMMEND without a recommended class")


def tie_key(seed: str, comparison: str, repo: str, site_id: str) -> str:
    return hashlib.sha256(f"{seed}|{comparison}|{repo}|{site_id}".encode("utf-8")).hexdigest()


def correct(label: Mapping, o: Output) -> int:
    return int(judge(label, o.action, o.rec_class).judgment == "CORRECT")


WITHDRAWN = Output("ABSTAIN", "NONE", None)


# --------------------------------------------------------------------------------------------- execution partition
def partition(site_ids: Sequence[str], f: Sequence[Output], m: Sequence[Output], *, require_concordant: bool) -> dict:
    out = {"both": [], "f_only": [], "m_only": [], "neither": []}
    for sid, a, b in zip(site_ids, f, m):
        fa, ma = a.action != "EXECUTION_FAILURE", b.action != "EXECUTION_FAILURE"
        out["both" if fa and ma else "f_only" if fa else "m_only" if ma else "neither"].append(sid)
    if require_concordant and (out["f_only"] or out["m_only"]):
        raise MatchingError("discordant EXECUTION_FAILURE between Module C arms of one comparison: software defect; "
                            f"F only {out['f_only'][:3]}, M only {out['m_only'][:3]}")
    return out


# --------------------------------------------------------------------------------------------- matching
@dataclass
class Match:
    k: int
    R_f: int
    R_m: int
    withdraw_f: list[str] = field(default_factory=list)       # in withdrawal order (seeded)
    withdraw_m: list[str] = field(default_factory=list)
    prob_f: dict[str, float] = field(default_factory=dict)      # exact tie-average withdrawal probabilities
    prob_m: dict[str, float] = field(default_factory=dict)
    boundary: str | None = None
    boundary_size: int = 0
    boundary_withdrawn: int = 0


def _withdraw(recs: list[tuple[str, Output]], excess: int, seed: str, comparison: str, repo: str, ranking: bool):
    if excess <= 0:
        return [], {}, None, 0, 0
    rank = (lambda o: TIER_INDEX[o.tier]) if ranking else (lambda o: 0)
    ordered = sorted(recs, key=lambda x: (rank(x[1]), tie_key(seed, comparison, repo, x[0])))
    chosen = [sid for sid, _ in ordered[:excess]]
    # exact tie-average: withdraw all tiers strictly below the boundary tier, a uniform share inside it
    groups: dict[int, list[str]] = {}
    for sid, o in recs:
        groups.setdefault(rank(o), []).append(sid)
    probs, left = {}, excess
    boundary = None
    for r in sorted(groups):
        g = groups[r]
        if left <= 0:
            probs.update({s: 0.0 for s in g})
        elif left >= len(g):
            probs.update({s: 1.0 for s in g})
            left -= len(g)
            if left == 0:
                boundary = (r, len(g), len(g))
        else:
            probs.update({s: left / len(g) for s in g})
            boundary = (r, len(g), left)
            left = 0
    label = (TIERS[boundary[0]] if ranking else "ANY") if boundary else None
    return chosen, probs, label, (boundary[1] if boundary else 0), (boundary[2] if boundary else 0)


def match(site_ids: Sequence[str], f: Sequence[Output], m: Sequence[Output], *, comparison: str, repo: str,
          seed: str = PRIMARY_SEED, ranking: bool = True) -> Match:
    """Label-free matching on the common evaluable set (no EXECUTION_FAILURE allowed here)."""
    if len(set(site_ids)) != len(site_ids):
        raise MatchingError("duplicate site IDs")
    if not (len(site_ids) == len(f) == len(m)):
        raise MatchingError("arm outputs and sites differ in length")
    for sid, a, b in zip(site_ids, f, m):
        _check_output(a, f"F/{sid}")
        _check_output(b, f"M/{sid}")
        if "EXECUTION_FAILURE" in (a.action, b.action):
            raise MatchingError(f"{sid}: EXECUTION_FAILURE must be removed before matching (common evaluable set)")
    rf = [(s, o) for s, o in zip(site_ids, f) if o.action == "RECOMMEND"]
    rm = [(s, o) for s, o in zip(site_ids, m) if o.action == "RECOMMEND"]
    k = min(len(rf), len(rm))
    res = Match(k=k, R_f=len(rf), R_m=len(rm))
    for recs, excess, side in ((rf, len(rf) - k, "f"), (rm, len(rm) - k, "m")):
        chosen, probs, b, size, wd = _withdraw(recs, excess, seed, comparison, repo, ranking)
        setattr(res, f"withdraw_{side}", chosen)
        setattr(res, f"prob_{side}", {s: probs.get(s, 0.0) for s, _ in recs})
        if chosen:
            res.boundary, res.boundary_size, res.boundary_withdrawn = b, size, wd
    return res


def matching_record(site_ids, f, m, mt: Match, comparison: str, repo: str) -> dict:
    """The label-free matching output that is hashed before labels are joined (plan Sec. 4.5)."""
    rec = {"comparison": comparison, "repo": repo, "k": mt.k, "R_f": mt.R_f, "R_m": mt.R_m,
           "withdraw_f": mt.withdraw_f, "withdraw_m": mt.withdraw_m,
           "sites": [[s, a.action, a.rec_class, a.tier, b.action, b.rec_class, b.tier] for s, a, b in zip(site_ids, f, m)]}
    import json
    rec["sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode("utf-8")).hexdigest()
    return rec


# --------------------------------------------------------------------------------------------- per-repository result
def _expected(labels, outs, probs):
    """(expected correct total, expected correct kept REC, expected incorrect, decomposition) of one arm."""
    tot = rec_ok = harm = 0.0
    dec = {"REC": 0.0, "WITHDRAWN": 0.0, "FLAG": 0.0, "ABSTAIN": 0.0, "NO_FINDING": 0.0}
    cat = {"FLAG_NO_TARGET": "FLAG", "ABSTAIN": "ABSTAIN", "NO_FINDING": "NO_FINDING"}
    for lab, o, sid in zip(labels, outs, [l["site_id"] for l in labels]):
        if o.action == "RECOMMEND":
            w = probs.get(sid, 0.0)
            ck, cw = correct(lab, o), correct(lab, WITHDRAWN)
            bad = int(judge(lab, o.action, o.rec_class).judgment == "INCORRECT")
            tot += (1 - w) * ck + w * cw
            rec_ok += (1 - w) * ck
            harm += (1 - w) * bad
            dec["REC"] += (1 - w) * ck
            dec["WITHDRAWN"] += w * cw
        else:
            c = correct(lab, o)
            tot += c
            harm += int(judge(lab, o.action, o.rec_class).judgment == "INCORRECT")
            dec[cat[o.action]] += c
    return tot, rec_ok, harm, dec


def site_arrays(labels: Sequence[Mapping], outs: Sequence[Output]) -> tuple[np.ndarray, ...]:
    """(rec, tier index or -1, correct if kept, correct if withdrawn) for the bootstrap."""
    rec = np.array([o.action == "RECOMMEND" for o in outs], dtype=bool)
    tier = np.array([TIER_INDEX[o.tier] if o.action == "RECOMMEND" else -1 for o in outs], dtype=np.int64)
    ck = np.array([correct(l, o) for l, o in zip(labels, outs)], dtype=np.int8)
    cw = np.array([correct(l, WITHDRAWN) for l in labels], dtype=np.int8)
    return rec, tier, ck, cw


def repository_result(labels: Sequence[Mapping], f: Sequence[Output], m: Sequence[Output], *, comparison: str,
                      repo: str, require_concordant: bool = True, seeds: Sequence[str] = SENSITIVITY_SEEDS) -> dict:
    """Everything plan Sec. 5-6 and 10 report for one repository. `labels` are the repository's primary-set
    eligible sites (owner-final labels; site_id, eligible, gt_role, assessability, hybrid_component; optional
    'stratum'). Labels are used only after matching, for scoring."""
    ids = [l["site_id"] for l in labels]
    for l in labels:
        if str(l["eligible"]).lower() not in ("yes", "true"):
            raise MatchingError(f"{l['site_id']}: only primary-set eligible sites enter H2")
    part = partition(ids, f, m, require_concordant=require_concordant)
    keep = set(part["both"])
    L = [l for l in labels if l["site_id"] in keep]
    F = [o for l, o in zip(labels, f) if l["site_id"] in keep]
    M = [o for l, o in zip(labels, m) if l["site_id"] in keep]
    cid = [l["site_id"] for l in L]
    n_all, n = len(labels), len(L)
    out = {"comparison": comparison, "repo": repo, "n_eligible": n_all, "n_common": n,
           "partition": {k: len(v) for k, v in part.items()}, "failed_sites": part,
           "fail_f": len(part["m_only"]) + len(part["neither"]), "fail_m": len(part["f_only"]) + len(part["neither"]),
           "n_indeterminate_common": sum(correct(l, WITHDRAWN) for l in L),
           "strata": {s: sum(l.get("stratum") == s for l in L) for s in ("S1-app", "S1-nonapp")},
           "estimable": n >= 1}
    if n == 0:
        out.update(k=0, R_f=0, R_m=0, delta_ta=None)
        return out
    mt = match(cid, F, M, comparison=comparison, repo=repo)
    mt_free = match(cid, F, M, comparison=comparison, repo=repo, ranking=False)
    xf, rf_ok, hf, dec_f = _expected(L, F, mt.prob_f)
    ym, rm_ok, hm, dec_m = _expected(L, M, mt.prob_m)
    xf0, _, _, _ = _expected(L, F, mt_free.prob_f)
    ym0, _, _, _ = _expected(L, M, mt_free.prob_m)
    nat_f, nat_m = sum(correct(l, o) for l, o in zip(L, F)), sum(correct(l, o) for l, o in zip(L, M))

    def seeded(seed: str):
        s_mt = match(cid, F, M, comparison=comparison, repo=repo, seed=seed)
        wf, wm = set(s_mt.withdraw_f), set(s_mt.withdraw_m)
        X = [correct(l, WITHDRAWN if s in wf else o) for l, o, s in zip(L, F, cid)]
        Y = [correct(l, WITHDRAWN if s in wm else o) for l, o, s in zip(L, M, cid)]
        return X, Y, s_mt

    X, Y, s_mt = seeded(PRIMARY_SEED)
    kept_f = [s for s, o in zip(cid, F) if o.action == "RECOMMEND" and s not in set(s_mt.withdraw_f)]
    kept_m = [s for s, o in zip(cid, M) if o.action == "RECOMMEND" and s not in set(s_mt.withdraw_m)]
    det = lambda l: l["assessability"] == "DETERMINATE"
    out.update(
        k=mt.k, R_f=mt.R_f, R_m=mt.R_m, cov_f=mt.R_f / n, cov_m=mt.R_m / n, matched_cov=mt.k / n,
        withdrawn_f=len(mt.withdraw_f), withdrawn_m=len(mt.withdraw_m), boundary_tier=mt.boundary,
        boundary_size=mt.boundary_size, boundary_withdrawn=mt.boundary_withdrawn,
        both_rec=len(set(kept_f) & set(kept_m)), f_only_rec=len(set(kept_f) - set(kept_m)),
        m_only_rec=len(set(kept_m) - set(kept_f)),
        delta_ta=(xf - ym) / n, delta_rankfree=(xf0 - ym0) / n, delta_nat=(nat_f - nat_m) / n,
        correct_f=xf, correct_m=ym, correct_f_nat=nat_f, correct_m_nat=nat_m, incorrect_f=hf, incorrect_m=hm,
        prec_matched_f=(rf_ok / mt.k if mt.k else None), prec_matched_m=(rm_ok / mt.k if mt.k else None),
        prec_nat_f=(sum(correct(l, o) for l, o in zip(L, F) if o.action == "RECOMMEND") / mt.R_f if mt.R_f else None),
        prec_nat_m=(sum(correct(l, o) for l, o in zip(L, M) if o.action == "RECOMMEND") / mt.R_m if mt.R_m else None),
        rec_correctness_frozen_f=_frozen_rc(L, F, det), rec_correctness_frozen_m=_frozen_rc(L, M, det),
        decomposition={k: (dec_f[k], dec_m[k]) for k in dec_f},
        seeded={"delta": (sum(X) - sum(Y)) / n, "b": sum(1 for x, y in zip(X, Y) if x and not y),
                "c": sum(1 for x, y in zip(X, Y) if y and not x), "X": X, "Y": Y,
                "withdraw_f": s_mt.withdraw_f, "withdraw_m": s_mt.withdraw_m},
        seed_deltas=[(lambda r: (sum(r[0]) - sum(r[1])) / n)(seeded(s)) for s in seeds],
        feasible=mt.k >= 5,
        matching_record=matching_record(cid, F, M, mt, comparison, repo),
        arrays=(site_arrays(L, F), site_arrays(L, M)),
        site_strata=[l.get("stratum") for l in L])
    # execution-failure sensitivities (plan Sec. 6), on the full eligible denominator
    lab = {l["site_id"]: l for l in labels}
    fo = {l["site_id"]: o for l, o in zip(labels, f)}
    mo = {l["site_id"]: o for l, o in zip(labels, m)}
    xf_extra = sum(correct(lab[s], fo[s]) for s in part["f_only"])
    ym_extra = sum(correct(lab[s], mo[s]) for s in part["m_only"])
    base = out["delta_ta"] * n + xf_extra - ym_extra
    out["delta_sf1"] = base / n_all
    out["delta_sf2"] = ((base - out["fail_f"]) / n_all, (base + out["fail_m"]) / n_all)
    return out


def _frozen_rc(L, outs, det):
    """Frozen 'recommendation correctness' at natural coverage: CORRECT / (eligible DETERMINATE sites with RECOMMEND)."""
    pairs = [(l, o) for l, o in zip(L, outs) if o.action == "RECOMMEND" and det(l)]
    return (sum(correct(l, o) for l, o in pairs) / len(pairs)) if pairs else None
