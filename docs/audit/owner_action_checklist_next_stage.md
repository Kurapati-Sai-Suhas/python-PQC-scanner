# Owner action checklist: next stage (specification review → DV annotation → F1 → T → F2 → E)

Prepared 18 Nov 2026. Supersedes `docs/paper/owner_action_checklist.md`, which is kept for the record.

**Verified state before writing:**
- branch `phase3-preparation`, HEAD `0e2932c`, in sync with origin;
- `main` = 81f561e, untouched;
- the pre-F1 run specification (`docs/specification/run_specification_pre_f1.{md,json}`) is committed in dba3fcb, and its test passes;
- **no** `docs/benchmark/ai_review_identity.json`, **no** `docs/freeze/`, **no** labels.

Nothing in this checklist has been started. It changes no protocol, threshold, baseline set or scanner code.

**Who does what:**
- **YOU**: only you may do it (labels, decisions, approvals, anything inside ChatGPT).
- **CLAUDE**: mechanical work I can run when you say "go" (commands, packets, statistics, records).
- **BLOCKER**: nothing after it can start until it is done.

---

## 0. One-page sequence

| # | Stage | Who | Blocker? | Rough effort / wait |
|---|---|---|---|---|
| 1 | Record the AI-review identity (V8) | YOU | **BLOCKER** | 15 min |
| 2 | Prepare the specification-review packet | CLAUDE (on your go) | **BLOCKER** | 30 min |
| 3 | Run the isolated ChatGPT specification review; decide each finding; sign off | YOU (+ CLAUDE applies the changes you approve) | **BLOCKER** | 2–4 h |
| 4 | Add pilot/synthetic loop support to the annotation tool (§4) | CLAUDE (on your go) | **BLOCKER** for step 5 | 1–2 h |
| 5 | Pilot (31) and synthetic (78) validation loops | YOU label; CLAUDE runs the tooling | **BLOCKER** | about 1 week of your time |
| 6 | DV annotation to quota (6 repositories) | YOU label and adjudicate; CLAUDE runs the steps | **BLOCKER** | 30–90 h of your time |
| 7 | Wait ≥ 14 days, then the intra-rater re-label | YOU | **BLOCKER** (calendar) | ≥ 14 days + a few hours |
| 8 | Reliability statistics; κ rule; frame audit; DV pipeline and feasibility check (D6) | CLAUDE | **BLOCKER** | 1 day |
| 9 | Decide the remaining pre-F1 items (§8) | YOU | some are blockers | — |
| 10 | **F1**: pre-test freeze record + tag | CLAUDE prepares; **YOU approve** | **BLOCKER** | 1 h |
| 11 | Fetch the test repositories; sealed run; location-only candidates | CLAUDE | — | 1 h |
| 12 | Phase T annotation + AI review + adjudication; ≥ 14-day re-label | YOU | **BLOCKER** | 40–100 h + ≥ 14 days |
| 13 | **F2**: label freeze + tag | CLAUDE prepares; **YOU approve** | **BLOCKER** | 1 h |
| 14 | **E**: the single pre-registered evaluation run | CLAUDE runs; **YOU approve** the start and review the result | — | 1 day |

**Durations.** From R4-20 where it gives them: specification review plus loops about 1 week; DV 30–90 owner hours; the re-label ≥ 14 days after labelling. The others (identity, packet, tooling, the Phase T hours, the freeze steps) are Claude's estimates. None are commitments.

---

## 1. Prerequisites for the isolated specification review

| Prerequisite | Status | Who |
|---|---|---|
| Protocol v1.0.4, guide v1.1, analysis plan v1.0 adopted and hash-recorded | ✅ done (`adoption_record_v1.0.4.json`, check passes) | — |
| Production tooling implemented and tested | ✅ done (494 passed, 1 skipped) | — |
| Pre-F1 run specification (D7, D15) | ✅ done (dba3fcb) | — |
| **AI-review identity recorded** (`docs/benchmark/ai_review_identity.json`) | ❌ **missing** | **YOU** (§2) |
| **Specification-review packet** (the documents plus a fixed review instruction) | ❌ not prepared | CLAUDE, on your go |
| A fresh, isolated ChatGPT session configured as in §2 | ❌ | **YOU** |

