# Final decision summary — Post-quantum crypto scanner for Python projects

Date: 12 November 2026. Full reasoning and evidence: `02_hostile_novelty_audit.md`; raw inspection notes: `02_audit_evidence_log.md`; first review: `01_research_feasibility_report.md`.

## Decision: B — CONDITIONAL GO

The current direction is defensible only after re-centring. The paper is the **measurement**, the analyzer is the **vehicle**.

## What did not survive (remove from novelty claims)
- Semgrep detection: lecturer requirement and floor baseline, not a contribution.
- CycloneDX CBOM generation: requirement; schema already carries role slots (`cryptoFunctions`); six tools emit CBOMs.
- Alias/wrapper/interprocedural resolution as techniques: established (Cryptolation, CryptoPyt, Cryptbara, CodeQL); keep as mechanism, claim only the measured effect.
- Numeric confidence scoring: no calibration basis; replace with ordinal evidence tiers T0–T3.
- Abstention as a contribution: established method; keep as evaluation discipline with risk–coverage reporting.
- LLM in the core pipeline: unnecessary; baseline arm only.

## What survives (source-verified, 12 Nov 2026)
1. **No inspected Python-capable tool infers a call site's cryptographic role from evidence.** pqcheck maps every RSA finding to ML-KEM-768 and `ec.generate_private_key` to the signature family; pqc-audit hard-codes a `Usage` per pattern and emits "ML-KEM / ML-DSA" for RSA and EC; PostQuant assigns role by library; CBOMkit captures sign/decrypt/exchange only for keys generated in place and has no verify/encrypt rules; CodeQL Python models expose no operation kind and no key loaders; Mehl's ESEM 2026 scanner labels vulnerable/safe/PQC-ready and prescribes nothing.
2. **No inspected paper or tool measures recommendation correctness.** All metrics are detection-level or repository-level.
3. **No inspected tool abstains.**

## Approved contribution set
- **N1 (primary):** PyPQC-RoleBench, a role-labelled benchmark (synthetic × transformation operators × key-provenance kinds, plus ≥ 300 frozen, double-annotated real call sites), and the first measurement of correct / harmful / undecided / abstained / missed PQC recommendations across seven pinned baselines (Semgrep floor, pqcheck 0.1.0, pqc-audit 0.4.1, PostQuant 0.7.0, pqc-posture 0.4.0, Quantum-Safe Auditor regex stage, CBOMkit 1.7.0, Mehl's Zenodo scanner).
- **N2 (primary):** bounded key-provenance-aware role inference with evidence-gated abstention, shown to reduce harmful recommendations at stated coverage, with ablations.
- **N3 (supporting):** role-invariance robustness study under semantics-preserving transformations.
- Optional: LLM adjudicator baseline (N4); CBOM link-correctness (N5); one validated RSA-PSS → ML-DSA pattern (base-paper P3).

## Revised problem statement
Existing Python PQC scanners attach ML-KEM or ML-DSA targets to RSA/ECC findings by algorithm name or hard-coded pattern usage, so recommendations can be role-incorrect or undecided, and no study has measured how often. We measure how often call-site role is undeterminable from the call alone, how often current tools consequently issue harmful or undecided targets, and whether provenance-aware role inference with evidence-gated abstention reduces harm at acceptable coverage. This instantiates Pillar P1 ("protocol roles", "enriched CBOM") of the fixed base paper; P2 and P3 are out of scope except the optional validation pattern.

## Conditions
1. Run the 30-site H1 pilot (two repositories, manual role labelling, record evidence needed) before building Module C. Kill criterion: if under ~10% of sites are undeterminable from names and existing tools' harmful + undecided rate is under ~10%, redesign around robustness or abandon the recommendation framing.
2. Freeze the role taxonomy, the role → target-class table (FIPS 203/204, SP 800-227) and the labelling guide before experiments; publish them.
3. Freeze held-out repositories and commit hashes before writing rules; no fixes from held-out misses.
4. At least one annotator outside the build team; report κ; adjudicate disagreements.
5. Pin all baselines by commit; publish output adapters; count dual targets as undecided, not harmful.
6. Report every error figure with its coverage; publish risk–coverage curves; McNemar for paired comparisons; CIs throughout.
7. State plainly that Semgrep, CBOM and abstention are not claimed as novel.

## Feasibility (undergraduate team)
Moderate. Essential: Semgrep CE rules, `ast`/`symtable` semantic layer with bounded def-use and one-level call resolution, deterministic role table, CycloneDX export, baseline containers, benchmark generator, annotation. Optional: PyCG, LLM arm. Two libraries (pyca/cryptography, PyCryptodome) and RSA/EC (+ DH/X25519 keygen) are sufficient. Sixteen-week plan in the audit.

## Publication path
Workshop or short paper on N1 alone; full paper (ESEM/EASE registered report, SANER/ICPC/MSR tool or data track, IEEE QCE software track, ARES) with N1 + N2 + N3 and ≥ 300 real sites.

## Open items
See audit Section 14: Yuan et al. (ASE 2026) and Cryptbara read from abstracts only; HyBind PDF blocked; Mehl's scanner not yet run; commercial tools unverifiable; NIST IR 8547 tables not read directly; rotate the Consensus API key that was pasted into chat.
