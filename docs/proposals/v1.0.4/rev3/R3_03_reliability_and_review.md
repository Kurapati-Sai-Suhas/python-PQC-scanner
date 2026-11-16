# R3-03 Annotation reliability and the ChatGPT review procedure (PROPOSED, revision 3)

## 1. Three different statistics (never called inter-annotator reliability)

| Statistic | Who vs. who | What it shows | What it does not show |
|---|---|---|---|
| **Owner intra-rater consistency** | owner at time 1 vs. owner ≥ 14 days later | stability of the ground truth | correctness; agreement with anyone else |
| **Owner–AI agreement** | owner primary vs. blind ChatGPT review | where an independent machine reading of the same code differs | correctness (errors may be shared); human reliability |
| **AI repeat-run consistency** | ChatGPT run 1 vs. run 2 (new isolated sessions) | stability of the AI review | correctness |

## 2. Phases

- **Phase DV:** development and validation combined (6 repositories), sampled as one phase.
- **Phase T:** test (7 repositories), a separate phase, after F1.
- Pilot (31) and synthetic subset (78): reported separately, with no re-label rule.

## 3. Intra-rater sample (per phase)

| Parameter | Definition |
|---|---|
| Denominator N | every candidate issued in the phase with a final label (B0 and B1+; not annotator-added sites) |
| Sample size | n = max(50, ⌈0.10 · N⌉). Expected: Phase DV about 468 candidates → n = 50; Phase T about 630 → n = 63 (expected workload scenario, assumed) |
| Seed | 20261113, with the phase name as a suffix (`20261113:intra:DV`, `20261113:intra:T`) |
| Selection | stratified by repository in proportion to N_r, with at least 3 per repository. Within each repository, half from owner-final eligible and half from ineligible candidates (or all available, if fewer). The script selects; the owner is not told the strata |
| Gap | the re-label starts ≥ 14 days after the latest primary submission among the sampled candidates; the script refuses earlier |
| Blinding | earlier labels are not visible; candidates are presented in a new seeded order |
| Rule (V3) | point estimate of κ(gt_role) < 0.60 → Phase DV: revise the guide, re-label Phase DV before F1; Phase T: all test results labelled exploratory |
| Reporting | per field (eligible, gt_role, assessability, hybrid_component, obvious_from_name, evidence_needed, key_provenance): n, raw agreement, Cohen's κ with a bootstrap 95% CI (resampling items within repositories), the confusion matrix, per-class specific agreement (2·n_ii / (row_i + col_i)) for classes with ≥ 5 items in either rating, and the class prevalence. Classes with < 5 items are listed with counts only, and no per-class statistic is computed |

**Limitations of κ (reported with it):**
- κ depends on prevalence and marginal imbalance. With a dominant class (for example SIGN, or NONE among all candidates), κ can be low while raw agreement is high, or the reverse.
- Rare roles (PK_ENCRYPT, PK_DECRYPT, PROTOCOL_CONFIG) contribute almost nothing to pooled κ.
- With n of about 50, the 95% range of κ is about ±0.12–0.18 (simulated in revision 2's audit).
- For these reasons κ is never reported alone.

## 4. Owner–AI agreement and AI repeat-run

| Statistic | Denominator | Notes |
|---|---|---|
| Owner–AI agreement | every candidate with an owner primary and an AI review in the phase; AI "insufficient context" items are excluded and counted | same reporting set as Sec. 3; also stratified by `context_used` (Sec. 6) |
| AI repeat-run | a seeded sample of max(30, ⌈0.10 · N_AI⌉) AI-reviewed candidates per phase, re-run in new isolated sessions | raw agreement and κ per field |

## 5. ChatGPT review procedure (V8, revision 3)

1. **Isolation.** The existing project conversation, and any conversation that has seen the project, must never be used. Each batch uses a fresh ChatGPT **Temporary Chat**, or an API call with a pinned model identifier where available.
   - Temporary Chat settings: custom instructions off, memory and chat-history reference off, no Project, no connectors, no file library, web browsing/search off.
   - API: the owner's own key; Claude never handles it.
2. **Inputs, and nothing else:**
   - the approved annotation guide v1.1 decision procedure and field definitions;
   - the fixed prompt template;
   - the permitted packet(s).

   Never the owner's label, tool output, the project's name, pqscan, hypotheses or results.
3. **Fixed prompt:** versioned and hashed (SHA-256 in the F1 record). The packet hash is recorded per candidate.
4. **Identification:** the interface (ChatGPT web, app or API); the model as displayed in the model picker, or the API model identifier; the app version if shown; date and time in UTC.
5. **Verbatim export:** the response saved unedited, plus the exported conversation (web data export, or the API response JSON).
6. **Repeat-run sample:** Sec. 4.

**What can and cannot be reproduced.**
- **Consumer interface:** it does not expose a model snapshot, and the provider can change the model behind a name without notice. A re-run can therefore neither be guaranteed to reach the same model nor to give the same text.
- **What is reproducible:** the *analysis*, from the archived verbatim responses. The *generation* of those responses is not.
- **API with a pinned snapshot:** improves model identity. Outputs can still vary run to run (sampling, serving changes), so the archive remains the record.

## 6. Context packets (V16)

The owner reads the whole repository; the AI sees a packet. Owner–AI disagreement therefore mixes reading differences with context differences.

**Recommended:**
- The AI receives the packet only.
- The owner labels from the full repository, as ground truth needs, and records `meta.context_used`:
  - `packet_sufficient`: the owner's label needed nothing outside the packet;
  - `extended`: list the extra files and lines consulted.
- Owner–AI agreement is reported overall and for the `packet_sufficient` subset, which is the interpretable comparison.
- Disagreements in which the AI's answer turns on missing context are tagged `context_difference`.

**Alternative (more time):** the owner first labels from the identical packet, then from the full repository. This doubles the owner's reading time for about 1,100 candidates.

## 7. Wording

None of these statistics may be called independent human validation or inter-annotator reliability. The review is "a separately conducted AI-assisted review".
