# Owner decision register for the pre-F1 corrections (protocol v1.0.5)

**Status: APPROVED by the owner on 18 Nov 2026** ("Approve register"), after four review rounds of the proposed register. Approved before any labelling and before any test-split access.

**Source of the findings.** The isolated ChatGPT specification review of protocol v1.0.4 (21 findings, F01–F21), run by the owner in a fresh Temporary Chat with the recorded AI-review identity. The verbatim reply is kept by the owner outside the repository. That review is an AI review with owner sign-off; it is **not** an independent human review, and the external human review required before F1 (F14) is still pending.

**Verification of each finding** against the repository: `docs/audit/chatgpt_review_finding_verification.md` (and `.csv`). **Correction plan and log:** `docs/audit/pre_f1_correction_plan.md`, `docs/audit/pre_f1_correction_log.md`. **Amendment record:** `docs/specification/amendment_v1.0.5.md`.

**Unchanged by every decision below:** the wording of RQ1–RQ4 and H1–H4; every threshold (25%, 10%, 30%, 90%; the 70/80/90% coverage points); the primary metrics and frozen scoring rules; the baseline membership; the confirmatory families F-A and F-B; D7 and D15; τ = T2; the sampling unit, pool and orders (V6). **Safeguards kept:** no held-out test access; no annotation, pilot or synthetic loop without approval; no F1, F2 or E.

## 1. Register

| ID | Final decision (approved) | Version impact | Blocks |
|---|---|---|---|
| F01 | PROTOCOL_CONFIG (kind c) is eligible when it occurs; D10 (the scanner does not emit it) stays a stated limitation | Taxonomy v1.1 | Phase 3 |
| F02 | Guide Step D follows taxonomy rule 1 (private key: SIGN with secondary VERIFY; public key with verify-only consumers: VERIFY) | Guide v1.2 | Phase 3 |
| F03 | Statement-level sampling (V6) kept. Deterministic rule for multi-call candidate statements (guide Step A); issued candidates marked `multi_call`. Measurement evidence (8 of 3,503 DV pool candidates) and regression tests kept. Pool and orders not rebuilt. | Guide v1.2; taxonomy v1.1; tooling | Phase 3 |
| F04 | Option 1: the primary C_r estimate describes the **commonly evaluable sites** when failures exist; **S-F1 separately describes the sampled primary set** under the rule that concordant failures are incorrect for both arms; the two are **never claimed identical when failures exist**; weight denominator corrected to m_r; S-F2 kept; failures reported by stratum (Sec. 3) | Plan v1.0.1; tooling | Phase 3; paper wording |
| F05 | Separate F-A Type I error simulation. No F-A validity claim until it passes. If any criterion fails: stop and present alternatives for separate owner approval; the method is never changed automatically. **Result: PASS** | Plan v1.0.1; acceptance artefact | F-A confirmatory |
| F06 | Test-output blinding is disclosed as **self-attested, not independently enforced**; never claimed otherwise | Protocol v1.0.5 | Paper wording |
| F07 | Forbidden content → the candidate is **excluded** from the AI review, with no reason override. Proceed only for a **verified false positive** with file:line evidence. Decision file SHA-256 recorded in the ledger. No redaction. | Guide v1.2; tooling | Phase 3 |
| F08 | `hybrid_component = true` needs an approved PQ component of the matching family (ML-KEM; ML-DSA or SLH-DSA) and evidence of actual combination; the scanner's missing SLH-DSA prefix (cryptography 47.0.0 has none) documented as a limitation | Guide v1.2; protocol threats | Phase 3 |
| F09 | A primary CORRECT means a compatible target family only, not a verified complete KEM + KDF + AEAD redesign | Scoring policy v1.0.1 (note) | Paper wording |
| F10 | Unresolved-field convention documented (provisional value; `meta.unresolved`; required `unresolved_reason`, already enforced by the meta schema) | Guide v1.2 | Phase 3 |
| F11 | Packet-first rule documented as implemented: rate max(10%, 60/N_planned); ≥ 50 is an expected count; realised count reported | Protocol v1.0.5; guide v1.2 | Phase 3 |
| F12 / H-4 | H1b set = pqcheck, pqc-audit, PostQuant, qsafe, QSA-regex, pqblocks-scan; B1/B2 reported separately; CBOMkit, Mehl and B1-dual excluded with reasons | Run specification | Phase 3 |
| F13 | Data dictionary updated to the single-investigator records; rate denominators n_exec as in the frozen scoring policy | Dictionary v1.1 | Neither |
| F14 | **External human review is a mandatory F1 prerequisite; pending, not waived, not marked complete** | Protocol v1.0.5 | **Blocks F1** |
| F15 | Separate owner and AI example records, each with `label_kind` | Guide v1.2 | Neither |
| F16 | v1.0.3, `candidates.py`, `frame_audit.py` and an adopted/pending decision page added to the second review packet; H1/H3/H4 recorded as H-1 to H-6 | Packet; run specification | Second review |
| H-1 | H1a/H1b keep their threshold decision-rule status without multiplicity-controlled inference; H3/H4 are pre-specified secondary/descriptive analyses | Run specification | Phase 3 |
| H-2 | Point estimates against the frozen 25% and 10%; Wilson 95% CIs always reported | Run specification | Phase 3 |
| H-3 | Primary H1 = primary-set eligible sites of the seven test repositories; DV reported separately, never pooled; H1b denominators n_exec per tool; failures reported separately | Run specification | Phase 3 |
| H-5 | H3 definition of Sec. 4, including owner choices **C1** and **C2** and the accurate description of B3-full-noabst | Run specification; plan Sec. 12 seeds | Phase 3 |
| H-6 | H4 definition of Sec. 5: primary denominator N(o, j) over all pairs where the tool ran on both instances, eligible and ineligible cases included (owner choice **C3**); failures counted separately; decision wording as stated; plus the **[S-ELIG]** paragraph verbatim | Run specification | Phase 3 |
| F17 | Bounds labelled per comparison, not multiplicity-adjusted | Plan v1.0.1 | Paper wording |
| F18 | Frame-audit seed, order and stopping rule stated as implemented (a stopping-rule defect found while doing so was fixed and tested) | Protocol v1.0.5; tooling | Neither |
| F19 | c_DV = c_pool on the DV primary set, per comparison | Plan v1.0.1 | Phase 3 |
| F20 | F1 is not permitted after a failed calibration | Plan v1.0.1; protocol v1.0.5 | Neither |
| F21 | An observed escape beyond the bounded scope → UNKNOWN, ahead of KEY_MATERIAL_ONLY; "storage" means within the scope | Taxonomy v1.1; guide v1.2 | Phase 3 |
| Pilot exposure | The 5 pilot sites shown as guide worked examples are a separately reported subset; their AI agreement is never blind evidence; the other 26 stay distinguishable | Decision record; tooling | Before the pilot |
| E01 | The owner's AI identity file stays **unchanged and uncommitted**; the evidence-register correction is prepared as a patch file only (`docs/audit/pending/e01_identity_committed.patch`) and applied only with separate owner approval | None now | Paper evidence |

