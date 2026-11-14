# Annotation candidate orders (development and validation)

Built 14 Nov 2026 with `pqscan/bench/candidates.py` (protocol v1.0.3 Sec. 2), from the real batch runs `runs/development/run1` and `runs/validation/run1`, at the pinned commits in `benchmark/real/manifest.json`. Seed: 20261113.

These files list the full seeded order of every candidate per stratum. Annotators receive only the location-only batches produced by the `next` command. They never see `pool_sources_*.json`, which records which tools reported each candidate; those files are git-ignored and stay on the coordinator's machine until the development and validation labels are frozen at F1.

| Split | Repository | S1-app | S1-test | S2 | Regex-only (missed by every tool) | Pool hash (first 12) |
|---|---|---|---|---|---|---|
| development | paramiko | 204 | 206 | 165 | 9 | 7edeeabe0f5a |
| development | python-jose | 55 | 62 | 183 | 5 | 59606fbdf959 |
| development | PyJWT | 111 | 282 | 78 | 98 | 04540f640a41 |
| development | Authlib | 171 | 270 | 515 | 42 | f01a19113309 |
| validation | jwcrypto | 379 | 0 | 37 | 31 | e6c26b358bb4 |
| validation | asyncssh | 143 | 117 | 525 | 12 | c5b6dd1401d2 |

Quota: 25 eligible sites per repository, of which at most 8 from test paths.

The first batch for a repository (no labels yet):

```bash
.venv/Scripts/python -m pqscan.bench.candidates next --order benchmark/candidates/development/order_paramiko__paramiko.json --quota 25 --out batch_paramiko_01.jsonl
```

Later batches add `--labels <adjudicated.jsonl>` (one `{"candidate_id": ..., "eligible": true|false}` per issued candidate). The command prints the counts and the stop reason once the quota, the candidate cap or the end of S1 is reached.

Known limitation: the scope rule is the frozen one from the annotation guide (a test directory, or `test_*.py` / `*_test.py`). Test modules named otherwise, such as jwcrypto's `jwcrypto/tests.py`, therefore fall in S1-app.

The test-split pools are built only after F1, from the sealed extraction run.
