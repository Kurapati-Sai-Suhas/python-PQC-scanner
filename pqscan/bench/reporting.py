"""Report generators for Phase 3 (phase3_analysis_plan.md Sec. 5-10; protocol v1.0.4 Sec. 1.1, 2, 5.6; decisions V4,
V9, V14; R4-19 item 14).

These functions only format results that already exist (they are tested on fixtures). No report is produced before
real results exist. Wording rules are enforced: "H2 supported" is never produced, the matched difference is never
called recommendation accuracy, and every pooled H2 figure carries "K = 7; K_e = x".
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

LIMITATION = ("Results are limited to RSA/EC/Ed/X public-key call sites in files importing pyca or PyCryptodome within "
              "the candidate frame of the 13 frozen repositories.")
FORBIDDEN_PHRASES = ("H2 supported", "recommendation accuracy")


def _f(x, nd=4):
    return "—" if x is None else (f"{x:+.{nd}f}" if isinstance(x, float) else str(x))


def repository_table(results: Sequence[dict]) -> str:
    """Per-repository report (plan Sec. 10) for one comparison, as Markdown."""
    rows = [("eligible sites", lambda r: r["n_eligible"]), ("common evaluable n_r", lambda r: r["n_common"]),
            ("failures F / M", lambda r: f"{r['fail_f']} / {r['fail_m']}"),
            ("both / F only / M only / neither ran", lambda r: "{both} / {f_only} / {m_only} / {neither}".format(**r["partition"])),
            ("indeterminate (common)", lambda r: r["n_indeterminate_common"]),
            ("stratum allocation app / non-app", lambda r: f"{r['strata']['S1-app']} / {r['strata']['S1-nonapp']}"),
            ("natural RECOMMEND R_F / R_M", lambda r: f"{r.get('R_f')} / {r.get('R_m')}"),
            ("matched k_r (coverage)", lambda r: f"{r['k']} ({r['matched_cov']:.3f})" if r.get("delta_ta") is not None else "—"),
            ("recommended both / F only / M only", lambda r: f"{r['both_rec']} / {r['f_only_rec']} / {r['m_only_rec']}" if r.get("delta_ta") is not None else "—"),
            ("delta_r (tie-average, primary)", lambda r: _f(r.get("delta_ta"))),
            ("delta_r seeded (20261113)", lambda r: _f(r["seeded"]["delta"]) if r.get("delta_ta") is not None else "—"),
            ("100-seed min / median / max", lambda r: (lambda s: f"{min(s):+.4f} / {sorted(s)[len(s) // 2]:+.4f} / {max(s):+.4f}")(r["seed_deltas"]) if r.get("seed_deltas") else "—"),
            ("delta_r ranking-free", lambda r: _f(r.get("delta_rankfree"))),
            ("delta_r natural coverage", lambda r: _f(r.get("delta_nat"))),
            ("matched precision F / M", lambda r: f"{_f(r.get('prec_matched_f'), 3)} / {_f(r.get('prec_matched_m'), 3)}"),
            ("S-F1 / S-F2", lambda r: f"{_f(r.get('delta_sf1'))} / [{_f((r.get('delta_sf2') or (None, None))[0])}, {_f((r.get('delta_sf2') or (None, None))[1])}]"),
            ("matching-feasible (k_r >= 5)", lambda r: "yes" if r.get("feasible") else "no")]
    head = "| field | " + " | ".join(r["repo"] for r in results) + " |\n|---|" + "---|" * len(results)
    body = "\n".join(f"| {name} | " + " | ".join(str(fn(r)) for r in results) + " |" for name, fn in rows)
    return head + "\n" + body + "\n"


def h2_table(family: dict) -> str:
    """Pooled H2 table (plan Sec. 8), one row per comparison."""
    cols = ["comparison", "K; K_e", "c_pool", "gate", "g (guard)", "delta (repo-bal.)", "delta (site-wt.)", "97.5% bound",
            "p", "guarded p", "Holm p", "statement"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for c, r in family.items():
        g = r.get("g")
        lines.append("| " + " | ".join([
            c, f"K = {r['K']}; K_e = {r['K_e']}", str(r["gate"]["c_pool"]), "passes" if r["gate"]["passes"] else "fails",
            "undefined" if g is None else f"{g} ({'active' if r['guard'] else 'inactive'})",
            _f(r.get("delta")), _f(r.get("delta_site")), _f(r.get("lower_975")), _f(r.get("p")), _f(r.get("p_guarded")),
            _f(r.get("p_holm")), r.get("statement", "")]) + " |")
    out = "\n".join(lines) + "\n"
    if "H2-1" in family and family["H2-1"].get("h2b"):
        out += "\n" + family["H2-1"]["h2b"] + "\n"
    check_wording(out)
    return out


def abstract_sentence(h21: dict) -> str:
    """Plan Sec. 8 abstract template, filled only from the H2-1 result."""
    if h21["assessability"] != "assessable" or not h21["gate"]["passes"]:
        s = ("In seven pre-registered test repositories, the comparison at equal recommendation volume could not be "
             f"assessed as pre-registered ({h21.get('statement', h21['assessability'])}). Results describe these "
             "repositories only.")
    else:
        more = "more often than" if h21["claimable"] else "not detectably more often than"
        met = h21["p_margin_guarded"] <= 0.025
        s = ("In seven pre-registered test repositories, matching each method to the same number of migration "
             "recommendations per repository, the provenance-aware analysis made correct site-level decisions "
             f"{more} method-and-argument analysis (difference {100 * h21['delta']:.1f} pp, one-sided 97.5% bound "
             f"{100 * h21['lower_975']:.1f} pp). The 10-point improvement of the original hypothesis "
             f"{'was' if met else 'was not'} met in a pre-specified exploratory analysis. Results describe these repositories only.")
    check_wording(s)
    return s


def check_wording(text: str) -> None:
    for p in FORBIDDEN_PHRASES:
        if p in text:
            raise ValueError(f"report text contains the forbidden phrase {p!r}")


# --------------------------------------------------------------------------------------------- V14 analysis sets
def analysis_set_tables(finals: Sequence[dict], tool_findings: dict[str, set[str]] | None = None) -> dict:
    """S2, annotator-added and per-tool false-positive reporting (protocol Sec. 2, V14). `finals` are final label
    envelopes with meta.stratum (S1-app, S1-nonapp, S2) attached by the caller; `tool_findings` maps a tool to the
    candidate IDs it reported (from the sealed pool sources, joined only after the labels are final)."""
    s2 = [r for r in finals if r["meta"].get("stratum") == "S2"]
    added = [r for r in finals if r["meta"].get("annotator_added")]
    out = {"S2": {"labelled": len(s2), "eligible": sum(r["site"]["eligible"] is True for r in s2)},
           "annotator_added": {"count": len(added), "by_role": dict(Counter(r["site"]["gt_role"] for r in added))},
           "false_positives": {}}
    inel = {r["meta"]["candidate_id"] for r in finals if r["site"]["eligible"] is False}
    for tool, ids in (tool_findings or {}).items():
        annotated = ids & {r["meta"]["candidate_id"] for r in finals}
        out["false_positives"][tool] = {"findings_on_annotated": len(annotated), "on_ineligible": len(annotated & inel)}
    return out


# --------------------------------------------------------------------------------------------- V4 and V9 variants
def label_variants(finals: Sequence[dict], ai_records: Sequence[dict]) -> dict[str, list[dict]]:
    """Site-label variants for the secondary label analyses (V4) and the unresolved bounding (V9, protocol Sec. 5.6):
    'final' (owner-final), 'unresolved_owner' (unresolved fields at the owner's primary value; final labels already
    hold it), 'unresolved_ai' (unresolved fields at the AI's value where it gave one), 'unresolved_indeterminate'
    (unresolved sites set to INDETERMINATE), 'consensus' (only sites where owner-final equals the AI on eligible,
    gt_role, assessability and hybrid_component)."""
    ai = {r["site"]["site_id"]: r for r in ai_records}
    base = lambda r: {"site_id": r["site"]["site_id"], "eligible": r["site"]["eligible"], "gt_role": r["site"]["gt_role"],
                      "assessability": r["site"]["assessability"], "hybrid_component": r["site"]["hybrid_component"]}
    out = {"final": [], "unresolved_owner": [], "unresolved_ai": [], "unresolved_indeterminate": [], "consensus": []}
    for r in finals:
        b = base(r)
        out["final"].append(b)
        out["unresolved_owner"].append(dict(b))
        unres = set(r["meta"].get("unresolved") or [])
        a = ai.get(b["site_id"])
        v_ai = dict(b)
        if a:
            for f in unres & {"eligible", "gt_role", "assessability", "hybrid_component"}:
                if f in a["site"]:
                    v_ai[f] = a["site"][f]
        out["unresolved_ai"].append(v_ai)
        out["unresolved_indeterminate"].append(dict(b, assessability="INDETERMINATE") if unres else dict(b))
        if a and all(f in a["site"] and a["site"][f] == b[f] for f in ("eligible", "gt_role", "assessability", "hybrid_component")):
            out["consensus"].append(dict(b))
    return out
