# Annotation candidate orders (development and validation)

**Format.** Orders use `pqscan-order/2`, built with `pqscan/bench/candidates.py` (protocol v1.0.4 Sec. 2; decisions V5, V6, V11).

**Regenerated 2026-11-16.**
- Sources: the same real batch runs (`runs/development/run1`, `runs/validation/run1`) and the pinned commits in `benchmark/real/manifest.json`, with each checkout verified clean at its pin.
- Seed: 20261113.
- The v1.0.3 orders are archived unchanged in `archive_v1.0.3/` and in git history.
- **Locations unchanged.** The candidate locations, and the S2 set, are identical to v1.0.3 for every repository.
- **What changed:**
  - the scope rule (V5): jwcrypto's `jwcrypto/tests.py`, 143 candidates, moved from S1-app to S1-nonapp; no other repository changed stratum;
  - opaque candidate IDs (`C-` plus 12 hex digits);
  - an order-format version.

**What annotators see.** These files list the full seeded order of every candidate per stratum. Annotators receive only the location-only batches produced by the `next` command. They never see `pool_sources_*.json` (which tools reported each candidate), which is git-ignored and stays on the coordinator's machine until the development and validation labels are frozen at F1.

| Split | Repository | S1-app | S1-nonapp | S2 | Regex-only (missed by every tool) | Pool hash (first 12) |
|---|---|---|---|---|---|---|
| development | paramiko | 204 | 206 | 165 | 9 | f8e7bb098331 |
| development | python-jose | 55 | 62 | 183 | 5 | 46f826156923 |
| development | pyjwt | 111 | 282 | 78 | 98 | 2907fcd4d9a6 |
| development | authlib | 171 | 270 | 515 | 42 | 30e118cb19a8 |
| validation | jwcrypto | 236 | 143 | 37 | 31 | 003c29560b3a |
| validation | asyncssh | 143 | 117 | 525 | 12 | fcf3c44afe9a |

**Quota:** 25 eligible sites per development or validation repository, of which at most 8 are non-app (`QUOTAS` in the code, tested against the protocol table).

**Issuance:** B0 (10 S2 candidates, once), then batches of 7 S1-app plus min(3, remaining non-app cap) S1-nonapp. The ledger supplies the issued list:

```bash
.venv/Scripts/python -m pqscan.bench.candidates next --order benchmark/candidates/development/order_paramiko__paramiko.json --split development --issued <issued ids> --labels <final labels.jsonl> --out batch.jsonl
```

**Before any annotation.** Annotation has not started; it waits for the owner's explicit instruction. The test-split pools are built only after F1, from the sealed extraction run.
