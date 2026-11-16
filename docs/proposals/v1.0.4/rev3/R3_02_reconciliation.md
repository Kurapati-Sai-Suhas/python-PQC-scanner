# R3-02 Repository, quota, stratum and S2 reconciliation (PROPOSED, revision 3)

## 1. Repository count (verified from `benchmark/real/manifest.json`; no test-repository content accessed)

| Split | Repositories | Count |
|---|---|---|
| development | paramiko, python-jose, PyJWT, Authlib | 4 |
| validation | jwcrypto, asyncssh | 2 |
| test | pyHanko, keylime, mitmproxy, scapy, salt, barbican, bismuth | 7 |
| **total** | | **13** |

**Defect:** protocol v1.0.3 (and revision 2) says Dataset B comes "from 8–12 repositories". The frozen manifest has 13 since bismuth was added on 14 Nov 2026 (manifest amendment). The "8–12" was a planning range written before the split was finalised. **Proposed correction (V15):** "13 repositories (4 development, 2 validation, 7 test), as frozen in the manifest". This is factual and changes no analysis.

## 2. Quotas and targets

| Split | Repositories × eligible quota | Primary-set eligible sites |
|---|---|---|
| test | 7 × 30 | 210 |
| development + validation | 6 × 25 | 150 |
| **total** | | **360** |

- **Why 360:** the owner chose O2 under D2 (14 Nov 2026). 210 test sites exceed the ≥ 150 test minimum, and 360 exceeds the ≥ 300 Dataset B minimum.
- **Status of the minimums:** they are minimum acceptance targets, not the quotas. If shortfalls (cap reached or S1 exhausted) bring the primary set below 300 overall or below 150 in test, that is reported as a failure to meet the target. Quotas are never moved between repositories.
- **What counts toward 300 / 150:** only **primary-set** eligible sites (Sec. 3).

## 3. Analysis sets and S2 (V14)

| Set | Contents | Counts toward quota? | Toward 300 / 150? | In primary metrics? | Reported |
|---|---|---|---|---|---|
| **Primary set** | every adjudicated-eligible site in S1-app or S1-nonapp (all issued batches, including overshoot and non-app sites beyond the cap) | yes: S1-app + min(S1-nonapp, cap) | yes | **yes** | main tables |
| S2 set (B0) | the 10 fixed S2 candidates per repository that are adjudicated eligible | **no** | **no** | **no** | own table: eligibility rate, roles, per-tool outcomes (descriptive) |
| Annotator-added set | eligible sites found by the annotator that were not in the candidate list | no | no | no | own table: count, roles, which methods found them (estimates sites missed by every candidate source) |
| Unresolved | sites with an unresolved key field | no (unresolved eligibility counts as not eligible) | no | no; bounding analysis per R3-07 Sec. 5.4 | listed |

**Sensitivity analysis:** "all adjudicated-eligible sites" (primary ∪ S2 ∪ annotator-added) is reported next to the primary results for H1–H3.

**Why S2 is excluded from the primary set:** S2 candidates come from files that import no supported library. They are sampled at a fixed 10 per repository, while S1 is sampled sequentially until the quota is met. The two strata have different inclusion mechanisms, so pooling them would give a sample with no defined estimand.

**Non-app sites beyond the cap:** they stay in the primary set, because removing annotated sites after labelling is not allowed. The cap limits counting and issuance, not inclusion. Under requirement R3, at most 2 such sites per repository are possible. Their number is reported.

## 4. Proposed protocol vs. the original sampler (`pqscan/bench/candidates.py`, commit `664e640`)

| # | Original sampler | Proposed (revision 3) | Mismatch |
|---|---|---|---|
| M1 | strata S1-app, S1-test, S2 | S1-app, S1-nonapp (test, example, vendored), S2 | yes |
| M2 | test-path regex: directory or `test_*.py` / `*_test.py` | adds `test.py`, `tests.py`, `tests_*.py`, `tests-*.py`, `conftest.py`; example and vendored classes; precedence vendored > test > example > app | yes |
| M3 | IDs `C-<repo>-<stratum>-<rank>` | opaque hash | yes |
| M4 | S2 added to the first batch, which is then 20 candidates | separate B0, issued once | yes |
| M5 | 3 test-path candidates per batch until eligible test-path ≥ cap | min(3, cap − eligible non-app) per batch | yes |
| M6 | when S1-app is exhausted, up to 10 non-app candidates are issued regardless of the remaining cap | non-app issuance always limited by the remaining cap | yes |
| M7 | `counted = eligible_app + min(eligible_test, cap)`; S2 not counted | the same formula with S1-nonapp; S2 not counted | consistent (S2 exclusion already matches V14) |
| M8 | cap = quota // 3 (10 of 30, 8 of 25) | the same | consistent |
| M9 | candidate cap 4 × quota S1 issued | the same | consistent |
| M10 | quota typed on the command line | protocol table plus a tested constant; override with a logged reason | yes |
| M11 | "issued" inferred from the labels file | hash-chained ledger | yes |
| M12 | `bool(r["eligible"])`: string `"false"` counts as true | JSON boolean required; unresolved is a separate state | yes |
| M13 | unknown and duplicate IDs accepted | rejected | yes |
| M14 | stop when the quota is reached, at 4 × quota, or when S1 is exhausted | the same, plus "unresolved eligibility = not eligible" | partly consistent |

Every "yes" row is a code change, made only after approval and tested by the cases in revision 2's `05` Sec. 3. M6 is new in revision 3.

## 5. Denominators

| Quantity | Denominator |
|---|---|
| H1–H3 rates, H2 test | primary-set eligible test sites (per repository and pooled) |
| Coverage | primary-set eligible sites per arm or tool |
| Detection recall per tool | primary-set eligible sites |
| Execution-failure rate | primary-set eligible sites in files where the tool's run is recorded |
| Owner–AI agreement | all candidates with both labels in the phase (Sec. R3-03) |
| Intra-rater agreement | the re-label sample (R3-03) |
