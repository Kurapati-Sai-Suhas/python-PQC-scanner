# R4-06 Owner decisions — PROPOSED, NOT ADOPTED (revision 4)

> **ADOPTION NOTICE (2026-11-16).** Superseded by the adopted decision record `docs/specification/phase3_decisions.md`: R4-18 as amended by R4-21 Sec. 6. Rows V10a‴, V10b″, V12′, V13′ and V18 below are replaced by V10a, V10b, V12, V13 and V18 there. V20–V24 are added. The body below is unchanged history.


Nothing takes effect until the owner approves it. Approved items are committed one by one on `phase3-preparation`; earlier revisions stay in `docs/proposals/`.

| # | Decision | Recommendation | Owner alternative |
|---|---|---|---|
| V1 | single investigator; blind isolated ChatGPT review; owner adjudication; wording limits | approve | — |
| V2 | quotas 30 (test) / 25 (development, validation); 360 primary-set; minimums 300 / 150; 13 repositories | approve | — |
| V3′ | reliability samples per R4-05 Sec. 3 | approve | κ threshold 0.70 |
| V4 | consensus and AI-label secondary analyses (on matched outcomes) | approve | — |
| V5 | test-file rule | approve | — |
| V6 | sampler, ledger and validation requirements M1–M14 | approve | — |
| V7′ | descriptive frame audit per R4-05 Sec. 4 | approve | skip (frame recall stated unknown) |
| V8 | AI isolation, identity, export, repeat runs; owner names the interface and model before the first review | approve | API with a pinned model |
| V9 | unresolved: recorded before F2, excluded, listed, bounded; > 5% flag | approve | — |
| **V10a‴** | H2: **direction confirmatory** (B1), **10 pp magnitude exploratory** (B2 bootstrap lower bound vs. 0.10); categories per R4-02 Sec. 4 | **approve** (honest given the power) | margin confirmatory under Holm m = 4 with low power declared |
| **V10b″** | F-B = Holm over B1, B3, B4 (m = 3) at one-sided family α 0.025; F-A separate Holm family (≤ 8 baselines, natural coverage) | approve | m = 4 including B2 (pairs with the V10a‴ alternative) |
| V11 | strata, scope precedence, separate reporting of the three non-app classes | approve | — |
| **V12′** | coverage = RECOMMEND / eligible; within-repository output-adaptive matching (k_r = min); lowest tier withdrawn first; seeded ties; abstentions stay in the denominator; fixed-target V12-B and natural coverage as secondary; 100-seed sensitivity | **approve** | V12-B (fixed target from Phase DV) as primary |
| **V13′** | confirmatory inference about the **7 selected repositories** by stratified re-matching bootstrap (B = 10,000); site-level exact McNemar / Tango secondary; repository-level t, sign-flip, Wilcoxon, LOO and all 7 δ_r values as exploratory generalisation | **approve** | declare H2 entirely exploratory |
| V14′ | primary population per R4-05 Sec. 1; S2, annotator-added and tool false-positive reporting | approve | — |
| V15 | 13 repositories (4 development, 2 validation, 7 test) | approve | — |
| V16′ | `context_used` recorded in the hashed primary file before the AI review; two values; packet-first on a seeded 10% subset | approve | packet-first for all candidates (about +9–28 h, assumed) |
| V17 | one-sided α = 0.025 as the family level | approve | two-sided 0.05 |
| **V18 (new)** | H2 arms: full vs. method+args, **both at threshold T0** (no tier gate; UNKNOWN abstains), then matched. The proposed system (full at τ = T2) vs. method+args reported as secondary | **approve** | full at T2 vs. method+args at T0 (mixes evidence with abstention policy) |

**Rejected from revision 3:** V10a′ (confirmatory margin as the default) and V13 (repository-level t as confirmatory).
**Unchanged and not decided here:** H1–H4 wording; the H1, H3 and H4 decision rules; `scoring_policy.md` metric definitions; τ = T2 for the proposed system; the licence (D6).
