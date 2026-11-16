# R4-04 Seven-repository inference — PROPOSED, NOT ADOPTED (revision 4)

## 1. How the test repositories were chosen

Source: `docs/benchmark/repository_split.md` Sec. 2; `docs/benchmark/candidate_verification.md`; `qualification_round3.md`.

- **Candidates:** named by the research team, and in round 3 found through GitHub code search, then filtered by mechanical criteria: ≥ 100 stars, OSI licence, not archived, ≥ 10 regex candidates, not in a baseline corpus. Round 3 selected by a pre-stated rule (most PyCryptodome public-key imports).
- **Not done:** no random sampling of repositories at any stage.
- **Conclusion:** the 7 test repositories are a **purposive** sample.

## 2. Two different claims

| Claim | Supported by | Status |
|---|---|---|
| **A. About the 7 selected repositories** (their primary-set eligible sites at the frozen commits) | random, seeded within-repository site sampling: a design basis for inference | **confirmatory** (R4-02: stratified re-matching bootstrap; site-level tests secondary) |
| **B. About Python projects in general** | no random repository sampling; only a model assumption that the 7 behave like draws from a population | **exploratory and descriptive only** |

## 3. Options evaluated for claim B

| Method | Assumption | Simulated behaviour with 7 repositories (`results/h2_type1.csv`, `h2_power.csv`) | Use |
|---|---|---|---|
| Repository-level one-sided t (df = 6) on δ_r | δ_r independent and roughly normal around a superpopulation mean | Type I ≤ 0.0295 when effects are redrawn (normal or skewed, τ ≤ 0.15). Power for δ > 0 at a true 15 pp: 0.59–0.99 at α = .025 | exploratory, labelled "model-based; repositories not randomly sampled" |
| Exact sign-flip | δ_r − d0 symmetric about 0 | Type I ≤ 0.019. Smallest possible p = 1/128 = 0.0078, so it **cannot** reject at the worst Holm step α/4 (0.00625). At α/3 it can only if all 7 point the same way | descriptive robustness |
| Exact Wilcoxon signed-rank | symmetric differences | same smallest p; Type I ≤ 0.019 | descriptive robustness |
| Repository cluster bootstrap | many clusters | not reliable with 7 clusters (few-cluster under-coverage); not simulated here | descriptive only, never for inference |
| Leave-one-repository-out | — | 7 re-estimates of δ; shows dependence on any single repository | **required** description |
| GEE or mixed models | asymptotic in the number of clusters | unreliable at K = 7 | not used |

**Strong heterogeneity.** Under the skewed shape (one outlier repository) and τ = 0.15, the repository-level t test stayed at or below 0.0295. But a single extreme repository can dominate both the mean and the standard deviation. That is why the t test is exploratory and leave-one-out is mandatory.

## 4. Required reporting

1. A table of all **seven** δ_r values: per-repository n, b_r, c_r, matched coverage, natural coverage, and a per-repository exact 95% interval for the paired difference.
2. A forest-style plot of the seven δ_r values, with the pooled estimate.
3. Leave-one-repository-out estimates (seven values).
4. The sign pattern (how many repositories favour the full arm).
5. The repository-level t-test p-value and the sign-flip p-value, both labelled exploratory.
6. The sentence: "The test repositories were selected purposively. Confirmatory conclusions apply to these seven repositories at the frozen commits; generalisation to other Python projects is not established."

## 5. Recommendation

- **Confirmatory:** claim A only, and only for the direction (B1, B3, B4 under Holm).
- **Exploratory:** the 10 pp margin (claim A) and every claim B.
- 7 clusters cannot support confirmatory generalisation, and the design does not pretend otherwise.
