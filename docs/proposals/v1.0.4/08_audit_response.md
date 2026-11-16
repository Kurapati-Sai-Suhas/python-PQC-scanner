# Response to the methodology and implementation-readiness audit (PROPOSED documents, revision 1 → revision 2)

The audit was conducted 14 Nov 2026 and was read-only. Reproducible scripts: `audit_power.py`, `audit_kappa.py` and `audit_h2_rules.py` in the session scratchpad. Their results are quoted in `01` Sec. 4–5.

| Decision | Audit classification (revision 1) | Finding | Revision 2 change | Where |
|---|---|---|---|---|
| V1 | APPROVE WITH MODIFICATION | fields used by the analysis not cross-checked; no external anchor for "owner labelled first"; AI-review workload omitted; no route to later external checking | all eight fields compared and adjudicated; ledger pushed after each step; workload 60–105 h (assumed); optional post-hoc external re-annotation | `01` Sec. 2, 4; `02` Sec. 3; `04` Sec. 1 |
| V2 | APPROVE WITH MODIFICATION | normal approximation overstated exact power by 0.02–0.04; the power analysis did not match the H2 "≥ 10 pp" rule; Holm family undefined; discordance and clustering not discussed; noise factor (1 − 2e) is a binary bound | exact and simulated figures; new decision V10a (three outcomes) and V10b (families); discordance and clustering caveats; noise factor explained | `01` Sec. 4; `02` Sec. 1; `06` V10 |
| V3 | APPROVE WITH MODIFICATION | 10% gives about 15 or 21 items (κ 95% range about ±0.2–0.3); denominator unspecified; 7 days short | ≥ 50 per phase (or 10%), seeded over all annotated candidates, ≥ 14 days, full reporting | `01` Sec. 5; `02` Sec. 3; `04` Sec. 2 |
| V4 | APPROVE WITH MODIFICATION | `hybrid_component`, `obvious_from_name` and `evidence_needed` not compared, though they decide the expected class and H1a | consensus defined on the expected-class fields; all eight fields compared; label sets frozen at F2 before judging | `01` Sec. 2, 6; `02` Sec. 5 |
| V5 | APPROVE | verified on 683 files: 4 newly classified files, all genuine tests; jwcrypto `tests.py` holds 143 of 379 S1-app candidates; example and vendored scope treated as app | rule kept; example and vendored handling made decision V11 | `02` Sec. 2; `06` V11 |
| V6 | APPROVE WITH MODIFICATION | frozen schema forbids extra fields; no quota field in the manifest; chain not externally anchored; unresolved eligibility undefined | envelope with a meta schema; protocol quota table and test; ledger pushed after every step; unresolved = not eligible for stopping; full test list | `05`; `02` Sec. 2–3 |
| V7 | APPROVE WITH MODIFICATION | six files give no defined precision | files added until ≥ 60 eligible sites; Wilson CI; scope of conclusions stated | `02` Sec. 2; `05` R8 |
| V8 | APPROVE WITH MODIFICATION | "memory off" insufficient; browsing could reveal the public repository; the interface does not expose a model snapshot; nondeterminism; context asymmetry | Temporary Chat or API with a pinned identifier; all personalisation and tools off; restricted prompt; exported conversations; self-consistency; context-difference tag; correlation disclosure | `01` Sec. 3; `04` Sec. 6 |
| V9 | APPROVE WITH MODIFICATION | exclusion can bias H2/H3 in either direction | finalised before F2; listed; three-way bounding; > 5% flag | `01` Sec. 6; `02` Sec. 5 |

**Self-check of revision 2.** Every quantitative statement in `01`–`07` traces to a script output or a repository count:
- the power table → `audit_power.py`, `audit_h2_rules.py`;
- κ ranges → `audit_kappa.py`;
- the V5 counts → read-only scan of `.cache/repos/{development,validation}`;
- pool counts → `benchmark/candidates/*/order_*.json`.

Workload hours remain assumptions and are labelled as such.
