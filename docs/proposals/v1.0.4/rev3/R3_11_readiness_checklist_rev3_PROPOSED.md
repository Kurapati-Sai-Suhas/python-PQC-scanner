# Phase 3 readiness checklist (PROPOSED, revision 3)

Status: READY / NOT READY / BLOCKED (owner decision). No human task below is done.

| # | Item | Status |
|---|---|---|
| **A** | **Methodology** | |
| A1 | Owner decides V1–V17 (`R3_10`) | BLOCKED (owner) |
| A2 | Protocol v1.0.4, guide v1.1 and the meta schema committed as approved; revisions 1–3 kept in `docs/proposals/` | NOT READY (after A1) |
| A3 | Owner names the AI interface and model; prompt template frozen and hashed | NOT READY |
| A4 | ChatGPT specification review in an isolated session; owner sign-off per document | NOT READY |
| A5 | Pilot re-label (31) + AI review + comparison with the Phase 1 AI labels | NOT READY |
| A6 | Synthetic subset (78) + AI review; generator fixes if needed | NOT READY |
| **B** | **Tooling (Claude, after A1)** | |
| B1 | Sampler M1–M14 with the revision 2 test list plus M6 and B0/S2 tests | NOT READY |
| B2 | Ledger, envelope validation and the meta schema | NOT READY |
| B3 | Packet builder, prompt template, forbidden-content test | NOT READY |
| B4 | Comparison; κ, specific agreement and intra-rater sampler; repeat-run sampler; derivation; secondary and bounding analyses | NOT READY |
| B5 | **Coverage matching (V12)** and **repository-level H2 statistics** (fixed sequence, t test, sign-flip, Holm F-B and F-A), moved from `docs/proposals/v1.0.4/rev3/scripts` into `pqscan/bench` with tests | NOT READY |
| B6 | Frame-audit tooling (seeded round-robin, matching, file-level cluster bootstrap) | NOT READY |
| B7 | Development/validation orders regenerated (opaque IDs, rev3 scope classes) | NOT READY |
| B8 | Batch runner on real tools | READY |
| B9 | Dataset A reproducible; holdout unscanned | READY |
| **C** | **Phase DV labels (owner)** | |
| C1 | Frame audit (≥ 60 eligible sites, all 6 repositories) | NOT READY |
| C2 | DV loop to quota; ledger pushed after each step | NOT READY |
| C3 | DV intra-rater (n = max(50, 10%), ≥ 14 days later): κ(gt_role) ≥ 0.60, or revise and re-label | NOT READY |
| C4 | DV owner–AI and AI repeat-run reported | NOT READY |
| C5 | DV results (development) with the frozen judge, coverage matching and repository-level statistics | NOT READY |
| **D** | **Frozen rules** | |
| D1 | H1–H4 wording, scoring v1.0, τ = T2 | READY |
| D2 | H2 decision rule (V10a′, V10b′, V12, V13, V17) | BLOCKED (owner) |
| D3 | Manifests (13 repositories), D4 = A | READY |
| D4 | Sampling rule (revision 3 amendments) | NOT READY (after A1) |
| **E** | **Freeze and evaluation** | |
| E1 | F1 record (revision 3 contents), tagged | NOT READY (needs A–D) |
| E2 | Test fetch; sealed extraction; Phase T loop; Phase T intra-rater; attestation | NOT READY (after E1) |
| E3 | F2, tagged | NOT READY |
| E4 | E once; determinism check; primary, secondary and bounding analyses | NOT READY |

**F1 reachability:**
- The engineering items (B1–B7) are a few focused days of implementation and testing.
- The dominant cost is the owner's Phase DV work: about 30–90 hours (assumed; DV share of `R3_06`), plus a mandatory gap of at least 14 days before the intra-rater re-label.
- F1 is therefore realistic about 3–6 weeks after approval, depending on the owner's available time. This is an estimate, not a commitment.
