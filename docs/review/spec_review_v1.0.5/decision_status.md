# Decision status at the second specification review (protocol v1.0.5)

This page tells the reviewer which decisions are adopted and which are pending. It adds no rule of its own.

## Adopted (owner decisions, before any labelling and any test-split access)

| Decision | Where it is recorded |
|---|---|
| Protocol v1.0.4 with annotation guide v1.1 and analysis plan v1.0 (16 Nov 2026) | `evaluation_protocol.md` history; `phase3_decisions.md` |
| D7 (18 Nov 2026): F-B at matched recommendation volume; F-A at natural coverage, always described so | `run_specification_pre_f1.{md,json}` |
| D15 (18 Nov 2026): B1-algorithm is the single algorithm-name baseline in F-A; B1-dual is descriptive only | `run_specification_pre_f1.{md,json}` |
| Pre-F1 decision register (18 Nov 2026): protocol v1.0.5, guide v1.2, analysis plan v1.0.1, role taxonomy v1.1, data dictionary v1.1, scoring policy v1.0.1 (interpretation note) | `amendment_v1.0.5.md` |
| H-1 to H-6: status and interpretation of H1, H3 and H4, including the H1b baseline set | `run_specification_pre_f1.{md,json}` |
| F-A Type I error simulation: required before F1; result PASS | analysis plan Sec. 11.6 |
| Statistical acceptance of the H2 procedure: ACCEPTED (unstratified bootstrap in force) | analysis plan Sec. 11 |

## Pending (not yet done; not waived)

| Item | Status |
|---|---|
| External human review of the full specification by a reviewer outside the build team | **Pending.** Mandatory before F1 (protocol Stage F1 item 9; recommendation policy Sec. 7). The AI specification reviews do not replace it. |
| Owner sign-off of this second specification review | Pending until the review is decided |
| Pilot and synthetic validation loops; Phase DV labelling; the 14-day intra-rater re-label; reliability statistics; the Phase DV feasibility check (c_DV) | Not started |
| F1 (pre-test freeze), test-split access, F2 (label freeze), E (held-out evaluation) | Not started; each needs the owner's explicit approval |
| D10: PROTOCOL_CONFIG is not emitted by the scanner | Reported as a limitation |
| D14 (Mehl's scanner run) and D5 (licence) | Optional; not part of the evaluation |
| Pilot figure in protocol Sec. 1 ("51.7% (15/29)"; the pilot data give 16/30 = 53.3%) | Owner decision pending; the protocol text is unchanged. It is a historical pilot value, not a threshold. |
| W6: precision of the SP 800-227 section reference in the recommendation policy text | Owner decision pending; the policy text is unchanged. |

## Known, stated limitations (not defects to rediscover)

- Test-output blinding is a self-attestation, not independently enforced or verifiable.
- Single investigator; the AI review is not an annotation and not independent human validation.
- Seven purposively chosen test repositories; no claim beyond them.
- No supported library version exposes an SLH-DSA API, so the scanner cannot recognise an SLH-DSA hybrid.
