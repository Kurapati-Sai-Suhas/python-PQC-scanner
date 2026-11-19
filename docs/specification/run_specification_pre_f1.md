# Pre-F1 run specification (owner decisions on executing protocol v1.0.5)

**Machine-readable form:** `run_specification_pre_f1.json`. The JSON is authoritative for method identifiers. `tests/test_run_specification.py` checks it against the code.

**Status: pre-F1.**
- It is hashed in the v1.0.5 adoption record (`adoption_record_v1.0.5.json`). The v1.0.4 record is kept unchanged.
- At F1, both files are hashed into `docs/freeze/pretest_freeze.json`: protocol "Stage F1", item 4 (baseline manifest) and item 7 (planned comparisons with their families).
- After F1 they may not change (protocol: "no change to … the baseline set or the analysis plan may influence Experiment E").

## Recorded owner decisions

| Id | Date | Decision |
|---|---|---|
| D7 | 2026-11-18 | **Option A.** RQ kept verbatim. F-B (H2a; H2-3, H2-4) compares at **matched recommendation volume** against the method/argument arms. F-A compares at **natural coverage** against the algorithm-name mapping, the method/argument-only mapping and the external tools. Every F-A finding is described as a natural-coverage comparison; no claim of superior correctness over algorithm-family baselines at comparable coverage. |
| D15 | 2026-11-18 | **`pqscan:B1-algorithm` is the single "simple algorithm-name mapping" in F-A**, using the mappings already in `pqscan/baselines/simple.py` (`ALG_RULE`, unchanged). **`pqscan:B1-dual` is descriptive only, outside F-A**, because it emits DUAL recommendations rather than a migration choice. The scanner is not modified or rebuilt. |

## Family F-A as it will be run (confirmatory; natural coverage)

| | Method identifier | Note |
|---|---|---|
| System | `pqscan:B4-full-T2` | `full` arm, τ = T2 (`pqscan/bench/fa.py` `SYSTEM`) |
| Baseline 1–6 | `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan` | pinned in `benchmark/baselines_manifest.json` |
| Baseline 7 | `pqscan:B1-algorithm` | RSA → KEM, EC → SIG, X25519/X448/XDH/DH → KEM, Ed25519/Ed448/EdDSA/DSA → SIG, unresolved → DUAL |
| Baseline 8 | `pqscan:B2-method-args` | the method/argument-only mapping (`method+args` arm, always recommend) |

**Procedure (analysis plan Sec. 9, unchanged):**
- one-sided exact McNemar on both-ran sites;
- Holm across the baselines that ran, one-sided α = 0.025;
- ≤ 8 members, as the protocol requires;
- coverage printed with every result.

**Not run / not scored:**
- CBOMkit: D4 = A.
- Mehl ESEM 2026 scanner: not in F-A, H1b or H4; produces repository-level readiness labels and no per-site migration recommendation by design (Mehl 2026, p. 3), so it cannot be scored on the recommendation outcome; a source repository exists (owner decision D14, 19 Nov 2026).

**Descriptive only:** `pqscan:B1-dual`.

## Family F-B (confirmatory; matched recommendation volume; unchanged)

| Comparison | Provenance-aware arm | Comparator |
|---|---|---|
| H2-1 (H2a) | `B3-full-noabst` | `B2-method-args` |
| H2-3 | `B3-full-noabst` | `method-args-recv-T0` |
| H2-4 | `B3-full-noabst` | `method-only-T0` |

Holm, m = 3, over guarded p-values, one-sided α = 0.025 (identifiers from `pqscan/baselines/simple.py` `H2_COMPARISONS`). H2b remains exploratory and outside error control.

## Owner decisions of 18 Nov 2026: pre-F1 decision register (PF-REG-2026-11-18)

Approved by the owner on 18 Nov 2026 (`docs/audit/owner_decision_register_v1.0.5.md`). The JSON is authoritative; this section repeats it.

