# Phase 8: pilot, synthetic validation and DV annotation, readiness report (19 Nov 2026, commit 1cdc2d7)

**Status: PENDING. Annotation has not started.** No ledger exists under `benchmark/ledger/`, no annotation folder exists under `benchmark/annotation/`, and `docs/review/review_register.md` is empty.

Annotation is human work. The single investigator labels each candidate from source (protocol Sec. 3; the tool says "every step is run by the owner"). The assistant must not create labels, and did not run `annotate issue`, which starts the hash-chained ledger.

## 1. Machine checks run now (all pass)

| Check | Command / evidence | Result |
|---|---|---|
| Annotation workflow, ledger integrity, packet rules | `tests/test_annotation_integrity.py`, `tests/test_validation_loops.py` | 29 passed |
| Forbidden-token gate (prompt and fail-closed response), attribution isolation, candidate orders, multi-call rule, reliability statistics | `tests/test_forbidden_gate.py`, `tests/test_g05_g06_forbidden_gate.py`, `tests/test_candidates.py`, `tests/test_f03_multicall.py`, `tests/test_reliability_reporting.py` | 184 passed |
| Full suite | `pytest -o addopts="" -q` | 742 passed, 1 skipped |
| Data contract (benchmark schema v1.1; 388 synthetic records; pilot record) | `tests/test_owner_decisions_r3.py` | pass |
| Candidate orders unchanged (3,503 DV candidates) | `docs/paper/verify_evidence.py` E12, E64; `scripts/f03_multicall_census.py --check` | pass |
| 14-day re-label gap enforced in code | `pqscan/bench/reliability.py` `GAP_DAYS = 14`: refuses an earlier re-label and prints the earliest permitted date | verified (code and tests) |
| Pilot checkouts available (development repositories only) | `.cache/repos/{paramiko,python-jose}` | present |
| Exposed pilot material | `pqscan/bench/loops.py` `GUIDE_EXPOSED_PILOT`: 5 pilot sites quoted in the guide are flagged; the pilot is circular (it tuned Module B) and is never used as blind evidence | as designed |

## 2. Prerequisites before the first label (in order)

1. **Owner decisions on labelling rules raised by the third AI review:**
   - TA06 (PROTOCOL_CONFIG examples);
   - TA07 (escaped keys of single-purpose algorithms);
   - TA11 (PyCryptodome `cipher = PKCS1_OAEP.new(key)` followed by `cipher.encrypt`);
   - TA19 (`hybrid_component` only for KEY_ESTABLISHMENT, SIGN, VERIFY).

   These change how sites are labelled, so they must be settled **before** any label is written. Otherwise early labels follow a different rule from later ones. See `docs/audit/owner_decisions_needed_before_annotation_and_F1.md`.
2. **AI-review identity still current:** `docs/benchmark/ai_review_identity.json` must describe the session that will be used (V8). If the model or app version changed, record a new identity first.
3. **Order of loops (protocol Sec. 3):**
   1. synthetic 78-instance blind subset (`--phase synthetic`);
   2. pilot 31 sites (`--phase pilot`);
   3. DV annotation of the 4 development and 2 validation repositories (`--phase DV`), each through issue → primary → prompt → ai → compare → adjudicate.
4. **Frame audit (V7):** after DV labelling, `pqscan/bench/frame_audit.py` (owner reads whole files blind to the pool, at least 60 eligible sites).

## 3. Commands (to be run by the owner; shown for completeness)

```
python -m pqscan.bench.annotate issue   --phase synthetic --repo synthetic
python -m pqscan.bench.annotate primary --phase synthetic --repo synthetic --batch B1 --file <labels>.jsonl
python -m pqscan.bench.annotate prompt  --phase synthetic --repo synthetic --batch B1
python -m pqscan.bench.annotate ai      --phase synthetic --repo synthetic --batch B1 --response raw.txt --utc <time>Z
python -m pqscan.bench.annotate compare --phase synthetic --repo synthetic --batch B1
python -m pqscan.bench.annotate adjudicate --phase synthetic --repo synthetic --batch B1 --adjudication adj.csv
```

Repeat per batch; then `reference` (synthetic and pilot only, after the last batch). Use `--push` so that every ledger step is committed, as the protocol requires.

## 4. The 14-day re-label requirement

| Phase | First primary label | Earliest re-label date |
|---|---|---|
| DV | none yet | **first computable when labelling ends:** latest primary label among the sampled candidates + 14 days. The tool computes and enforces it |
| Test (after F1) | none yet | same rule |

No date can be computed today because no primary label exists. The interval will not be shortened or simulated. Reliability is **not** established until the second annotation and the κ analysis exist.

## 5. What Phase 8 can deliver without a human

All of it is delivered: checks (Section 1), workflow and commands (Section 3), and the prerequisite list (Section 2). Everything else in Phase 8 is human labelling.