The tooling refuses to build any AI-review prompt until the identity file exists (`pqscan/bench/review.py`, `load_identity`).

---

## 2. How to record the AI-review identity (V8). Only you can do this.

**Why:** every AI review must state exactly which AI produced it, under which isolation. Otherwise the reviews cannot be reproduced or audited. Claude must not fill these values in: they must describe what *you* actually use.

**Before you write anything**, set up the session you will use (annotation guide v1.1 Sec. 6):
- **Interface:** ChatGPT, using **one new Temporary Chat per review batch**, never this project's conversation or any chat that has seen the project.
- **Settings that must be OFF:**
  - custom instructions;
  - memory and chat-history reference;
  - Projects;
  - connectors;
  - file library;
  - browsing / web search.
- **Alternative:** the OpenAI API with a pinned model identifier and *your own* key. Claude never handles API keys.

**Then create the file** `docs/benchmark/ai_review_identity.json` with exactly these four keys. The tool checks that all four are present and non-empty (`review.load_identity`):

```json
{
  "interface_or_api": "<what you actually use, e.g. the product name and mode as you see it>",
  "model": "<the model name EXACTLY as the model picker displays it (or the API model ID)>",
  "recorded_utc": "<the current date and time in UTC, ISO format, e.g. YYYY-MM-DDTHH:MM:SSZ>",
  "isolation": "<the settings you actually switched off, in your own words>"
}
```

**How to get each value:**
- **`interface_or_api`:** describe what you open, for example the product and the Temporary Chat mode. Do not copy an example: write what you use.
- **`model`:** read it from the model picker at the moment you record. Copy it character for character.
- **`recorded_utc`:** the time you write the file, in UTC. In Git Bash, `date -u +%FT%TZ` prints it.
- **`isolation`:** list the settings from the list above that you turned off, and anything else you did.

**Rules:**
- **Never leave a `<…>` placeholder.** The tool only checks that the fields are non-empty; it cannot tell a placeholder from a real value.
- If the displayed model changes later (providers rotate models), stop and tell Claude. Record a new identity file version with the date and the reason, committed before the next batch. Each review record also stores the model and UTC time per batch.
- Commit the file yourself, or ask Claude to commit it as written by you. Claude will not change its content.

---

## 3. What you review in the specification review

**What the review is.** ChatGPT, in the isolated session, reads the frozen specification and lists problems: ambiguities, contradictions, unsafe cryptographic claims, untestable rules. **You decide on every finding**: accept → Claude makes the change through the pre-F1 correction route; or reject, with a reason. Then you **sign off**. This is "ChatGPT review with owner sign-off" (protocol Sec. 3). It does **not** replace your own reading. Read the sections below yourself before signing.

| File | Sections to read | Why it matters |
|---|---|---|
| `docs/specification/evaluation_protocol.md` (v1.0.4) | Sec. 1 (RQs, H1–H4, H2a/H2b); Sec. 2 (datasets, quotas, sampling rule); Sec. 3 (labelling, reliability, packet-first); Sec. 4 (experiments); Sec. 5 (statistics, families F-A/F-B); Stage F1 and Stage F2 | The pre-registered study itself |
| `docs/specification/phase3_analysis_plan.md` | Secs. 1–9 (comparisons, estimand, matching, estimators, failures, inference, statements, F-A) | Exactly how H2 and F-A will be computed |
| `docs/specification/phase3_decisions.md` | all | The adopted decisions V1–V23 |
| `docs/specification/run_specification_pre_f1.md` | all | Your D7 and D15 decisions (F-A membership) |
| `docs/benchmark/annotation_guide.md` (v1.1) | Secs. 1–6 (workflow, your rules, decision procedure Steps A–G, evidence requirements, record format, AI-review rules) | What you will do when labelling |
| `docs/specification/role_taxonomy.md` | Secs. 2–5 | Role definitions you label against |
| `docs/specification/scoring_policy.md` | Secs. 1–5 | How every tool's output is judged |
| `docs/specification/recommendation_policy.md` + `pqscan/policy/policy_v1_1.yaml` | all | What pqscan recommends per role |
| `docs/benchmark/meta_schema.json`, `docs/benchmark/benchmark_schema.json`, `docs/specification/data_dictionary.md` | fields | The label format |
| `docs/benchmark/ai_review_prompt_v1.md` | all | What the AI reviewer will be told |