| Id | Decision |
|---|---|
| H-1 | H1a and H1b keep their status as pre-registered threshold decision rules, without any multiplicity-controlled inference. H3 and H4 remain pre-specified secondary/descriptive analyses, without a confirmatory or family-wise error claim. The confirmatory families remain F-A and F-B only. |
| H-2 | H1a is met if and only if the point estimate of its proportion is >= 0.25. H1b is met if and only if, for every tool in the H1b set, the point estimate of (harmful + UNDECIDED + UNJUSTIFIED) / n_exec is >= 0.10, where harmful = INCORRECT with a harm category (scoring policy). Wilson 95% confidence intervals are always reported. Neither threshold changes. H1a numerator (owner decision TA08, r6): eligible primary-set test sites with obvious_from_name = false, including UNKNOWN/INDETERMINATE sites (their role does not follow from the name); denominator: all eligible primary-set test sites. Reported alongside: the evidence_needed categories and a sensitivity excluding INDETERMINATE sites. |
| H-3 | The primary H1 results use the primary-set eligible sites of the seven test repositories, with F2-frozen owner-final labels; 'the full real set' in the RQ1 row is read this way. Development and validation results are reported separately and never pooled with test results. For tool j, the H1b denominator is n_exec,j: the eligible sites on which j ran (scoring policy Sec. 5). Execution failures per tool are reported separately, by count and reason. |
| H-4 | The H1b set is pqcheck, pqc-audit, PostQuant, qsafe, QSA-regex and pqblocks-scan (the external tools; RQ1 asks about existing scanners). The internal arms pqscan:B1-algorithm and pqscan:B2-method-args are reported separately and are not in H1b. Excluded, with reasons: CBOMkit (not run, decision D4: an inventory tool without migration advice); Mehl's scanner (produces repository-level readiness labels and no per-site migration recommendation by design (Mehl 2026, p. 3), so it cannot be scored on the recommendation outcome; a source repository exists (owner decision D14, 19 Nov 2026)); pqscan:B1-dual (descriptive only, D15: it emits dual recommendations, not a specific migration choice). A tool in the set that runs but produces no scoreable output is reported as not assessable, and H1b is reported as not decidable for it. |

**H1b set (F12, H-4):** `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan`. Reported separately: `pqscan:B1-algorithm`, `pqscan:B2-method-args`. Excluded: CBOMkit (sonar-cryptography) (not run, decision D4 = A: an inventory tool without migration advice); Mehl ESEM 2026 scanner (results-only artefact without scoreable per-site recommendations); pqscan:B1-dual (descriptive only (D15): emits dual recommendations, not a specific migration choice).

### H-5: H3 (with owner choices C1 and C2)

- **status:** pre-specified secondary/descriptive analysis; no multiplicity-controlled or confirmatory claim (H-1)
- **population:** Dataset B, the seven test repositories, primary-set eligible sites; n_r = sites where pqscan ran (the common evaluable set of both arms; arm-level failures reported)
- **arms:** {"tau_T2_policy": "pqscan:B4-full-T2", "always_recommend": "pqscan:B3-full-noabst (Module C full, tier threshold T0). It recommends at every site where it reaches a determinate role, at any evidence tier, but it still abstains on UNKNOWN roles, so it is not literally universal recommendation; its natural coverage is reported explicitly and is not assumed to be 100%."}
- **coverage points:** ["7/10", "4/5", "9/10"]
- **target count:** K_r(c) = ceil(c * n_r), c held as an exact fraction
- **t2 to coverage:** If R_r^T2 >= K_r(c), withdraw R_r^T2 - K_r(c) recommendations of the T2 policy: evidence tier ascending (T2 before T3), then ascending SHA-256 of '20261113|H3-T2|<repo>|<site_id>' within a tier (the deterministic rule of H2 matching); a withdrawn recommendation is judged ABSTAIN; the order does not depend on c, so kept sets are nested. If R_r^T2 < K_r(c), repository r cannot reach c; nothing is extrapolated.
- **always recommend comparison:** B3-full-noabst at its own natural coverage (sum_r R_r^AR / sum_r n_r, reported). T2 versus always-recommend is a natural-coverage comparison, never a matched-coverage one, and is always labelled so.
- **random withholding:** Seeds 20261113:withhold:001 ... 20261113:withhold:100, frozen before F1. For seed s, the per-repository order of B3-full-noabst's recommended sites is the ascending SHA-256 (hexadecimal text) of UTF-8 '<s>|H3-withhold|<repo>|<site_id>'; no random-number generator is used. At coverage c the first K_r(c) sites keep their recommendation and the rest are judged ABSTAIN. The same order is used at 70%, 80% and 90%, so the subsets are nested. If R_r^AR < K_r(c), the random comparison cannot reach c.
- **estimability C1:** If any of the seven repositories has n_r = 0, every coverage point is NOT ESTIMABLE. Point c is estimable only if, in all seven repositories, R_r^T2 >= K_r(c) and R_r^AR >= K_r(c); otherwise the pooled point is NOT ESTIMABLE. Per-repository results are always reported where available. No repository is removed and the population never changes between points.
- **harmful rate:** HR(c) = sum_r H_r(c) / sum_r n_r (frozen scoring: harmful = INCORRECT with a harm category; denominator n_exec); HR_T2(c); HR_AR at natural coverage; HR_k(c) per seed and HR_rand(c) = mean over the 100 seeds.
- **reported per point:** HR_T2(c), HR_AR and HR_rand(c); the random distribution (minimum, 2.5th percentile, median, 97.5th percentile, maximum) and its standard deviation across seeds; a within-repository site bootstrap 95% CI for HR_T2(c) - HR_rand(c) (1,000 resamples, seed 20261113); per-repository values; the existing risk-coverage curves and AURC, unchanged.
- **decision C2:** At each coverage point c in {70%, 80%, 90%}, evaluated separately, the point comparison holds if HR_T2(c) < HR_AR (natural coverage) and HR_T2(c) < HR_rand(c), strictly, on point estimates. The overall H3 criterion is MET only if all three points are estimable and the point comparison holds at every point; NOT MET if all three are estimable and any comparison fails; NOT ASSESSABLE if any point is not estimable. Every estimable point is always presented separately.
- **always-recommend reporting (TA03):** The always-recommend half of decision C2 compares at different coverages and is therefore coverage-confounded under the per-site harmful rate (owner decision TA03, r6): it is always printed with both arms' coverages and with each arm's per-recommendation risk (harmful / recommended). The random-withholding half is the coverage-matched comparison. Decision rule C2 is unchanged.
- **bootstrap procedure (TA28):** Bootstrap for HR_T2(c) - HR_rand(c) (owner decision TA28, r6): 1,000 resamples drawn with numpy default_rng(20261113); in each resample, sites are resampled with replacement within each repository; K_r(c) is recomputed from the resampled n_r; the T2 withdrawal uses the frozen SHA-256 order (copies of a duplicated site are ordered by copy index); HR_rand(c) is recomputed as the mean over the 100 frozen withholding orders, each applied to the resampled sites; the 95% CI is the percentile interval. A resample in which a point is not estimable is counted and reported; the interval uses the estimable resamples.
- **code note:** New H3 code goes in a new module: pqscan/bench/stats.py (risk_coverage, aurc) belongs to the E30 calibration closure and is not modified.

