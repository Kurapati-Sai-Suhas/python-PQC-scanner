"""Join the H1 pilot site annotations with raw baseline-tool outputs and judge
each tool's action per site under recommendation policy v1.1.

Usage:
    python experiments/pilot/join_tool_outputs.py docs/pilot/h1_pilot_sites.csv \
        docs/pilot/raw_tool_outputs docs/pilot/h1_pilot_joined.csv docs/pilot/h1_pilot_summary.md

Outcome vocabulary (see docs/specification/data_dictionary.md):
  tool_action        RECOMMEND | FLAG_NO_TARGET | ABSTAIN | NO_FINDING
  rec_class          SIG | KEM | DUAL | PQC_ALREADY | NONE
  judgment           CORRECT | INCORRECT | UNDECIDED | UNJUSTIFIED | UNASSESSABLE | MISSED | DETECTED_ONLY
  harm_category      ROLE_INCOMPATIBLE | FALSE_ASSURANCE | OVER_RECOMMENDATION | (empty)

Policy v1.1 expected target class by ground-truth role:
  SIGN, VERIFY            -> SIG   (ML-DSA family, FIPS 204)
  KEY_ESTABLISHMENT       -> KEM   (ML-KEM-based redesign, FIPS 203 / SP 800-227; hybrid allowed)
  PK_ENCRYPT, PK_DECRYPT  -> KEM   (KEM + KDF/AEAD redesign; "drop-in" wording is noted, not scored)
  KEY_MATERIAL_ONLY       -> NONE  (inventory finding; any specific target is OVER_RECOMMENDATION)
  hybrid_component = yes  -> NONE  (already PQ/T hybrid; any migration target is OVER_RECOMMENDATION)
  UNKNOWN / INDETERMINATE -> ABSTAIN or DUAL expected; a single target is UNJUSTIFIED
"""
from __future__ import annotations
import csv, json, re, sys, collections
from pathlib import Path

sites_csv, raw_dir, out_csv, out_md = map(Path, sys.argv[1:5])

def norm(p: str) -> str:
    return p.replace("\\", "/")

PKG = {"paramiko": "paramiko", "python-jose": "jose"}

def rel(path: str, repo: str) -> str:
    """Return a path relative to the repository root, whatever the tool emitted
    (absolute path, path including the clone directory, or already relative)."""
    p = norm(path)
    marker = f"/pilot_repos/{repo}/"
    if marker in p:                      # absolute path from the scratchpad clone
        return p.split(marker, 1)[1]
    for top in (PKG[repo], "tests"):     # path that still carries the clone directory
        if p.startswith(f"{repo}/{top}/"):
            return p[len(repo) + 1:]
    return p

DROPIN = re.compile(r"replace[sd]?.*(entirely|directly)|drop-?in|swap|replace (RSA|ECDH|X25519|ECDSA|EC) with", re.I)

def classify_text(t: str) -> str:
    t = t or ""
    has_kem = "ML-KEM" in t or "Kyber" in t
    has_sig = "ML-DSA" in t or "Dilithium" in t or "SLH-DSA" in t
    if "Already using PQC" in t:
        return "PQC_ALREADY"
    if has_kem and has_sig:
        return "DUAL"
    if has_kem:
        return "KEM"
    if has_sig:
        return "SIG"
    return "NONE"

# ---------------------------------------------------------------- load raw outputs
def load_pqcheck(repo):
    s = json.load(open(raw_dir / f"pqcheck_policy_{repo}.sarif"))
    out = []
    for x in s["runs"][0]["results"]:
        loc = x["locations"][0]["physicalLocation"]
        out.append({"file": rel(loc["artifactLocation"]["uri"], repo), "line": loc["region"]["startLine"],
                    "text": x["message"]["text"], "rule": x["ruleId"]})
    return out

def load_pqcaudit(repo):
    cb = json.load(open(raw_dir / f"pqcaudit_{repo}.cbom.json"))
    out = []
    for c in cb.get("components", []):
        props = {p["name"].split(":")[-1]: p["value"] for p in c.get("properties", [])}
        for o in c.get("evidence", {}).get("occurrences", []):
            out.append({"file": rel(o["location"], repo), "line": o["line"],
                        "text": f"{c['name']} usage={c['bom-ref'].split(':')[-1]} target={props.get('migrationTarget')}",
                        "rule": c["bom-ref"]})
    return out

