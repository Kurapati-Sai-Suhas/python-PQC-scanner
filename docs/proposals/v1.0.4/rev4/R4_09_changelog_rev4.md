# Methodology change log, revision 3 → 4 — PROPOSED, NOT ADOPTED

Revisions 1–3 are preserved unchanged. Protocol v1.0.3 and guide v1.0 remain in force.

| Area | Revision 3 | Revision 4 | Basis | Decision |
|---|---|---|---|---|
| H2 arms | unspecified threshold | full vs. method+args at T0, matched; proposed system (T2) secondary | method+args tiers are only T0/T1 (`docs/dev/roles_on_pilot.md`) | V18 |
| H2 confirmatory claim | fixed sequence; margin confirmatory | direction confirmatory (B1); margin exploratory (bootstrap lower bound) | margin power 0.07–0.43 at a true 15 pp (`results/h2_power.csv`) | V10a‴ |
| Holm family | m = 4 | m = 3 (B1, B3, B4); m = 4 as the owner's alternative; per-step table | FWER ≤ 0.0249 for both (`results/fwer.md`) | V10b″ |
| Inferential target | superpopulation (repository-level t confirmatory) | the 7 selected repositories (design-based); generalisation exploratory | purposive selection (`repository_split.md`) | V13′ |
| Primary H2 test | repository-level t | stratified re-matching bootstrap; site-level tests secondary | matching variance ratio 0.486; score-test rejection 0.0025; bootstrap 0.0145 (`results/matching.md`) | V13′ |
| Site-level tests | "invalid with clustering" | valid for fixed repositories (Type I ≤ 0.030); invalid for generalisation (up to 0.118) | `results/h2_type1.csv` | V13′ |
| Sign-flip robustness | robustness under Holm | descriptive only (smallest p 0.0078 > α/4) | arithmetic; zero power at α/4 | V13′ |
| Coverage | implied 1 − abstention | RECOMMEND / eligible (frozen); within-repository output-adaptive matching; fixed-target variant secondary; 100-seed sensitivity; worked example | `data_dictionary.md`; `pilot_harness/summary.md` | V12′ |
| S2, annotator-added, false positives | excluded and reported | adds a per-tool false-positive profile and out-of-scope findings; primary population defined | R4-05 | V14′ |
| Reliability | intra-rater per phase | 8 fields; within-repository bootstrap CI; enforced gap | R4-05 | V3′ |
| Frame audit | descriptive | explicit can / cannot estimate | R4-05 | V7′ |
| Context | `context_used` | recorded before the AI review in the hashed file; criteria; packet-first 10% subset | R4-05 | V16′ |
| Statistical code | `rev3/scripts` | `rev4/scripts`, with independent cross-checks (numeric optimiser, scipy, statsmodels, brute force) and simulation tests; 27 tests pass | `results/unit_tests.txt` | — |

**Corrections to revision 3:**
1. Revision 3 called the site-level score test invalid with 7 repositories. That holds only for generalisation.
2. Revision 3's power tables combined random-effects heterogeneity with confirmatory claims about the 7 repositories.
3. Revision 3 did not analyse the dependence that matching creates.
4. Revision 3 listed sign-flip as robustness at a Holm level it cannot reach.