## 2. Owner choices recorded during the review of the register

- **H3(a):** deterministic tier-based withdrawal of the T2 policy to a fixed target count (T2 tier before T3; SHA-256 tie-break as in H2 matching); not estimable when the natural T2 count is below the target; never extrapolated.
- **H3(b):** always-recommend (B3-full-noabst) at its own natural coverage, reported explicitly; a natural-coverage comparison.
- **H3(c):** seeds `20261113:withhold:001` … `:100`, frozen before F1; nested per-repository permutations; the seed-to-order mapping is recorded (Sec. 4).
- **H4(d):** loaded-key retained in the H4 flip analysis (named by the original hypothesis), reported separately as an evidence-condition change, excluded from invariance.
- **H4(e):** classification and recommendation flips reported separately; "classification or recommendation" kept; the 30% criterion may be met by either outcome type; combined invariant outcome defined.
- **C1:** all seven repositories must reach both targets at a coverage point, otherwise NOT ESTIMABLE.
- **C2:** MET only if all three points are estimable and every comparison holds; NOT MET; NOT ASSESSABLE.
- **C3:** primary recommendation-flip denominator over all pairs where the tool ran on both instances; eligible-only rate as a separate sensitivity ([S-ELIG]).

## 3. F04: estimands (analysis plan v1.0.1 Sec. 2)

For repository r and stratum h: U_r,h the eligible frame; E_r the sampled primary set with m_r,h per stratum and m_r = |E_r|; C_r ⊆ E_r the sites where both arms ran, with c_r,h per stratum and n_r = |C_r|; U^ev_r,h the sites where both arms would run, ρ_r,h = |U^ev_r,h| / |U_r,h|.

- Estimand A (corrected): w_r,h = m_r,h / m_r; P_r^A = Σ_h w_r,h · Uniform(U_r,h); δ_r^A = Ψ(P_r^A); δ^A = (1/7) Σ_r δ_r^A.
- Primary target when failures exist: π_r = Σ_h w_r,h ρ_r,h; P_r^ev = Σ_h (w_r,h ρ_r,h / π_r) · Uniform(U^ev_r,h); δ_r^ev = Ψ(P_r^ev). The primary δ̃_r on C_r estimates δ_r^ev (commonly evaluable sites).
- S-F1 (sampled primary set; concordant failures incorrect for both arms): δ_S-F1,r = [n_r·δ̃_r + Σ_F-only X − Σ_M-only Y] / m_r; for H2 (one-arm failures stop the run) δ_S-F1,r = (n_r / m_r)·δ̃_r, targeting π_r·δ_r^ev.
- S-F2 unchanged: [(n_r·δ̃_r + Σ_F-only X − Σ_M-only Y − fail_F,r) / m_r, (… + fail_M,r) / m_r].
- They coincide iff π_r = 1 (no eligible site fails). Otherwise they differ (factor π_r within a repository; reweighting across repositories; stratum shift), and are never claimed identical.

## 4. H3 (H-5)