def load_postquant(repo):
    p = json.load(open(raw_dir / f"postquant_{repo}.json"))
    return [{"file": rel(x["file"], repo), "line": x["line"], "text": x["migration"], "rule": x["patternId"]}
            for x in p["findings"]]

def load_qsafe(repo):
    q = json.load(open(raw_dir / f"qsafe_{repo}.json"))
    return [{"file": rel(x["file"], repo), "line": x["line"], "text": x["migration"],
             "rule": f"{x['algorithm']}/{x['context']}"} for x in q["findings"]]

def load_qsa(repo):
    q = json.load(open(raw_dir / f"qsa_{repo}.json"))
    return [{"file": rel(x["file"], repo), "line": x["line_number"], "text": x["pqc_replacement"],
             "rule": x["algorithm"]} for x in q["findings"]]

LOADERS = {"pqcheck": load_pqcheck, "pqc-audit": load_pqcaudit, "PostQuant": load_postquant,
           "qsafe": load_qsafe, "QSA-regex": load_qsa}

# ---------------------------------------------------------------- judging
def expected_class(site):
    if site["eligible"] != "yes":
        return "N/A"
    if site["hybrid_component"] == "yes" or site["gt_role"] in ("KEY_MATERIAL_ONLY", "PROTOCOL_CONFIG"):
        return "NONE"
    if site["assessability"] == "INDETERMINATE":
        return "ABSTAIN"
    return {"SIGN": "SIG", "VERIFY": "SIG", "KEY_ESTABLISHMENT": "KEM",
            "PK_ENCRYPT": "KEM", "PK_DECRYPT": "KEM"}.get(site["gt_role"], "ABSTAIN")

def judge(site, action, rec_class):
    exp = expected_class(site)
    if exp == "N/A":
        return ("N/A", "") if action == "NO_FINDING" else ("FALSE_POSITIVE_SITE", "")
    if action == "NO_FINDING":
        return "MISSED", ""
    if action == "FLAG_NO_TARGET":
        return ("CORRECT", "") if exp == "NONE" else ("DETECTED_ONLY", "")
    if exp == "ABSTAIN":
        if rec_class == "DUAL":
            return "UNDECIDED", ""
        if rec_class == "PQC_ALREADY":
            return "INCORRECT", "FALSE_ASSURANCE"
        return "UNJUSTIFIED", ""
    if exp == "NONE":
        if rec_class == "PQC_ALREADY" and site["hybrid_component"] == "yes":
            return "CORRECT", ""  # hybrid already PQ: 'already PQC' is defensible here
        if rec_class == "PQC_ALREADY":
            return "INCORRECT", "FALSE_ASSURANCE"
        if rec_class == "DUAL":
            return "UNDECIDED", ""
        return "INCORRECT", "OVER_RECOMMENDATION"
    if rec_class == "PQC_ALREADY":
        return "INCORRECT", "FALSE_ASSURANCE"
    if rec_class == "DUAL":
        return "UNDECIDED", ""
    if rec_class == exp:
        return "CORRECT", ""
    return "INCORRECT", "ROLE_INCOMPATIBLE"

