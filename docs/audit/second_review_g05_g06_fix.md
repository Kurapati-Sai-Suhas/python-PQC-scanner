# Second specification review: code fixes G05 and G06 (19 Nov 2026)

Owner-approved fix of the two verified code defects among findings G01–G11 of the second isolated AI specification review (protocol v1.0.5). Starting commit `f67c25056d1c271c5669da30887bf3b14fbc12ae` (local checkpoint tag `pre-g05-g06-fix-f67c250`).

| Finding | Defect | Fix |
|---|---|---|
| G05 | `packets.FORBIDDEN` listed only `h2a`, `h2b` of the registered hypothesis/comparison identifiers | `HYPOTHESIS_IDS` = h1a, h1b, h2a, h2b, h2-1, h2-2, h2-3, h2-4, h2-s, f-a, f-b, added to `FORBIDDEN` (case-insensitive, existing word boundaries). Bare H1–H4 deliberately not listed (they match ordinary code). |
| G06 | The prompt gate existed, but the `ai` step accepted a response without checking that the gate's decision existed, and parsed records for excluded candidates | `cmd_ai` now calls `_ai_gate`: if any packet contains a forbidden token, the recorded decision must exist and validate (same rules as the prompt gate); a response naming an excluded candidate is rejected before anything is written or ledgered; excluded candidates are never parsed. The prompt gate's semantics are unchanged. |

**Hashes (SHA-256, LF-normalised).**
- `pqscan/bench/packets.py`: before `636b4b8f68fc315dc5d2c504b566452c1a89f477e0567116a6bdb89a6f493925`, after `3aa9ea54e5b3ed44d4348179870447376145845fa0317621e8465ff249922301`.
- `pqscan/bench/annotate.py`: before `f630b215370f6e4e03c017cf5af4722032d305dd794bbe746ad17d67de6c7bc6`, after `d9a4bdba9856d8327e4f2e2b9665053b335840b540d92645d251ad3cccc36904`.

**Records.** `adoption_record_v1.0.5.json` and `adoption_record_v1.0.4.json` are not rewritten; the pre-fix `packets.py` is archived byte-for-byte in `docs/specification/archive/v1.0.5/` and `archive/v1.0.4/` and verified against both. Current hashes: `adoption_record_v1.0.5-r1.json`. Both review packets (v1.0.4, v1.0.5) still reproduce exactly the texts their reviewers saw.

**Tests.** `tests/test_g05_g06_forbidden_gate.py` (every registered identifier in several forms and cases; ordinary-code negatives; the real `prompt` and `ai` command paths: refused without a decision, genuine content excluded, a response naming an excluded candidate rejected, a tampered decision refused, a verified false positive proceeding).

**Not changed.** Protocol v1.0.5 text, sampling, candidate orders, labels, hypotheses, estimands, metrics, statistics, thresholds, F-A/F-B, D7, D15, the scanner and its hybrid detector (G09 is an implementation false positive), the E30 calibration closure.

**Still open (not resolved by this fix):** G01, G02, G03, G04, G07, G08, G10 and G11 remain as verified (documentation corrections or owner decisions; G11 is a self-attested safeguard: `pool_sources_*.json` is git-ignored but on the same disk). The policy YAML comment noted under G09 is stale and unchanged.