### H-6: H4 (with owner choice C3)

- **status:** pre-specified secondary/descriptive analysis; no confirmatory or family-wise error claim (H-1)
- **data:** Dataset A's frozen base-variant pairs (b, o): base case b's identity instance and its variant under operator o, one site each. Pairs per operator: alias-import, wrapper-function, class-method 61 each; cross-function, dict-dispatch, loaded-key 48 each.
- **tool set:** Every runnable baseline and pqscan arm is listed by name in this run specification before the evaluation; the proposed analyser is pqscan:B4-full-T2. Exclusions are pre-specified with reasons only.
- **outcomes:** Classification outcome: no finding, or a finding with its reported category (each tool's field fixed in the inventory). Recommendation outcome: (action, rec_class) in the common vocabulary: RECOMMEND with its class, FLAG_NO_TARGET, ABSTAIN or NO_FINDING.
- **denominator C3:** N(o, j) = the pairs for operator o on which tool j ran on both the identity and the variant instance, eligible and ineligible cases included. Execution-failure pairs are counted and reported separately and excluded from the rate. The same N(o, j) is used for classification and recommendation flips.
- **flip rates:** FR_cls(o, j) = #{pairs in N(o, j) whose classification outcome differs between identity and variant} / |N(o, j)|; FR_rec(o, j) = #{pairs in N(o, j) whose recommendation outcome differs between identity and variant} / |N(o, j)|.
- **decision:** All decisions use point estimates, with Wilson 95% confidence intervals reported for every rate. Part 1: for every tool j in the pre-specified H4 baseline set, at least one pre-registered operator o - loaded-key included, because the original hypothesis names it - has FR_cls(o, j) >= 0.30 or FR_rec(o, j) >= 0.30 (wording kept: 'classification or recommendation'). Both flip types are always reported separately. The prediction (loaded-key, cross-function) is reported as confirmed or not. loaded-key is reported separately as an evidence-condition change, not a semantics-preserving transformation. Part 2: for the proposed analyser, separately under alias-import and under wrapper-function: classification stability 1 - FR_cls and recommendation stability 1 - FR_rec are reported separately; a pair is invariant only if neither its classification nor its recommendation flipped; Part 2 is met if the invariant share is >= 0.90 for both operators. loaded-key never enters the invariance calculations.

**H4 tool inventory (second review G08; the JSON is authoritative).** Inventory of the actual runnable identifiers (second review G08), taken from the code and the manifest. Owner decision G08 (19 Nov 2026): the H4 Part 1 set is the F-A baseline set, frozen below.

- Proposed analyser: `pqscan:B4-full-T2`.
- Runnable external tools: `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan`.
- Runnable pqscan arms: `pqscan:B1-algorithm`, `pqscan:B1-dual`, `pqscan:B2-method-args`, `pqscan:B3-full-noabst`, `pqscan:B4-full-T2`, `pqscan:method-args-recv-T0`, `pqscan:method-only-T0`.
- Not runnable: CBOMkit (not run, D4 = A); Mehl ESEM 2026 scanner (produces repository-level readiness labels and no per-site migration recommendation by design (Mehl 2026, p. 3), so it cannot be scored on the recommendation outcome; a source repository exists (owner decision D14, 19 Nov 2026)).
- Sources: `pqscan/baselines/adapters.py ADAPTERS`; `pqscan/baselines/simple.py ARMS and H2_ARMS`; `benchmark/baselines_manifest.json not_runnable`.
- Decision set for Part 1 ('every baseline'), **owner decision G08 (19 Nov 2026): the F-A baseline set**: `pqcheck`, `pqc-audit`, `PostQuant`, `qsafe`, `QSA-regex`, `pqblocks-scan`, `pqscan:B1-algorithm`, `pqscan:B2-method-args`. `pqscan:B4-full-T2` is the proposed analyser (Part 2). `pqscan:B1-dual` is descriptive only (D15). The arms `pqscan:B3-full-noabst`, `pqscan:method-args-recv-T0` and `pqscan:method-only-T0` are reported separately and are not in Part 1. Registry: `pqscan/bench/h4.py`.
- **Owner confirmation (19 Nov 2026, third review TB01; `docs/audit/owner_decision_g08_confirmation_2026-11-19.md`).** H4 Part 1 contains exactly these eight identifiers. The inclusion criterion is membership in the registered F-A baseline set, not evidence tier and not external versus internal: `pqscan:B2-method-args` is included because it belongs to the F-A set, although it is a T0 arm. The other five pqscan arms (`pqscan:B4-full-T2`, `pqscan:B1-dual`, `pqscan:B3-full-noabst`, `pqscan:method-args-recv-T0`, `pqscan:method-only-T0`) are reported separately and are never added to Part 1.
- **Why H1b and H4 Part 1 differ.** Both say 'every baseline', but they use different, separately registered sets on purpose. H1b (RQ1) asks about existing scanners, so its set is the six external tools (F12, H-4, unchanged). H4 Part 1 (RQ4) asks whether transformations change the outcome of any baseline method the proposed analyser is compared with, so its set is the full F-A baseline set. The set used is printed next to every H1b and H4 result.

**[S-ELIG]**

Eligible-only recommendation-flip sensitivity (H4; secondary; reported separately). FR_rec^elig(o, j) = #{pairs in N^elig(o, j) whose recommendation outcome differs between the identity and the variant instance} / |N^elig(o, j)|, where N^elig(o, j) is the set of base–variant pairs for operator o whose frozen Dataset A label is eligible and on which tool j ran successfully on both the identity and the variant instance. It uses the same common recommendation-outcome vocabulary as the primary rate. It is reported separately from the primary all-pair classification and recommendation flip rates, FR_cls(o, j) and FR_rec(o, j), and is never substituted for them in the primary H4 decision.

## What this record does not change

- The wording of RQ1–RQ4 and H1–H4 and every threshold (25%, 10%, 30%, 90%; 70/80/90% coverage points).
- Primary metrics, frozen scoring rules, the confirmatory families F-A and F-B, D7 and D15.
- All thresholds. The H1, H3 and H4 decision rules are interpreted above (H-1 to H-6), not changed.
- The F-A / F-B methodology.
- The baseline manifest.
- The test-split safeguards: `scripts/fetch_pinned.py --include-test` refuses until the F1 record and tag exist.

**Pre-F1 analysis decisions (r6, 19 Nov 2026).** H4 quantifier (TA04): Part 1 uses the per-tool reading (for each baseline some operator meets the threshold; owner decision TA04, r6). Also reported, descriptively only: whether one operator meets FR >= 0.30 for all eight baselines. H4 population (TA05): Part 1 uses all base-variant pairs (61 or 48 per operator). Part 2 (the proposed analyser's invariance) uses the 30 synthetic-holdout base cases as its primary population, because the 31 synthetic-dev base cases were visible during development; Part 2 on all pairs is reported as well (owner decision TA05, r6). K = 7 (TA17): The Experiment E driver asserts that exactly the seven test repositories are present before any comparison is analysed, so K = 7 always (owner decision TA17, r6); pqscan/bench/h2.py, part of the calibration closure, is not changed. TA01: Historical verification of S16 (19 Nov 2026; docs/audit/ta01_s16_historical_verification.md): the planning calibration observed S16 (random repositories) above the criterion before protocol v1.0.4 was adopted; the adopted plan Sec. 11 item 2 lists all 18 single-comparison scenarios, S16 included, without an exemption; the exemption exists only in the acceptance script. S16 is therefore NOT excluded retrospectively: acceptance criterion 2 is not met under the adopted text, and F1 stays blocked until an adopted and calibrated solution exists (owner decision required). Record: `docs/audit/owner_decisions_pre_f1_analysis_2026-11-19.md`.
