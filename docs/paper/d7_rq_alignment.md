# Author decision D7: research-question alignment ("at comparable coverage")

**Status: OPEN. The owner decides. Nothing in the protocol or the RQ has been changed.**

**Adopted RQ (verbatim):** *Does bounded key-provenance-aware cryptographic role inference improve the correctness of post-quantum migration recommendations at comparable coverage for Python cryptographic call sites, compared with algorithm-family and method/argument-based baselines?*

## 1. Which comparisons are coverage-matched (protocol v1.0.4; analysis plan v1.0)

| Comparison | Comparator | Coverage handling | Status | Answers which part of the RQ |
|---|---|---|---|---|
| H2-1 (H2a) | `method+args` at T0 | **Matched**: equal RECOMMEND count per repository; tier-ordered withdrawal; tie-average; guard on the coverage gap; feasibility gate | Confirmatory, family F-B | "improve correctness **at comparable coverage** … compared with **method/argument-based** baselines" |
| H2-3 | `method+args+recv` at T0 | Matched | Confirmatory, F-B | same (ablation) |
| H2-4 | `method-only` at T0 | Matched | Confirmatory, F-B | same (ablation) |
| H2-2 (H2b) | `method+args` at T0 | Matched, ≥ 10-point margin | Exploratory | effect size only |
| RQ3 / H3 | the proposed system's own τ-gated policy vs always-recommend and **random withholding at matched coverage** | Matched (random withholding) | Pre-registered secondary | whether *abstention* reduces harm at comparable coverage. This is not a comparison with baselines. |

## 2. Which comparisons are at natural coverage

| Comparison | Comparator | Coverage handling | Status |
|---|---|---|---|
| F-A | each baseline that ran (≤ 8; protocol Secs. 4 and 5.2): the six runnable external tools, the **simple algorithm-name mapping** and the **method/argument-only mapping** (both computed on pqscan's own candidate sites). The proposed system is `full` at T2. | **Natural coverage**: exact one-sided McNemar on both-ran sites; no matching, no guard (analysis plan Sec. 9) | Confirmatory, family F-A |
| Experiment B, natural | ablation arms on the same sites | Natural coverage, McNemar | Secondary |
| natural δ, H2-S | `full` T2 vs `method+args` T0 | Natural | Secondary |

**Note.** The method/argument baseline appears twice:
- coverage-matched in F-B (H2-1: `full` vs `method+args`, both at T0);
- at natural coverage in F-A (the proposed system at T2 vs the method/argument-only mapping).

**Ambiguity to fix before F1 (owner).**
- The protocol names "a simple algorithm-name mapping" but not which code variant: `B1-algorithm` (RSA → KEM, EC → SIG) or `B1-dual` (dual target for multi-purpose algorithms). Both exist in `pqscan/baselines/simple.py`.
- "≤ 8" fits exactly one algorithm mapping plus one method/argument mapping plus six external tools.
- The run specification should name the variant(s) before F1; this is recorded as D15.

**Consequence of the design.**
- The phrase "at comparable coverage" is tested confirmatorily **only for the method/argument-based baselines** (family F-B).
- The comparison with **algorithm-family** (and external) baselines is confirmatory but **at natural coverage**. A difference there can reflect coverage, because one method recommends more often or abstains more, as well as correctness given a recommendation.

## 3. Two academically defensible presentations

### Option A: decompose the RQ into its two pre-registered tests (recommended)

**Wording.** Keep the RQ verbatim, then state:
> "We operationalise the RQ through two pre-registered confirmatory families. (a) Against method/argument-based analysis, correctness is compared at equal recommendation volume per repository (family F-B, H2a). (b) Against algorithm-family and existing-tool baselines, per-site correctness is compared at each method's natural coverage (family F-A), with coverage reported alongside. Comparable coverage therefore holds by construction in (a) and is reported, not imposed, in (b)."

**Scientific consequences:**
- It maps one-to-one onto the adopted families. No new analysis is needed, and nothing exploratory is promoted.
- Any F-A finding must be worded "at natural coverage". It cannot support "better at comparable coverage than algorithm-family baselines".
- The coverage numbers (n_exec, coverage per method) must be printed with every F-A result (already required, analysis plan Sec. 9).
- A reviewer may say that the RQ's coverage phrase is fully answered only for half the comparators. This is a transparent limitation, not a flaw.

### Option B: scope the coverage clause to the confirmatory method/argument comparison, and present algorithm-family evidence descriptively by coverage

**Wording.** Keep the RQ verbatim, with a footnote:
> "'At comparable coverage' refers to the confirmatory method/argument comparison (H2a). Comparisons with algorithm-family and existing-tool baselines are confirmatory at natural coverage (F-A). In addition, each baseline's (coverage, harmful-rate) point is shown descriptively against the proposed system's pre-registered risk–coverage curve (RQ3)."

**Scientific consequences:**
- It gives readers a visual sense of coverage comparability for the algorithm-family baselines.
- Placing baseline points on pqscan's risk–coverage curve is **not** among the pre-registered analyses (RQ3 compares pqscan's own policies). It must therefore be labelled **exploratory**, cannot support any claim, and must be listed as an addition made after adoption, before F1 at the latest.
- It adds a figure and some complexity. Readers may misread the descriptive overlay as a coverage-matched test.

## 4. Recommendation (the decision is the owner's)

**Option A.**
- It uses only adopted analyses.
- It states exactly which comparisons are coverage-matched.
- It avoids an exploratory overlay that readers could mistake for evidence.

Option B is defensible only if the overlay is fixed and labelled exploratory before F1.

**Effect on the manuscript.** Sec. IX already states the facts in neutral form ("Coverage note"). The final wording waits for this decision.