**Arms.** τ = T2 policy `pqscan:B4-full-T2`. The pre-registered "always recommend" comparator is `pqscan:B3-full-noabst` (Module C `full`, threshold T0); it recommends at every site where it reaches a determinate role, at any tier, **but still abstains on UNKNOWN roles**, so it is not literally universal; its natural coverage is reported explicitly.

**Population.** Dataset B, seven test repositories, primary-set eligible sites; n_r = sites where pqscan ran. Coverage points c ∈ {7/10, 4/5, 9/10}, exact fractions. Target count K_r(c) = ⌈c · n_r⌉.

**T2 to coverage c.** If R_r^T2 ≥ K_r(c), withdraw R_r^T2 − K_r(c) recommendations: tier ascending (T2 before T3), then ascending SHA-256 of `20261113|H3-T2|<repo>|<site_id>`; withdrawn = ABSTAIN; nested across c.

**Random withholding.** Seeds `20261113:withhold:001` … `:100`, frozen before F1. Order for seed s: ascending SHA-256 (hex text) of UTF-8 `<s>|H3-withhold|<repo>|<site_id>` over B3's recommended sites; no random-number generator. The first K_r(c) keep their recommendation; the rest are ABSTAIN; the same order at every c (nested).

**Estimability (C1).** Any repository with n_r = 0 → every point NOT ESTIMABLE. Point c is estimable only if, in all seven repositories, R_r^T2 ≥ K_r(c) and R_r^AR ≥ K_r(c); otherwise NOT ESTIMABLE. Per-repository results always reported; no repository removed; the population never changes between points.

**Harmful rate (frozen scoring, n_exec).** HR_T2(c) = Σ_r H_r^T2(c) / Σ_r n_r; HR_AR at natural coverage Σ_r R_r^AR / Σ_r n_r (reported); HR_rand(c) = mean over the 100 seeds; random distribution (min, 2.5th pct, median, 97.5th pct, max) and SD; within-repository site bootstrap 95% CI for HR_T2(c) − HR_rand(c) (1,000 resamples, seed 20261113); per-repository values; risk–coverage curves and AURC unchanged. T2 versus always-recommend is always labelled a natural-coverage comparison.

**Decision (C2).** "H3 is a pre-specified secondary/descriptive analysis; no multiplicity-controlled or confirmatory claim is made. At each coverage point c ∈ {70%, 80%, 90%}, evaluated separately, the point comparison holds if HR_T2(c) < HR_AR (natural coverage) **and** HR_T2(c) < HR_rand(c), strictly, on point estimates. The overall H3 criterion is **MET** only if all three points are estimable and the point comparison holds at every point; **NOT MET** if all three are estimable and any comparison fails; **NOT ASSESSABLE** if any point is not estimable. Every estimable point is always presented separately."

## 5. H4 (H-6)

**Data.** Dataset A's frozen base–variant pairs (b, o), one site each: alias-import, wrapper-function, class-method 61 pairs each; cross-function, dict-dispatch, loaded-key 48 each. **Tool set:** every runnable baseline and pqscan arm named before evaluation; proposed analyser `pqscan:B4-full-T2`; pre-specified exclusions with reasons only. **Outcomes:** classification (no finding, or a finding with its reported category; field fixed per tool in the inventory); recommendation ((action, rec_class): RECOMMEND with class, FLAG_NO_TARGET, ABSTAIN, NO_FINDING).

**Primary denominator (C3).** N(o, j) = pairs for operator o where j ran on both instances, eligible and ineligible cases included; failure pairs counted and reported separately and excluded. FR_cls(o, j) and FR_rec(o, j) = flips / |N(o, j)|.

**[S-ELIG]**

Eligible-only recommendation-flip sensitivity (H4; secondary; reported separately). FR_rec^elig(o, j) = #{pairs in N^elig(o, j) whose recommendation outcome differs between the identity and the variant instance} / |N^elig(o, j)|, where N^elig(o, j) is the set of base–variant pairs for operator o whose frozen Dataset A label is eligible and on which tool j ran successfully on both the identity and the variant instance. It uses the same common recommendation-outcome vocabulary as the primary rate. It is reported separately from the primary all-pair classification and recommendation flip rates, FR_cls(o, j) and FR_rec(o, j), and is never substituted for them in the primary H4 decision.

**Decision.** "H4 is a pre-specified secondary/descriptive analysis; no confirmatory or family-wise error claim is made. All decisions use point estimates, with Wilson 95% confidence intervals reported for every rate. **Part 1.** For every tool j in the pre-specified H4 baseline set, at least one pre-registered operator o — loaded-key included, because the original hypothesis names it — has FR_cls(o, j) ≥ 0.30 **or** FR_rec(o, j) ≥ 0.30 (wording kept: 'classification or recommendation'). Both flip types are always reported separately. The prediction (loaded-key, cross-function) is reported as confirmed or not. loaded-key is reported separately as an evidence-condition change, not a semantics-preserving transformation. **Part 2.** For the proposed analyser, separately under alias-import and under wrapper-function: classification stability 1 − FR_cls and recommendation stability 1 − FR_rec are reported separately; a pair is **invariant** only if neither its classification nor its recommendation flipped; Part 2 is met if the invariant share is ≥ 0.90 for **both** operators. loaded-key never enters the invariance calculations."
