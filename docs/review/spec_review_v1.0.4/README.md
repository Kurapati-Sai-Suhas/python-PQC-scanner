# Specification review of protocol v1.0.4 (prepared, not started)

Protocol v1.0.4, Sec. 3 says the specification review is "ChatGPT review with owner sign-off". This folder holds everything that review needs. **Nothing here has been sent to any AI service. The review has not started.** It starts only after the owner explicitly approves it.

This is an AI review followed by the owner's decision on each finding. It is not an independent human review, and it must never be reported as one.

## What is in this folder

| File | What it is |
|---|---|
| `review_instructions.md` | The fixed instructions the reviewer receives. They form the start of part 1. Do not edit them after the review starts. |
| `packet/part_01_of_05.txt` … `part_05_of_05.txt` | The packet: the instructions, then 15 adopted specification documents, each with its SHA-256 hash. Every part is under 30,000 characters. |
| `packet/manifest.json` | The hash of the instructions, of every document and of every part. |
| `owner_decisions_TEMPLATE.csv` | Blank sheet for the owner's decision on each finding. Copy it before filling it in. |
| `sign_off_TEMPLATE.md` | Blank sign-off record. Copy it before filling it in. |

The packet is built by `scripts/spec_review_packet.py`. Running `python scripts/spec_review_packet.py --check` confirms that the committed packet still matches the documents (exit code 0). If a specification document changes, the check fails and the packet must be rebuilt before the review.

## The documents in the packet (in order)

1. `docs/specification/evaluation_protocol.md` (protocol v1.0.4)
2. `docs/specification/phase3_analysis_plan.md` (analysis plan v1.0)
3. `docs/specification/phase3_decisions.md` (decision records)
4. `docs/specification/run_specification_pre_f1.md` and 5. `.json` (pre-F1 run specification: D7, D15)
6. `docs/benchmark/annotation_guide.md` (guide v1.1)
7. `docs/specification/role_taxonomy.md`
8. `docs/specification/data_dictionary.md`
9. `docs/specification/scoring_policy.md`
10. `docs/specification/recommendation_policy.md`
11. `pqscan/policy/policy_v1_1.yaml`
12. `docs/benchmark/benchmark_schema.json`
13. `docs/benchmark/meta_schema.json`
14. `docs/benchmark/ai_review_prompt_v1.md`
15. `pqscan/bench/packets.py` (the packet rule the AI labeller sees)

No tool output, no label, no result and no held-out test repository is in the packet.

## Steps for the owner (only after approving the review)

1. **Check the identity record.** `docs/benchmark/ai_review_identity.json` must exist and describe the interface, model and isolation settings actually used (V8). At the time this folder was prepared, the file was **not in the repository**. Do not start until it is. `python scripts/spec_review_packet.py --check` must end with `AI-review identity: recorded`; it reports `INVALID: ...` when the record fails `pqscan.bench.review.load_identity` (placeholder left, missing setting, or a setting not off).
2. **Check the packet.** Run `python scripts/spec_review_packet.py --check`. It must print no "out of date" line and exit 0.
3. **Open one fresh isolated session**, set up exactly as the identity record says (for ChatGPT: a new Temporary Chat; custom instructions, memory and chat history, Projects, connectors, file library and browsing off).
4. **Paste the parts in order**, one per message. After each part except the last, the reply should be only `RECEIVED PART i OF 5`. If the reviewer starts reviewing early or says a part is cut off, stop, note it, and start again in a new session.
5. **Save the full reply verbatim** and the conversation export or share link, outside Git if it contains anything private. Record its SHA-256.
6. **Decide every finding** in a copy of `owner_decisions_TEMPLATE.csv`: accept, reject or defer, with a reason. A finding is never ignored silently.
7. **Changes.** An accepted finding that needs a change to the protocol, guide, plan, thresholds, sample size, sampling orders or confirmatory families is a protocol amendment and needs its own explicit owner decision before anything is edited. Purely editorial fixes are recorded the same way.
8. **Sign off** in a copy of `sign_off_TEMPLATE.md`. Only after the sign-off may the pilot and synthetic loops start, and only with the owner's approval.

## Points the owner already knows about (for the decision sheet, not for the reviewer)

These were found during preparation. They are kept out of the packet instructions on purpose, so the reviewer is not steered towards them. If the reviewer does not raise them, the owner should still record a decision on each:

- the out-of-date pilot figure in protocol Sec. 1 ("51.7% (15/29)"; the data give 16/30 = 53.3%);
- W6: the SP 800-227 section reference in the policy text (should be Secs. 5.2.1 and 4.3);
- D10: PROTOCOL_CONFIG is not emitted by the scanner (report it as a limitation, or change it before F1).

All three are listed in `docs/audit/owner_action_checklist_next_stage.md`.

## What this folder does not do

It does not start the review, contact any service, create labels, start the pilot or synthetic loops, touch the held-out test repositories, or create an F1 or F2 freeze record.
