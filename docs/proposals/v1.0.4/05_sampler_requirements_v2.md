# Sampler and annotation tooling: audit findings and requirements (PROPOSED, revision 2)

## 1. Defects found in `pqscan/bench/candidates.py` (v1.0.3, commit `664e640`), all reproduced on the committed paramiko order

| # | Finding | Severity | Requirement |
|---|---|---|---|
| T1 | Quotas 25/30 are the approved values, but `next --quota` accepts any value typed by hand, and the manifest has no quota field | medium | R1 |
| T2 | IDs `C-<repo>-S1-app-0001` reveal stratum and rank | low–medium | R2 |
| T3 | With 7 eligible test-path sites and a cap of 8, 3 more test-path candidates are issued (reproduced). With 9 of 8, none are (correct) | low | R3 |
| T4 | The first batch is 20 candidates (10 S2 mixed in); missing S2 labels cause re-issue (reproduced) | medium | R4, R5 |
| T5 | `bool("false") is True`; unknown IDs accepted; duplicates silently overwritten; "issued" inferred from the labels file (all reproduced) | **high** | R5, R6 |
| T6 | jwcrypto `tests.py` (143 of 379 S1-app candidates) classed as app under the frozen rule | medium | R7 |
| T7 | Pool and recall claims imprecise (see the change log, corrections 1–2) | medium (documentation) | R8 |
| T8 | Overshoot past the quota was unstated | low | R3 |
| T9 | The frozen schema has `additionalProperties: false`, so "schema plus v1.1 fields" cannot validate | **high** | R12 |
| T10 | A hash chain without an external anchor can be regenerated wholesale | medium | R14 |
| T11 | Example and vendored code were counted as app | low (no effect on development/validation: 0 such S1-app candidates) | R7 |
| T12 | The stopping rule did not define how unresolved eligibility counts | medium | R15 |

## 2. Requirements (implemented only after approval)

- **R1 Quota source.** A constant table (test 30, development 25, validation 25) is tested against the protocol table. The split is read from `benchmark/real/manifest.json`. `--quota` is refused unless `--override-reason` is given, and the override is logged in the ledger.
- **R2 Opaque IDs.** `C-` plus the first 12 hex digits of SHA-256 of seed, repository, file and line. Stratum and rank stay only in the order file.
- **R3 Non-app issuance.** min(3, cap − eligible non-app so far) per batch, with the remaining slots filled from S1-app (and vice versa when one list is exhausted). Every annotated site is kept; overshoot is reported.
- **R4 Batch B0.** The 10 S2 candidates are issued once, as B0, before B1.
- **R5 Ledger.** `ledger_<repo>.jsonl` is append-only, with entry types `issue | primary | ai_review | compare | adjudication | override`. Each entry holds UTC time, batch, candidate IDs or file hash, the order hash and the previous entry's hash. `next` refuses to issue when:
  - an issued candidate lacks exactly one final label;
  - a label references an ID that was never issued;
  - the chain does not verify;
  - the step order is violated, for example an `ai_review` entry before a `primary` entry for the same batch.
- **R6 Strict validation.** The envelope (`site` against the frozen schema; `meta` against the v1.1 meta schema). The boolean fields must be JSON booleans. Any failure is an error, never coerced.
- **R7 Scope classes.** One function (test / example / vendored / app) is used by the sampler and the validator. The strata are S1-app, S1-nonapp and S2. Development/validation orders are regenerated (nothing has been annotated).
- **R8 Frame audit.** Seeded crypto-importing development/validation files are added one at a time until ≥ 60 eligible sites have been audited (≥ 6 files). The output gives the missed share with a Wilson CI, the per-file counts, and an explicit statement of scope.
- **R9 Packet builder and prompt template.** As in guide Sec. 6 and `01` Sec. 3. A test asserts that no packet contains tool names, `pqscan`, any label value or any result.
- **R10 Scripts.** Comparison over all eight fields; owner–AI, intra-rater and AI self-consistency κ with bootstrap CIs; the seeded intra-rater sample (≥ 50 or 10%), with a check of the 14-day gap; final-label derivation; secondary and bounding analyses.
- **R12 Envelope schema.** A `meta` JSON schema is added in `docs/benchmark/`. The frozen site schema is not modified.
- **R13 Quota table test.** Fails if the sampler constant and the protocol table differ.
- **R14 Ledger anchoring.** After every ledger entry, the ledger file is committed and pushed (hashes only; test labels stay out of git until F2). A verifier checks the local chain against the pushed history.
- **R15 Unresolved eligibility.** It counts as not eligible for stopping; it is listed in the ledger summary.

## 3. Required automated tests (R11)

| Test | Asserts |
|---|---|
| string booleans | `"false"`, `"true"`, `0` and `1` in boolean fields are rejected |
| unknown, duplicate and missing IDs | each blocks `next` with a specific error |
| tampered or reordered chain | the verifier fails; `next` refuses |
| step order | an `ai_review` entry before `primary` is refused |
| quota | the test split → 30, development/validation → 25; an override without a reason is refused; with a reason it is logged |
| B0 | issued exactly once; never mixed into B1+ |
| cap boundary | 7 of 8 eligible non-app → at most 1 non-app issued; 8 of 8 → 0 |
| overshoot | all annotated sites are retained in the final file |
| unresolved eligibility | not counted toward the quota |
| opaque IDs | stable across runs; no stratum or rank substring; distinct for distinct (file, line) |
| scope parity | sampler and validator classify an identical list of 30 synthetic paths the same way; jwcrypto's three test files → test |
| envelope | a valid record passes; any extra key in `site` fails; a missing `meta` field fails |
| packet | contains no forbidden strings; holds the excerpt and the line numbers |
| intra-rater sample | seeded; ≥ 50 or 10%; refuses re-labels dated within 14 days |
| bounding | three variants produce the expected label substitutions on a toy set |