**Known items the review should cover** (already found; each needs your decision before F1):
- the stale pilot figure in protocol Sec. 1 ("51.7% (15/29)" vs the data's 16/30 = 53.3%);
- the SP 800-227 section reference in the policy text (W6: should be Secs. 5.2.1 and 4.3);
- PROTOCOL_CONFIG is not emitted by the scanner (D10: report as a limitation, or change before F1).

**Exit artefacts:**
- the review export (verbatim);
- your decision per finding;
- a signed-off record;
- changelog entries and an updated adoption record if anything changed.

---

## 4. Pilot and synthetic validation loops (step 5)

**Purpose:** test the whole labelling machinery on data where problems are cheap, *before* touching the 6 DV repositories:
1. You label from source.
2. The isolated AI reviews.
3. The script compares.
4. You adjudicate.

They also check that the synthetic generator's labels are right.

| Loop | Items | What you do | Evidence it produces | What it is NOT |
|---|---|---|---|---|
| **Pilot re-label** | the 31 pilot sites (paramiko, python-jose; `docs/pilot/h1_pilot_sites.csv`) | Label the 31 sites under guide v1.1, then AI review, compare, adjudicate | Proof that the loop works end to end; guide problems found early; an owner–AI agreement figure for the pilot (reported separately) | Not evidence of scanner accuracy. The pilot is circular (the scanner was debugged on it) and you have seen its tool outputs before. |
| **Synthetic validation** | the 78-instance blind subset of Dataset A (`benchmark/synthetic/validation_subset.csv`: locations only) | Label each instance blind (do not open `sites.jsonl`, which holds the generated labels), then AI review, compare with the generator's labels, adjudicate | Whether the generator's by-construction labels are right. A confirmed generator error is fixed in the generator and Dataset A is regenerated **before F1**. | Not real-world accuracy |

**Tooling gap (Claude, needs your go):** the annotation tool supports only phases `DV` and `T` (`pqscan/bench/annotate.py`, `--phase` choices). Running these two loops needs a small extension:
- the pilot and synthetic site lists as issue sources;
- the same primary → prompt → ai → compare → adjudicate steps;
- separate, git-ignored work folders.

This is tooling, not a scanner or protocol change (R4-20 step 4: "tooling defects fixed").

---

## 5. Development/validation (DV) annotation (step 6)

**Scale:**
- 6 repositories: paramiko, python-jose, pyjwt, authlib (development); jwcrypto, asyncssh (validation).
- Quota: **25 eligible sites per repository** (150 in total) + **B0 = 10 S2 candidates per repository** (60, reported separately).
- Candidates are issued in batches of 10 from the frozen orders (`benchmark/candidates/*/order_*.json`).
- A repository stops at quota, or after 4 × quota issued, or when its S1 pool is exhausted. A shortfall is reported, never moved between repositories.

**The loop for each batch** (guide v1.1 Sec. 1; commands in `pqscan/bench/annotate.py`):

| Step | What happens | Who |
|---|---|---|
| a. Issue | `annotate issue …` produces a **location-only** batch (opaque ID, repository, commit, file, line) and a ledger entry | CLAUDE, when you say "issue the next batch" |
| b. Label | You open each location in the pinned checkout (`.cache/repos/…`) and decide eligibility, role, assessability, provenance and evidence, following guide Secs. 3–4. You write one JSON line per candidate in `benchmark/annotation/DV/<repo>/primary_<repo>_B<n>.jsonl` (git-ignored). **Packet-first candidates** (flagged at issue, about 12.8% in DV) are labelled from the packet alone first. | **YOU** |
| c. Record | `annotate primary --file …` validates strictly, hashes, writes the ledger, and pushes the hash (never the labels) | CLAUDE runs it; YOU must have finished the file |
| d. AI review | `annotate prompt …` builds the prompt. You paste it into a **new** isolated Temporary Chat, save the verbatim reply, and run `annotate ai --response <file> --utc <time>` | YOU (ChatGPT part); CLAUDE (commands) |
| e. Compare | `annotate compare …` produces the disagreements file | CLAUDE |
| f. Adjudicate | For each disagreement **you** choose the final value, a reason, a category (kept / adopted_ai / third_value / unresolved) and a context tag; then `annotate adjudicate …` | **YOU** decide; CLAUDE runs it |

**Your blinding rules, until a repository's final labels exist** (guide v1.1 Sec. 2):
- **Do not open** `runs/`, `docs/pilot/raw_tool_outputs/`, `docs/dev/` (pilot harness and tool judgments on paramiko and python-jose), or any pqscan or baseline output for these six repositories.
- Do not run a scanner on them.
- Claude will not show you DV tool outputs.

**The 14-day intra-rater interval (step 7):**
1. After DV labelling, the script draws a re-label sample: **n = max(50, ⌈0.10 × N⌉)**, seed `20261113:intra:DV`, stratified by repository (≥ 3 each) and by eligibility, in a new random order.
2. You may start re-labelling **no earlier than 14 days after the latest primary label among the sampled candidates**. The tool refuses earlier (`reliability.GAP_DAYS = 14`, `check_gap`). The wait is what makes it a real test of consistency: you can no longer remember your first answers.
3. You re-label **without looking at your earlier labels**.
4. Claude computes agreement and Cohen's κ.
5. **Rule:** if κ for the role is below 0.60, the guide is revised and DV is re-labelled before F1. This is a genuine blocker.

**Also measured:**
- AI repeat-run consistency on max(30, ⌈0.10 × N_AI⌉) reviews, each re-run in new sessions;
- owner–AI agreement.

None of these may be called inter-annotator agreement.

---

## 6. From DV to E: what happens and why

| Stage | What happens | Gate |
|---|---|---|
| DV pipeline and feasibility check (D6) | Claude re-runs every method on DV with the current code and computes the H2 pipeline on DV labels (development results only), including matched coverage and k_r per repository: the first real sign of whether the feasibility gate can pass | after DV labels + reliability |
| **F1: pre-test freeze** | Claude writes `docs/freeze/pretest_freeze.json` (hashes of code, protocol, guide, policy, scoring, run specification, baseline manifest, DV label hashes, ledger heads, Dataset A, prompt and packet rule, reliability, frame audit, specification-review record, feasibility, calibration) and tags `phase3-pretest-freeze`. **From then on nothing may change.** | **your explicit approval** |
| Test fetch and sealed run | Only now `fetch_pinned.py --include-test` works (it refuses before). Every method runs once; raw outputs are sealed (hashed) and you never see them; a mechanical step produces location-only candidates. | after F1 |
| Phase T annotation | The same loop as DV, on the 7 test repositories (quota 30 each); intra-rater re-label after ≥ 14 days. Test labels stay out of git until F2. **You record an attestation that the sealed outputs were not opened** (protocol, "Between F1 and F2"). | — |
| **F2: label freeze** | Claude writes `docs/freeze/label_freeze.json` (label, AI, adjudication and reliability hashes; unresolved list) and tags `phase3-label-freeze` | **your explicit approval** |
| **E: evaluation** | One run of the pre-registered analysis: H1, H2 (F-B), F-A, H3, H4, reported with the fixed statement templates. F-A is always described at natural coverage (D7). | **your explicit approval** |

---

## 7. You vs Claude at a glance

| Only YOU | CLAUDE can do (when you say go) |
|---|---|
| Write the AI-review identity file | Prepare the specification-review packet |
| Run every ChatGPT session (specification review, AI reviews, repeat runs) | Build prompts and packets; parse the saved replies |
| Decide each specification-review finding; sign off | Apply the changes you approve; update the adoption record |
| Label every candidate (pilot, synthetic, DV, T) | Issue batches; validate, hash and push ledgers; compare |
| Adjudicate every disagreement | Run adjudication; build final label files |
| Re-label the intra-rater sample after ≥ 14 days | Compute κ and agreement statistics; frame audit; D6 check |
| Approve F1, F2 and E (explicitly, in chat) | Write the freeze records and tags; fetch and seal the test run; run E |
| Decide D5, D10, D14 and the two document corrections | Implement the decided changes before F1 |

Claude will never: create or edit your labels or identity values; start annotation, F1, F2 or E on its own; access the test repositories before F1; show you blinded tool outputs; or claim accuracy figures before E.

---

## 8. Optional items vs genuine blockers

| Item | Type | Must be decided before | Default if you do nothing |
|---|---|---|---|
| V8 identity; specification review and sign-off; pilot/synthetic loops; DV labels; 14-day re-label; κ ≥ 0.60; F1, F2 and E approvals | **Genuine blockers** | their next stage | nothing proceeds |
| Loop tooling for pilot/synthetic (§4) | **Blocker** (Claude's work) | step 5 | — |
| Stale pilot figure (51.7% → 53.3%) and W6 citation precision | Should decide (document accuracy) | **F1** (documents freeze then) | they stay as written and are noted as known inaccuracies |
| D10 PROTOCOL_CONFIG (limitation vs implement) | Should decide | **F1** | reported as a limitation |
| **D14 Mehl scanner** | **Optional** | F1, if you ever want it run | kept outside F-A and F-B, reported separately with the corrected reason (it gives no migration recommendations by design). Nothing is blocked. |
| S1/W5 module-level typing; method-implied role display | Optional (software quality) | F1, if ever (code freezes then) | stays a documented limitation |
| D5 licence | Optional for research; needed for public release | publication | README says "none chosen" |
| D1 IEEE sample, D3 publication scope, D2 title, D11 novelty audit | Optional (publication) | after E | — |

---

## 9. In plain language: what you are approving and why

- **Why the AI identity first?** You will use ChatGPT as a second reader of your work. A scientific record must say exactly which AI, in which mode, with which settings, so anyone can judge or repeat it. Writing that down once, honestly, before the first use is what makes the AI reviews admissible.
- **Why a specification review?** Before anyone labels anything, a fresh reader checks that the rules are clear and consistent. Fixing a rule now is cheap. After labelling it would mean re-labelling, and after F1 it is not allowed at all. You stay the decision-maker: the AI only raises points.
- **Why the pilot and synthetic loops?** They are a rehearsal. You practise the exact labelling routine on small, low-stakes sets, and we find tool or guide problems before they can affect real data. The synthetic loop also checks that our generated "answer key" is correct.
- **Why DV annotation and the 14-day wait?** Your labels are the ground truth that every accuracy number will be measured against. Labelling some sites twice, two weeks apart, without looking at your first answers, shows whether your labels are stable. With only one human annotator, this is the honest substitute for a second annotator. If consistency is too low (κ < 0.60), the rules are improved first.
- **Why F1 before touching the test repositories?** F1 locks every rule, the code and the comparisons, and records their fingerprints. Only after that may the sealed test repositories be opened. Then nobody, including us, can tune anything to the test data, so the final results can be trusted.
- **Why F2 and E?** F2 locks your test labels before any score is computed. E runs the pre-registered analysis exactly once. Whatever comes out, positive or negative, is reported as it is.
- **What you are not approving today:** nothing in this checklist starts automatically. Each stage needs your explicit "go".
