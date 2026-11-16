# Phase 3 readiness checklist, revision 4 — PROPOSED, NOT ADOPTED

> **ADOPTION NOTICE (2026-11-16).** Superseded by `R4_20_readiness_checklist_final.md` and the live tracker `docs/implementation/phase3_tracker.md`. The body below is unchanged history.


No human task below is done. Status: READY / NOT READY / BLOCKED (owner decision).

| # | Item | Status |
|---|---|---|
| A1 | Owner decides V1–V18 (`R4_06`) | BLOCKED (owner) |
| A2 | Approved protocol v1.0.4, guide v1.1 and meta schema committed; revisions 1–4 kept | NOT READY |
| A3 | Owner names the AI interface and model; prompt template frozen and hashed | NOT READY |
| A4 | ChatGPT specification review in an isolated session; owner sign-off | NOT READY |
| A5 | Pilot re-label (31) and synthetic subset (78) loops | NOT READY |
| B1 | Sampler and ledger (M1–M14), envelope and meta schema, strict validation | NOT READY |
| B2 | Packet builder; prompt template; forbidden-content test; packet-first subset selection | NOT READY |
| B3 | Comparison, reliability samplers (intra-rater, AI repeat-run), κ with within-repository bootstrap, specific agreement, derivation, unresolved bounding | NOT READY |
| B4 | **Coverage matching (V12′)** in `pqscan/bench`, with tests: exact equality, label-free, tier order, seeded ties, the worked example reproduced | NOT READY |
| B5 | **Stratified re-matching bootstrap** and Holm, F-B and F-A, in `pqscan/bench`, with tests; **calibration re-run with ≥ 5,000 data sets on at least two generative models**, recorded before F1 | NOT READY |
| B6 | Exploratory repository-level outputs (7 δ_r, LOO, t, sign-flip, Wilcoxon) | NOT READY |
| B7 | Frame-audit tooling | NOT READY |
| B8 | Development/validation orders regenerated (opaque IDs, scope rule) | NOT READY |
| B9 | Batch runner on real tools; Dataset A | READY |
| C1 | Frame audit (≥ 60 eligible sites, 6 repositories) | NOT READY |
| C2 | Phase DV annotation loop to quota | NOT READY |
| C3 | Phase DV reliability (intra-rater, owner–AI, AI repeat-run, packet-first subset) | NOT READY |
| C4 | Phase DV results computed with the full H2 pipeline (development results only); c_DV recorded | NOT READY |
| D1 | H1–H4 wording, scoring v1.0, τ = T2, manifests | READY |
| D2 | H2 operationalisation (V10a‴, V10b″, V12′, V13′, V17, V18) | BLOCKED (owner) |
| E1–E4 | F1 → test extraction and Phase T loop → F2 → E | NOT READY (sequential) |

**F1 reachability (estimate, not a commitment):**
- B1–B8: about one to two focused weeks of implementation and testing.
- Phase DV owner work: about 30–90 h (assumed), plus the mandatory 14-day gap before the re-label.
- F1: about 4–7 weeks after approval, depending on the owner's available time.
