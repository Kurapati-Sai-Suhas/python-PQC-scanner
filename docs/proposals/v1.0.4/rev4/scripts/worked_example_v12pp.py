"""V12'' worked example (three repositories) and pilot (development) tables. PROPOSED, NOT ADOPTED. Not results.

    .venv/Scripts/python docs/proposals/v1.0.4/rev4/scripts/worked_example_v12pp.py

Writes ../results/worked_example_v12pp.md and ../results/pilot_v12pp.md. Every judgment comes from the frozen judge.
The pilot arms method+args+recv and method-only are derived from docs/dev/roles_on_pilot.csv with the policy's
role -> action mapping at threshold T0 (UNKNOWN -> ABSTAIN; KEY_MATERIAL_ONLY / PROTOCOL_CONFIG / approved hybrid ->
FLAG_NO_TARGET; otherwise RECOMMEND the role's family). The same derivation is checked against the recorded harness
rows for method+args and full, and must reproduce them exactly.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import matching_ref_v4 as MR
import worked_example_v4 as WE
from matching_ref_v4 import ArmOutput as A

OUT = Path(__file__).resolve().parents[1] / "results"
ROOT = MR.ROOT


def S(sid, role, ass, hyb="no"):
    return dict(site_id=sid, eligible="yes", gt_role=role, assessability=ass, hybrid_component=hyb)


EF = A("EXECUTION_FAILURE")
# Repository B: 8 eligible sites, two in a file that does not parse (both arms fail there: shared parser)
B_SITES = [S("b1", "SIGN", "DETERMINATE"), S("b2", "VERIFY", "DETERMINATE"), S("b3", "KEY_ESTABLISHMENT", "DETERMINATE"),
           S("b4", "UNKNOWN", "INDETERMINATE"), S("b5", "SIGN", "DETERMINATE"), S("b6", "PK_DECRYPT", "DETERMINATE"),
           S("b7", "SIGN", "DETERMINATE"), S("b8", "KEY_ESTABLISHMENT", "DETERMINATE")]
B_F = [A("RECOMMEND", "SIG", "T3"), A("RECOMMEND", "SIG", "T2"), A("RECOMMEND", "KEM", "T2"), A("RECOMMEND", "SIG", "T1"),
       A("ABSTAIN", "NONE", "T1"), A("RECOMMEND", "KEM", "T2"), EF, EF]
B_M = [A("RECOMMEND", "SIG", "T1"), A("RECOMMEND", "SIG", "T1"), A("ABSTAIN", "NONE", "T1"), A("ABSTAIN", "NONE", "T1"),
       A("RECOMMEND", "SIG", "T1"), A("ABSTAIN", "NONE", "T1"), EF, EF]
# Repository C: 6 eligible sites; the comparator never recommends (k = 0)
C_SITES = [S("c1", "SIGN", "DETERMINATE"), S("c2", "KEY_ESTABLISHMENT", "DETERMINATE"), S("c3", "UNKNOWN", "INDETERMINATE"),
           S("c4", "KEY_MATERIAL_ONLY", "DETERMINATE"), S("c5", "VERIFY", "DETERMINATE"), S("c6", "UNKNOWN", "INDETERMINATE")]
C_F = [A("RECOMMEND", "SIG", "T3"), A("RECOMMEND", "KEM", "T2"), A("RECOMMEND", "SIG", "T1"), A("FLAG_NO_TARGET", "NONE", "T2"),
       A("ABSTAIN", "NONE", "T1"), A("ABSTAIN", "NONE", "T2")]
C_M = [A("ABSTAIN", "NONE", "T1")] * 4 + [A("ABSTAIN", "NONE", "T0"), A("ABSTAIN", "NONE", "T1")]

REPOS = [("example", WE.EX_SITES, WE.EX_F, WE.EX_M), ("B", B_SITES, B_F, B_M), ("C", C_SITES, C_F, C_M)]


def _fmt_prec(t):
    c, n = t
    return f"{c}/{n}" + (f" = {c / n:.3f}" if n else "")


def report_rows(reps):
    head = ["| field | " + " | ".join(r["repo"] for r in reps) + " |", "|---|" + "---|" * len(reps)]
    fields = [
        ("eligible sites", lambda r: r["n_eligible"]),
        ("execution failures F / M", lambda r: f"{r['exec_fail_f']} / {r['exec_fail_m']}"),
        ("both ran / F only / M only / neither", lambda r: "{both} / {f_only} / {m_only} / {neither}".format(**r["partition"])),
        ("common evaluable sites n_r", lambda r: r["n_common"]),
        ("indeterminate sites (common)", lambda r: r["n_indeterminate_common"]),
        ("natural RECOMMEND R_F / R_M", lambda r: f"{r['R_f']} / {r['R_m']}"),
        ("natural coverage F / M", lambda r: f"{r['cov_f']:.3f} / {r['cov_m']:.3f}"),
        ("matched count k_r (coverage)", lambda r: f"{r['k']} ({r['matched_cov']:.3f})"),
        ("withdrawn F / M (boundary tier, withdrawn of tied)", lambda r: f"{r['withdrawn_f']} / {r['withdrawn_m']} ({r['boundary_tier']}, {r['withdrawn_at_boundary']} of {r['tied']})" if r['k'] < max(r['R_f'], r['R_m']) else "0 / 0"),
        ("recommended after matching: both / F only / M only", lambda r: f"{r['both_rec']} / {r['f_only_rec']} / {r['m_only_rec']}"),
        ("correct F / M (primary-seed table)", lambda r: f"{r['correct_f']} / {r['correct_m']}"),
        ("incorrect (harmful) F / M", lambda r: f"{r['incorrect_f']} / {r['incorrect_m']}"),
        ("natural correct F / M", lambda r: f"{r['correct_f_nat']} / {r['correct_m_nat']}"),
        ("precision natural F", lambda r: _fmt_prec(r["prec_f_nat"])),
        ("precision natural M", lambda r: _fmt_prec(r["prec_m_nat"])),
        ("precision matched F (primary-seed table)", lambda r: _fmt_prec(r["prec_f_matched"])),
        ("precision matched M (primary-seed table)", lambda r: _fmt_prec(r["prec_m_matched"])),
        ("precision matched, tie-averaged F / M", lambda r: "{:.2f}/{k} / {:.2f}/{k}".format(r["prec_matched_ta"][0][0], r["prec_matched_ta"][1][0], k=r["k"])),
        ("**delta_r, exact tie-average (primary)**", lambda r: f"**{r['delta_ta']:+.4f}**"),
        ("delta_r, primary-seed table", lambda r: f"{r['delta_seed']:+.4f}"),
        ("delta_r over 100 seeds: min / median / max", lambda r: f"{min(r['delta_seeds']):+.4f} / {np.median(r['delta_seeds']):+.4f} / {max(r['delta_seeds']):+.4f}"),
        ("delta_r ranking-free (tie-average)", lambda r: f"{r['delta_ta_rankfree'] + 0.0:+.4f}"),
        ("delta_r natural coverage", lambda r: f"{r['delta_nat']:+.4f}"),
        ("failure sensitivity S-F1 (failures not correct, all eligible)", lambda r: f"{r['delta_failures_not_correct']:+.4f}"),
        ("failure bounds S-F2", lambda r: "[{:+.4f}, {:+.4f}]".format(*r["delta_failure_bounds"])),
        ("matching-feasible (k_r >= 5)", lambda r: "yes" if r["k"] >= MR.K_MIN else "no"),
    ]
    return head + [f"| {name} | " + " | ".join(str(fn(r)) for r in reps) + " |" for name, fn in fields]


def pooled_block(reps, B=10_000):
    ns = [r["n_common"] for r in reps]
    ta = [r["delta_ta"] for r in reps]
    g = MR.coverage_gap([r["R_f"] for r in reps], [r["R_m"] for r in reps], ns)
    feas = MR.feasibility([r["k"] for r in reps], ns, feasible_min=len(reps))
    p, dist = MR.bootstrap_ta([r["arrays"] for r in reps], B=B, return_dist=True)
    terms = " + ".join(f"{(a - b)}/{n}" for a, b, n in zip([r["R_f"] for r in reps], [r["R_m"] for r in reps], ns))
    return [f"- Repository-balanced (primary): delta = ({' + '.join(f'{x:+.4f}' for x in ta)}) / {len(ta)} = **{MR.pooled(ta, ns):+.4f}**.",
            f"- Site-weighted (secondary): delta = ({' + '.join(f'{n} x {x:+.4f}' for n, x in zip(ns, ta))}) / {sum(ns)} = {MR.pooled(ta, ns, 'site'):+.4f}. "
            "The two differ because the common denominators differ.",
            f"- Signed coverage gap g = ({terms}) / {len(ns)} = {g} = {float(g):.4f}; guard {'ACTIVE (p doubled)' if MR.guard_active(g) else 'not active'} (active iff g < 1/10).",
            f"- Feasibility: k_r = {[r['k'] for r in reps]}, feasible = {feas['feasible']}, pooled matched coverage = {feas['pooled_matched_coverage']} = "
            f"{float(feas['pooled_matched_coverage']):.3f}. (The test-split gate needs >= 5 of 7 feasible and >= 0.20; with 3 illustrative "
            f"repositories the count condition is shown only as arithmetic.)",
            f"- Re-matching bootstrap of the tie-averaged estimate (B = {B}, seed 20261113, hypothetical data): one-sided p = {p:.4f}"
            f"{' -> guarded p = ' + format(MR.guarded_p(p, g), '.4f') if MR.guard_active(g) else ''}; 2.5th percentile of delta* = {np.quantile(dist, 0.025):+.4f}.",
            "- Holm is applied across the three comparisons H2-1, H2-3, H2-4; a single example comparison only shows its own p."]


def worked():
    reps = [MR.evaluate_repository(s, f, m, comparison="H2-1", repo=name) for name, s, f, m in REPOS]
    L = ["# V12'' worked example: three hypothetical repositories (PROPOSED, NOT ADOPTED; not results)", "",
         "Generated by `scripts/worked_example_v12pp.py` with `scripts/matching_ref_v4.py`; judgments from the frozen judge. "
         "Repository `example` (A) is the 12-site example of R4-03b. Repository B has two sites in a file that does not parse "
         "(both arms fail there: the Module C arms share one parser). Repository C: the comparator never recommends (k = 0).", "",
         "## Per-repository report (every field required by R4-14)", ""]
    L += report_rows(reps)
    L += ["", "## Pooled", ""] + pooled_block(reps)
    L += ["", "## Hand check of repository B", "",
          "- b7, b8: EXECUTION_FAILURE in both arms -> removed from the common set (n_B = 6), listed, and kept in the failure sensitivity.",
          "- Natural RECOMMEND: F on b1, b2, b3, b4, b6 (R_F = 5); M on b1, b2, b5 (R_M = 3); k = 3; F withdraws 2: b4 (T1) first, "
          "then one of the three tied T2 sites b2, b3, b6.",
          "- Tie-average: b4 withdrawn surely (indeterminate: UNJUSTIFIED -> CORRECT); each of b2, b3, b6 withdrawn with probability 1/3, "
          "each is a correct recommendation, so each loses 1/3 expected correct. F expected correct = b1 1 + (b2, b3, b6) 3 x 2/3 + b4 1 + b5 0 = 4. "
          "M correct = b1, b2, b5 = 3; b4 abstain on an indeterminate site = 1 -> 4. delta_B = (4 - 4)/6 = 0.",
          "- Failure sensitivity S-F1: the failures are concordant, so delta over all 8 eligible sites = 0 x 6/8 = 0.",
          "", "## Hand check of repository C (k = 0)", "",
          "- R_F = 3 (c1, c2, c3), R_M = 0, so k = 0 and F withdraws all three: c1, c2 (correct) become UNASSESSABLE; c3 "
          "(indeterminate, UNJUSTIFIED) becomes CORRECT. F correct = c3 + c4 (FLAG on KEY_MATERIAL_ONLY) + c6 = 3. M correct = c3 + c6 = 2. "
          "delta_C = +1/6, entirely from F's FLAG on c4: the repository contributes a policy difference without any recommendation. "
          "It stays in the estimand; it is reported as not matching-feasible."]
    (OUT / "worked_example_v12pp.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return reps


# ---------------------------------------------------------------------------------------------------- pilot
FAM = {"SIGN": "SIG", "VERIFY": "SIG", "KEY_ESTABLISHMENT": "KEM", "PK_ENCRYPT": "KEM", "PK_DECRYPT": "KEM"}


def derive(role, tier, hybrid):
    if role == "UNKNOWN":
        return A("ABSTAIN", "NONE", tier)
    if role in ("KEY_MATERIAL_ONLY", "PROTOCOL_CONFIG") or hybrid:
        return A("FLAG_NO_TARGET", "NONE", tier)
    return A("RECOMMEND", FAM[role], tier)


def pilot():
    jr = list(csv.DictReader((ROOT / "docs/dev/pilot_harness/judgments.csv").open(encoding="utf-8")))
    rp = {x["site_id"]: x for x in csv.DictReader((ROOT / "docs/dev/roles_on_pilot.csv").open(encoding="utf-8"))}
    rec = {(x["method"], x["site_id"]): x for x in jr}
    sites = [x for x in jr if x["method"] == "pqscan:B3-full-noabst" and x["eligible"] == "yes"]
    arms = {"full": [], "method+args": [], "method+args+recv": [], "method-only": []}
    check = []
    for x in sites:
        hyb = x["hybrid_component"] == "yes"
        for arm in arms:
            arms[arm].append(derive(rp[x["site_id"]][f"{arm}:role"], rp[x["site_id"]][f"{arm}:tier"], hyb))
        for arm, meth in (("full", "pqscan:B3-full-noabst"), ("method+args", "pqscan:B2-method-args")):
            r = rec[(meth, x["site_id"])]
            check.append(arms[arm][-1] == A(r["tool_action"], r["rec_class"], r["tier"] or None))
    L = ["# Pilot (development data, circular) — V12'' tables (PROPOSED, NOT ADOPTED; NOT results)", "",
         "Source: `docs/dev/pilot_harness/judgments.csv` (30 eligible sites, labels and recorded full / method+args outputs) and "
         "`docs/dev/roles_on_pilot.csv` (roles and tiers of all four arms). pqscan was developed on these sites.", "",
         f"Derivation check: the derived full and method+args actions reproduce the recorded harness rows on {sum(check)} of {len(check)} (site, arm) pairs.", "",
         "## Evidence-tier distribution of RECOMMEND decisions (threshold T0)", "",
         "| arm | RECOMMEND | T0 | T1 | T2 | T3 | FLAG_NO_TARGET | ABSTAIN |", "|---|---|---|---|---|---|---|---|"]
    for arm, outs in arms.items():
        recs = [a for a in outs if a.action == "RECOMMEND"]
        tc = [sum(1 for a in recs if a.tier == t) for t in ("T0", "T1", "T2", "T3")]
        L.append(f"| {arm} | {len(recs)} | " + " | ".join(map(str, tc)) + f" | {sum(a.action == 'FLAG_NO_TARGET' for a in outs)} | "
                 f"{sum(a.action == 'ABSTAIN' for a in outs)} |")
    labels = [dict(site_id=x["site_id"], eligible="yes", gt_role=x["gt_role"], assessability=x["assessability"],
                   hybrid_component=x["hybrid_component"]) for x in sites]
    repo_of = [x["repo"] for x in sites]
    for comp, other in (("H2-1", "method+args"), ("H2-3", "method+args+recv"), ("H2-4", "method-only")):
        reps = []
        for repo in ("paramiko", "python-jose"):
            ix = [i for i, r in enumerate(repo_of) if r == repo]
            reps.append(MR.evaluate_repository([labels[i] for i in ix], [arms["full"][i] for i in ix],
                                               [arms[other][i] for i in ix], comparison=comp, repo=repo))
        ns = [r["n_common"] for r in reps]
        g = MR.coverage_gap([r["R_f"] for r in reps], [r["R_m"] for r in reps], ns)
        L += ["", f"## {comp}: full vs {other}", ""] + report_rows(reps)
        L += ["", f"- Pooled repository-balanced tie-averaged delta = {MR.pooled([r['delta_ta'] for r in reps], ns) + 0.0:+.4f}; site-weighted "
              f"{MR.pooled([r['delta_ta'] for r in reps], ns, 'site') + 0.0:+.4f}; ranking-free {MR.pooled([r['delta_ta_rankfree'] for r in reps], ns) + 0.0:+.4f}; "
              f"natural {MR.pooled([r['delta_nat'] for r in reps], ns):+.4f}.",
              f"- Coverage gap g = {float(g):.4f} -> guard {'active' if MR.guard_active(g) else 'not active'}; matched coverage "
              f"{sum(r['k'] for r in reps)}/{sum(ns)} = {sum(r['k'] for r in reps) / sum(ns):.3f}."]
    (OUT / "pilot_v12pp.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return all(check)


if __name__ == "__main__":
    worked()
    ok = pilot()
    print("wrote worked_example_v12pp.md, pilot_v12pp.md; derivation check", "OK" if ok else "FAILED")
