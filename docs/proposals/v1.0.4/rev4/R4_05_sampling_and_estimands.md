# R4-05 Study population, analysis sets, reliability, frame audit and context — PROPOSED, NOT ADOPTED (revision 4)

## 1. Primary study population (V14′)

**Definition.** Primary-set eligible sites are call sites that meet both conditions:
1. eligible under annotation guide v1.1: RSA, EC, X25519/X448 or Ed25519/Ed448 public-key operations, or key material, of pyca or PyCryptodome;
2. located in a `.py` file that imports pyca or PyCryptodome (stratum S1), in one of the 13 frozen repositories at their pinned commits, inside the candidate frame (regex ∪ baseline findings ∪ pqscan Module A), sampled by the seeded sequential sampler.

**What lies outside the primary population, and why it matters:**

| Excluded set | Can it contain real cryptographic usage? | Risk if ignored | How it is reported |
|---|---|---|---|
| **Eligible S2 sites** (files importing no supported library; B0, 10 per repository) | **yes**: for example a key object received from another module, or a wrapper module | tool performance outside the primary scope stays hidden; the frame looks narrower than real usage | separate table: S2 eligibility rate; each tool's judgments on eligible S2 sites; an "eligible S2 rate × S2 pool size" indication of how much in-scope usage lies outside S1 (descriptive, with the S2 pool size per repository) |
| **Ineligible S2 and S1 candidates** reported by a tool | no (by definition) | **false positives hidden** | per tool: the number of findings on adjudicated-ineligible candidates (S1 and S2), by category (hash or symmetric, parameter object, unrelated method, out-of-scope library) and per repository; the denominator is that tool's findings that map to annotated candidates |
| **Annotator-added sites** (eligible, in no candidate source) | yes | the frame looks more complete than it is | count per repository and role; listed as "missed by every candidate source (regex, all tools, pqscan)" |
| **Baseline findings that fall on no sampled candidate** | unknown (not annotated) | — | count per tool, labelled "not assessed (not sampled)" |

**Rule.** Primary metrics describe the primary population only. Every report states: "Results are limited to RSA/EC/Ed/X public-key call sites in files importing pyca or PyCryptodome within the candidate frame of the 13 frozen repositories."

## 2. Denominators

| Analysis | Denominator |
|---|---|
| Primary H1–H3 metrics, H2, F-A | primary-set eligible test sites (per repository and pooled) |
| Sensitivity "all eligible" | primary ∪ eligible S2 ∪ annotator-added |
| Tool false-positive profile | each tool's findings on annotated candidates |
| Execution failures | primary-set eligible sites in files the tool attempted |
| Frame audit | audited eligible sites (Sec. 4) |

## 3. Reliability samples (V3′)

| Item | Phase DV (development + validation) | Phase T (test) |
|---|---|---|
| Population N | every issued candidate with a final label in the phase (B0 and B1+), excluding annotator-added | the same, for the test split |
| Size | n = max(50, ⌈0.10·N⌉) | n = max(50, ⌈0.10·N⌉) |
| Seed | `20261113:intra:DV` | `20261113:intra:T` |
| Selection | proportional to N_r per repository, at least 3 per repository; within a repository half owner-final eligible and half ineligible (or all available) | the same |
| Gap | ≥ 14 days after the latest primary label in the sample (enforced by script) | the same; done before F2 |
| Blinding | earlier labels hidden; new seeded presentation order | the same |
| Reporting | per field (8 fields): n, raw agreement, Cohen's κ with a bootstrap 95% CI (items resampled within repositories, 2,000 resamples), the full confusion table, per-class specific agreement for classes with ≥ 5 items, and class prevalence | the same |
| Rule | κ(gt_role) point estimate < 0.60 → revise the guide and re-label Phase DV before F1 | κ(gt_role) < 0.60 → all test results labelled exploratory |

**Owner–AI agreement:** every candidate in the phase with both labels; "insufficient context" items excluded and counted.

**AI repeat-run:** n = max(30, ⌈0.10·N_AI⌉) per phase, seed `20261113:airepeat:<phase>`.

None of these is called inter-annotator reliability. Limitations of κ: prevalence and marginal effects, and rare classes contributing almost nothing (`R3_03` Sec. 3).

## 4. Frame audit (V7′) — descriptive

- **Frame:** crypto-importing `.py` files of the 6 development and validation repositories (SHA-256 of the list recorded).
- **Selection:** a seeded order per repository, taken round-robin across repositories until ≥ 60 eligible sites have been audited and every repository has contributed ≥ 1 file. Zero-site files count.
- **Procedure:** the owner reads each whole file blind to the pool, records every eligible site with evidence, and a script checks pool membership at statement level.

**Can estimate:** the share of eligible sites in such files that the pool misses, for development/validation repositories, with a file-level cluster bootstrap interval (resampling files within repositories) and per-file counts.

**Cannot estimate:**
- recall in files importing no supported library;
- recall in the test split;
- recall across Python projects generally;
- errors the owner and the pool share.

A Wilson interval appears only with the caveat "assumes independent sites". With few files, the interval is wide and is described as such.

## 5. Context recording (V16′)

**Recorded before the AI review.** `meta.context_used` is part of the owner's primary file, which is hashed and pushed before the AI review is requested (ledger step order). It therefore cannot depend on whether the owner and AI agree.

**Permitted values:**
- `packet_sufficient`: every one of the 8 labelled fields was decided using only lines inside the candidate's packet, as generated by the packet builder.
- `extended`: some field needed context outside the packet. `meta.context_extra` lists every additional file:line range consulted.

No other values. The criterion is what the owner actually consulted, not what the owner thinks the AI would need.

**Identical-packet-first design (evaluated).**
- **Full version:** the owner first labels from the identical packet (P-label), then may extend context and record the final primary label (F-label). The P-label against the AI is the clean comparison.
- **Cost:** about 0.5–1.5 extra minutes per candidate (assumed), or about 9–28 h for about 1,100 candidates.
- **Recommendation:** packet-first **only on a seeded 10% subset per phase** (seed `20261113:packet:<phase>`, at least 50). That measures how context affects owner labels and owner–AI agreement, for about 1–3 h of extra work. All other candidates use the single primary label with `context_used`.
