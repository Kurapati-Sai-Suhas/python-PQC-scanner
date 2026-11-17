# Owner action checklist (updated 18 Nov 2026)

**Current state** (verified by `docs/paper/verify_evidence.py`, E01):
- engineering complete;
- no AI-review identity;
- no specification review, no labels, no F1 tag or freeze record;
- `main` = `phase2-complete` = 81f561e.

**Restrictions in force:**
- No fake `ai_review_identity.json`.
- No Claude substitute for the isolated ChatGPT specification review.
- No annotation without the owner actions below.
- No access to held-out test repositories before F1.
- No F1, F2 or E without explicit approval and the freeze.
- The 14-day intra-rater gap is never shortened.
- No protocol change without approval.
- Never modify `main`; never force-push.
- No credentials or labels in git.

## A. In order: steps only you can perform

| # | Step | What you do | Done when | Then Claude can |
|---|---|---|---|---|
| 1 | **Record the AI-review identity (V8)** | Create `docs/benchmark/ai_review_identity.json` yourself with `interface_or_api` (e.g. "ChatGPT web, Temporary Chat"), `model` exactly as the model picker displays it, `recorded_utc`, and `isolation` (the settings you actually use). | file committed | build review prompts and packets (the tooling refuses until then) |
| 2 | **Instruct the isolated ChatGPT specification review** | Tell Claude to prepare the review package. You run the review in the recorded interface; Claude must not do it. You sign off the outcome. | review export and sign-off stored | apply the corrections you approve, through the pre-F1 correction route |
| 3 | Decide D5 (licence) and D9/D10 (policy citation, PROTOCOL_CONFIG) | `docs/paper/author_decisions.md` | decisions recorded | implement the approved changes before F1, with tests and an adoption-record update |
| 4 | **Pilot (31) and synthetic (78) validation loops (D2)** | Label blind from source, following the annotation guide; run the AI review; adjudicate | adjudicated files (git-ignored) and ledger entries | run the comparisons and reports; score synthetic-dev **after** your D2 labels exist |
| 5 | **Phase DV annotation** | Instruct issuance, then label each batch blind (no tool outputs, no `runs/`), AI review, adjudicate | DV quotas met or shortfalls recorded | frame audit, reliability statistics, the D6 pipeline re-run and feasibility check (label-free) |
| 6 | **Intra-rater re-label** | No earlier than 14 days after your latest DV primary label; the script refuses earlier | re-label file | κ and agreement statistics |
| 7 | **Approve F1** | Explicit written approval after DV, the reliability check and D6 | your instruction | write `docs/freeze/pretest_freeze.json`, tag `phase3-pretest-freeze`; only then fetch the test split (`fetch_pinned.py` refuses before) |
| 8 | **Phase T annotation** | Same procedure on the test candidates | T labels adjudicated | — |
| 9 | **Approve F2** (label freeze) | Explicit approval | F2 record | — |
| 10 | **Approve E** (single evaluation run) | Explicit approval | your instruction | run E once; fill `results_placeholders.md`; update the manuscript with the pre-registered statement templates |
| 11 | Final novelty audit and paper decisions D1–D4, D6–D8, D11–D13 | Provide the IEEE sample paper; choose scope and venue | decisions recorded | format the manuscript to the template; final peer-review pass |

## B. Work Claude can do now, without any owner gate

- Format the manuscript to your IEEE sample once you provide it (D1). No compliance claim before your approval.
- Draw figures F-1 to F-4 (architecture, decision flow, protocol timeline, calibration labelled as simulation).
- Re-check the ◐ related-work items against full text where it is openly accessible, and update `related_work_matrix.md`.
- Keep `verify_evidence.py` green after any change.
- Prepare the specification-review package. Running the review stays yours, after step 1.

## C. Time constraints that cannot be shortened

- The intra-rater re-label is ≥ 14 days after the latest primary label of the phase. That applies separately to DV and to T.
- E runs once, after F2.

So a completed empirical paper requires at least: DV annotation time + 14 days + T annotation time + 14 days (T re-label) + E. The design and protocol content can be finalised before then.
