# R4-12 Execution-failure handling for H2 and paired comparisons — PROPOSED, NOT ADOPTED

**Frozen rules this specification keeps unchanged** (`scoring_policy.md` v1.0 Sec. 2 and 5; `data_dictionary.md` Sec. 2; protocol v1.0.3 Sec. 5):
- EXECUTION_FAILURE is its own judgment, recorded per file, and never counted as MISSED.
- Every rate uses n_exec, the eligible sites where the method ran.
- Paired comparisons use only sites where both methods ran.
- When a comparison involves different site sets, the paired test is not applied to the excluded sites, and the reason is stated.

Nothing below changes a judgment. It adds definitions, mandatory reporting and two sensitivity analyses. Reference implementation: `matching_ref_v4.execution_partition` and `evaluate_repository`; tests in `scripts/test_v12pp.py`.

## 1. How failures arise for the H2 arms (code evidence)

`pqscan/bench/run.py`, `judge_ours`, parses each file once (`analyze_source`) and caches the result. Every Module C arm (full, method+args, method+args+recv, method-only, and the T2 system) is then derived from that **same** parsed evidence by `decide(hit, arm)`. A pqscan EXECUTION_FAILURE arises only at file level:
- the file cannot be read (`OSError`): "file could not be read";
- the file does not parse (`site_kind == "parse-error"`): "file could not be parsed".

**Consequence.** For H2-1, H2-3, H2-4 and H2-S, a site fails either for **both** arms or for **neither**. "Only one arm succeeds" cannot happen in the current harness.

**Requirement for the production implementation (new):**
- evidence is computed once per file and shared by all Module C arms;
- the H2 harness **asserts** that the failure sets of the two arms of every H2 comparison are identical;
- a discordant failure is treated as a software defect: the run stops and the defect is reported. It is not silently handled.

The scanning CLI's isolated worker (`pqscan/pipeline.py`: time limit, `RecursionError`, other exceptions) is also file-level. If it is used for the H2 run, the same assertion applies.

## 2. Can excluding failed sites bias the comparison?

| Question | Answer for H2 (Module C arms) | Answer for F-A (external tools) |
|---|---|---|
| Bias **between the two arms** | **None from the exclusion.** Failure does not depend on the arm, so both arms are compared on exactly the same sites, and the matched comparison on that set is unaffected. | **Possible and serious.** A tool that crashes on hard files is scored only on easier ones. The frozen rule applies (paired comparison on both-ran sites; reason stated), and the sensitivity analyses in Sec. 4 are mandatory. |
| Bias **of what is estimated** (population shift) | **Yes.** The estimand becomes "eligible sites in files the analyser can parse". Parse failures are not random: Python-2-only syntax, syntax newer than the analysis interpreter, generated or very deeply nested code (RecursionError), and encoding damage. Such files may hold more legacy cryptographic code (older PyCryptodome or PyCrypto idioms). | Yes, per tool, and differently for each tool. |
| Can failures change k_r? | No. A failed site has no RECOMMEND under either arm, so it is excluded before matching and does not alter the counts. Only the denominator n_r changes. | Not applicable (no matching in F-A). |

## 3. Definitions (per repository r and per comparison)

| Symbol | Definition | Used for |
|---|---|---|
| E_r | primary-set eligible sites of r (R4-05 Sec. 1), with owner-final labels | **the reporting base: every site in E_r appears in some table** |
| F_A,r | sites in E_r where arm A has EXECUTION_FAILURE | per-arm failure reporting |
| C_r = E_r \ (F_F,r ∪ F_M,r) | **common evaluable set**: both arms ran | **primary denominator for H2 (n_r = \|C_r\|) and for every paired comparison** |
| O^F_r = F_M,r \ F_F,r | only the full arm ran | sensitivity S-F1 and S-F2; must be empty for H2 |
| O^M_r = F_F,r \ F_M,r | only the comparator ran | sensitivity S-F1 and S-F2; must be empty for H2 |
| N_r = F_F,r ∩ F_M,r | neither ran | reported; S-F1 |
| n_exec,A,r = \|E_r\| − \|F_A,r\| | frozen per-arm rate denominator | unpaired per-arm tables (scoring policy Sec. 5) |

**Edge cases:**
- **A repository with C_r = ∅** cannot yield δ_r. It stays listed in every table with its failure counts and a note. It counts as not matching-feasible (k_r = 0) in the gate. The repository-balanced estimate is then the mean over repositories with n_r ≥ 1, and that fact is printed next to the estimate.
- **Never silently removed:** the confirmatory estimand still names the 7 repositories.

## 4. Primary analysis and failure sensitivity analyses

| Analysis | Denominator | Failed sites | Status |
|---|---|---|---|
| **Primary H2** (matching, δ, bootstrap, Holm) | C_r | excluded, listed | confirmatory |
| Per-arm rates (coverage, correctness, harmful…) | n_exec,A,r | excluded (frozen rule) | primary descriptive |
| **S-F1** "failures are not correct" | \|E_r\| | each failed (site, arm) scored **not correct**. Sites where only one arm ran are scored for the arm that ran, at natural output. | pre-registered sensitivity |
| **S-F2** extreme bounds | \|E_r\| | lower: every site where F failed counted as correct for M only; upper: every site where M failed counted as correct for F only | pre-registered, descriptive |

Formulas, per repository; δ̃_r is the primary tie-averaged estimate on C_r:

δ_S-F1,r = [n_r·δ̃_r + Σ_{O^F_r} X_i − Σ_{O^M_r} Y_i] / |E_r|

S-F2 = [n_r·δ̃_r + Σ_{O^F} X − Σ_{O^M} Y − |F_F,r|] / |E_r| to [… + |F_M,r|] / |E_r|

**For H2 with concordant failures**, S-F1 is a pure rescaling: δ_S-F1,r = δ̃_r · n_r / |E_r|. It can shrink the effect but never change its sign.

**How the two coexist.**
- The confirmatory test is always computed on C_r. Failures cannot change it, because they are excluded from both arms by the frozen paired-comparison rule.
- S-F1 and S-F2 are always reported next to it, per repository and pooled, using the same weighting as the primary.

**Pre-registered triggers** (they fix wording, never the test):

| Trigger | Consequence |
|---|---|
| pooled \|F_F ∪ F_M\| / \|E\| > 5%, or > 10% in any repository | The limitations paragraph and the H2 sentence say "on sites in files the analyser could parse (x% of eligible sites failed)". S-F1 is shown in the main H2 table, not only in the supplement. |
| any discordant failure in an H2 comparison | the run stops (Sec. 1); nothing is reported until the defect is fixed and the run repeated before F2 |

## 5. Mandatory failure reporting (never omitted)

Per repository, per arm (and per external tool in F-A):
- |E_r|, |F_A,r| and the failure rate;
- the counts of both / F only / M only / neither;
- failure reasons (unreadable, parse error, time limit, recursion, other) with the file count and site count each;
- failures by library (pyca / PyCryptodome) and by scope (app / test / vendored / example) where known.

Pooled: the same with totals. A list of failed files with commit-relative paths is published with the artefact.

**Labels.** Failed sites keep their owner-final labels. Their label distribution (role, assessability) is reported against C_r, so that a reader can see whether failures concentrate on particular constructs.