sites = list(csv.DictReader(open(sites_csv, encoding="utf-8")))
rows = []
for tool, loader in LOADERS.items():
    findings = {repo: loader(repo) for repo in ("paramiko", "python-jose")}
    for s in sites:
        lo, hi = int(s["line_start"]), int(s["line_end"])
        hits = [f for f in findings[s["repo"]] if f["file"] == s["file"] and lo <= int(f["line"]) <= hi]
        if not hits:
            action, rec_class, text = "NO_FINDING", "NONE", ""
        else:
            classes = {classify_text(h["text"]) for h in hits}
            text = " || ".join(sorted({f"{h['rule']}: {h['text'][:90]}" for h in hits}))
            if classes == {"NONE"}:
                action, rec_class = "FLAG_NO_TARGET", "NONE"
            elif "PQC_ALREADY" in classes and classes - {"PQC_ALREADY", "NONE"}:
                # a tool contradicting itself on one site: treat the migration-bearing class as its action
                cl = classes - {"PQC_ALREADY", "NONE"}
                action, rec_class = "RECOMMEND", ("DUAL" if len(cl) > 1 or "DUAL" in cl else cl.pop())
                text = "[CONFLICT incl. 'Already using PQC'] " + text
            else:
                cl = classes - {"NONE"}
                action, rec_class = "RECOMMEND", ("DUAL" if (len(cl) > 1 and cl != {"PQC_ALREADY"}) or "DUAL" in cl else cl.pop())
        judgment, harm = judge(s, action, rec_class)
        dropin = bool(hits) and expected_class(s) == "KEM" and rec_class == "KEM" and any(DROPIN.search(h["text"] or "") for h in hits)
        rows.append({"dropin_wording": dropin, "site_id": s["site_id"], "tool": tool, "gt_role": s["gt_role"], "assessability": s["assessability"],
                     "eligible": s["eligible"], "hybrid_component": s["hybrid_component"], "expected_class": expected_class(s),
                     "tool_action": action, "rec_class": rec_class, "judgment": judgment, "harm_category": harm, "tool_text": text})

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------------------------------------------------------------- summary
elig = [s for s in sites if s["eligible"] == "yes"]
n_elig = len(elig)
n_indet = sum(1 for s in elig if s["assessability"] == "INDETERMINATE")
n_not_obvious = sum(1 for s in elig if s["obvious_from_name"] == "no")
prov = collections.Counter(s["key_provenance"] for s in elig)
roles = collections.Counter(s["gt_role"] for s in elig)
lines = ["# H1 pilot — joined results (auto-generated by experiments/pilot/join_tool_outputs.py)", ""]
lines += [f"Eligible sites: {n_elig} of {len(sites)} annotated (ineligible negatives: {len(sites)-n_elig}).",
          f"Role not determinable from method/algorithm name alone: {n_not_obvious}/{n_elig} = {100*n_not_obvious/n_elig:.1f}%.",
          f"Statically INDETERMINATE role (depends on a runtime value): {n_indet}/{n_elig} = {100*n_indet/n_elig:.1f}%.",
          "", "Ground-truth roles: " + ", ".join(f"{k}={v}" for k, v in sorted(roles.items())),
          "Key provenance: " + ", ".join(f"{k}={v}" for k, v in sorted(prov.items())), "",
          "| Tool | Sites judged | CORRECT | of which drop-in wording | INCORRECT (harmful) | of which ROLE_INCOMPATIBLE | FALSE_ASSURANCE | OVER_RECOMMENDATION | UNDECIDED | UNJUSTIFIED | DETECTED_ONLY | MISSED | harmful+undecided+unjustified rate |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for tool in LOADERS:
    r = [x for x in rows if x["tool"] == tool and x["eligible"] == "yes"]
    c = collections.Counter(x["judgment"] for x in r)
    h = collections.Counter(x["harm_category"] for x in r if x["judgment"] == "INCORRECT")
    bad = c["INCORRECT"] + c["UNDECIDED"] + c["UNJUSTIFIED"]
    nd = sum(1 for x in r if x["dropin_wording"])
    lines.append(f"| {tool} | {len(r)} | {c['CORRECT']} | {nd} | {c['INCORRECT']} | {h['ROLE_INCOMPATIBLE']} | {h['FALSE_ASSURANCE']} | {h['OVER_RECOMMENDATION']} | {c['UNDECIDED']} | {c['UNJUSTIFIED']} | {c['DETECTED_ONLY']} | {c['MISSED']} | {bad}/{len(r)} = {100*bad/len(r):.0f}% |")
lines += ["", "Negative candidate (J14, padding constant) flagged as a finding by: " +
          ", ".join(x["tool"] for x in rows if x["site_id"] == "J14" and x["judgment"] == "FALSE_POSITIVE_SITE"), ""]
lines += ["## Per-site matrix (judgment per tool)", "", "| Site | Role | Assess. | " + " | ".join(LOADERS) + " |", "|---|---|---|" + "---|" * len(LOADERS)]
for s in sites:
    cells = []
    for tool in LOADERS:
        x = next(r for r in rows if r["site_id"] == s["site_id"] and r["tool"] == tool)
        cells.append(f"{x['judgment']}" + (f" ({x['rec_class']})" if x["tool_action"] == "RECOMMEND" else ""))
    lines.append(f"| {s['site_id']} | {s['gt_role']}{' [hybrid]' if s['hybrid_component']=='yes' else ''} | {s['assessability']} | " + " | ".join(cells) + " |")
Path(out_md).write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:16]))
