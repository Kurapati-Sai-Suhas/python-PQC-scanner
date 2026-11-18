# Second specification review (protocol v1.0.5): prepared, not started

The first isolated AI review (v1.0.4; `docs/review/spec_review_v1.0.4/`, kept frozen) produced 21 findings. The owner decided every finding (`docs/audit/owner_decision_register_v1.0.5.md`), and the corrections made protocol v1.0.5. This folder holds the second review. **Nothing has been sent to any AI service. It starts only after the owner's explicit approval.**

This is an AI review followed by the owner's decision on each finding. It is not an independent human review and must never be reported as one. The external human review that the protocol requires before F1 is separate and still pending.

## Contents

| File | What it is |
|---|---|
| `review_instructions.md` | The fixed instructions (start of part 1). They require acknowledging each part, reviewing only after the last part, quoting evidence for every finding, separating confirmed contradictions from ambiguity and missing evidence, not inventing defects, separating methodological validity from external standards, reporting limitations, and never calling the research validated because the documents are consistent. |
| `decision_status.md` | Read first by the reviewer: what is adopted, what is pending, and the stated limitations. |
| `packet/part_01_of_08.txt` … `part_08_of_08.txt` | The instructions and 21 documents, each with its SHA-256; every part under 30,000 characters (about 234,000 characters in total). |
| `packet/manifest.json` | Hashes of the instructions, every document and every part. |
| `owner_decisions_TEMPLATE.csv`, `sign_off_TEMPLATE.md` | Copy before filling in. |

The 21 documents: the decision-status page; protocol v1.0.5 and **v1.0.3** (normative for H1, H3, H4, as interpreted in H-1 to H-6); analysis plan v1.0.1; the decision records; the run specification (Markdown and JSON); the amendment record; guide v1.2; taxonomy v1.1; data dictionary v1.1; scoring policy v1.0.1; the recommendation policy (text and YAML); the benchmark and meta schemas; the AI-review prompt; and the implementation rules the documents name as normative: `packets.py`, `candidates.py`, `frame_audit.py`, `multicall.py`. No label, tool output, held-out test material, pilot or synthetic answer, or identity value is in the packet.

## Readiness checklist (owner)

- [ ] `python scripts/spec_review_packet.py --check` exits 0 and ends with `AI-review identity: recorded`.
- [ ] The full test suite passes (`.venv\Scripts\python -m pytest -o addopts="" -q`).
- [ ] `python scripts/adoption_record.py --check` exits 0.
- [ ] Your identity file still describes the session you will use (model as the picker shows it; settings off). If the model or app version changed, record a new identity first.
- [ ] One **new** Temporary Chat, never the first review's chat.
- [ ] You have time to paste 8 parts and save the reply in one sitting (about 30–60 minutes).
- [ ] You will not open pilot labels, synthetic answers or tool outputs while deciding findings.

## Steps (only after approval)

1. Paste the parts in order; after each part except the last the reply should be only `RECEIVED PART i OF 8`. If the reviewer starts early or reports a truncated part, stop and restart in a new Temporary Chat.
2. Save the full reply verbatim, outside the repository, with the page saved as a PDF; record the time (UTC) and SHA-256 of the saved reply.
3. Record a decision for every finding in a copy of `owner_decisions_TEMPLATE.csv` (accept, reject with a specific reason, or defer with what is unclear). A change to a threshold, hypothesis, family or sampling rule needs its own explicit decision.
4. Sign off in a copy of `sign_off_TEMPLATE.md`.

## Not covered by this review

The external human review (mandatory before F1), the owner decisions still pending (pilot figure, W6), and anything needing external standards verification.
