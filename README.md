# Post-quantum crypto scanner for Python projects

Research prototype (`pqscan`) that scans a Python repository **without executing it**, finds RSA/ECC
usage in PyCA `cryptography` and PyCryptodome, infers the cryptographic role of each call site from
bounded evidence (receiver type, arguments, key provenance, consumers), maps the role to an ML-DSA /
ML-KEM migration direction or abstains, and exports a CycloneDX 1.6 CBOM, SARIF 2.1.0 or JSON.

Mandatory base paper: Lei Zhang, "Toward Quantum-Safe Software Engineering: A Vision for Post-Quantum
Cryptography Migration", ICSE-Companion '26, pp. 402–403, DOI 10.1145/3774748.3795653. This project
implements part of its Pillar P1 (PQC-aware detection with protocol roles and an enriched inventory). It
does not implement AQuA P2 (refactoring) or P3 (verification).

> Migration guidance only. pqscan does not establish that a migrated system is secure, compliant or
> quantum-safe. Semgrep detection, CBOM generation and abstention are requirements and mechanisms, not
> novelty claims; see `docs/research/02_final_decision_summary.md`.

## Status

Phase 1 (research specification and pilot): conditional pass. Phase 2 (system implementation): gate passed on
14 Nov 2026 (`docs/reports/Phase_2_System_Implementation_Report.md`, tag `phase2-complete`). Phase 3
(benchmark annotation and held-out evaluation) has not started, and no experimental results exist yet.
Numbers in `docs/dev/` and `docs/pilot/` are development checks on development repositories, not results.

Licence: none chosen yet (the default is all rights reserved). Bundled third-party files keep their own
licences: the CycloneDX 1.6 schema (Apache-2.0) and the OASIS SARIF 2.1.0 schema.

## Install (Windows or Linux, Python ≥ 3.12)

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -e ".[bench,dev]"
```

On Linux use `.venv/bin/python`. Semgrep 1.185.0 is pinned and installed as a dependency.

## Use

```bash
.venv/Scripts/pqscan scan path/to/repo --format summary
.venv/Scripts/pqscan scan path/to/repo --format cbom -o bom.json
.venv/Scripts/pqscan scan path/to/repo --format sarif -o pqscan.sarif
.venv/Scripts/pqscan scan path/to/repo --format json --tier-threshold T3 --arm method+args
```

Options: `--exclude-tests`, `--no-semgrep`, `--policy <yaml>`, `--max-file-bytes`, `--file-timeout`,
`--timestamp` (the CBOM omits timestamps by default so output is byte-identical across runs).
Exit codes: 0 completed, 2 input error, 3 internal failure (including a CBOM that fails schema validation).

## What each output means

Every role-bearing site gets one of three actions:

| Action | Meaning |
|---|---|
| RECOMMEND | `SIG` (ML-DSA, FIPS 204), `KEM` (ML-KEM key-establishment redesign, SP 800-227) or `KEM_DEM` (KEM + KDF + AEAD redesign of RSA encryption; never a drop-in) |
| FLAG_NO_TARGET | inventory only (key material with no consumer) or the classical half of an approved PQ/T hybrid (ML-KEM next to key establishment, ML-DSA next to signatures) |
| ABSTAIN | the role is UNKNOWN, or the evidence tier is below the policy threshold (T2 by default); the reason is stated |

Evidence tiers T0–T3 are ordinal labels defined in `docs/specification/data_dictionary.md`, not probabilities.

## Safety properties

Scanned code is parsed with `ast` and Semgrep only; it is never imported or executed. The walk does not
follow symlinks or junctions, and Semgrep receives the same explicit, root-confined file list (results
resolving outside the root are dropped). Files above a size limit and excluded directories are skipped
and listed. Each file is analysed in a worker process with its own time limit; a file that exceeds it has
its worker killed and is recorded as an execution failure, as are unparsable files (never as abstentions).
Outputs carry identifiers (function, class, variable and attribute names, used in evidence trails) but no key
bytes, no source snippets and no source string literals.

## Known limits

- Protocol configuration (TLS/SSH contexts, KEX lists) is out of scope: the `PROTOCOL_CONFIG` role exists in
  the taxonomy for labelling, but pqscan never emits it. Imports of `ssl`, `paramiko`, `asyncssh` and other
  out-of-scope crypto libraries are reported in the `unsupported` list instead.
- Analysis is flow-insensitive and bounded (two call levels when leaving a class). A name reused for a
  different key or object is reported as a conflict, which lowers the evidence tier and leads to abstention.
- DH key agreement, DH parameter key generation and PKCS#12 loading are detected by Semgrep but not analysed.
- Analysis is flow-insensitive apart from if/else and try/except alternatives.
- A classical operation counts as part of an approved PQ/T hybrid only when its secret (or signature) is
  combined with a matching ML-KEM (key establishment) or ML-DSA (signature) result by an accepted combiner
  in the same block of one function, with no path that uses the classical value on its own. The check is
  deliberately conservative and may miss genuine hybrids, for example a combination spread across modules;
  a miss gives a migration note, never false assurance. It shows data combination, not that the combiner
  meets SP 800-227 Sec. 4.6.

## Layout

| Path | Contents |
|---|---|
| `pqscan/detect` | Module A — Semgrep rules (28) and runner |
| `pqscan/semantic` | Module B — imports, typing, arguments, consumer tracing, evidence |
| `pqscan/roles` | Module C — role decision table and ablation arms |
| `pqscan/policy` | Module D — policy v1.1 (YAML) and engine |
| `pqscan/export` | Module E — CycloneDX 1.6, SARIF, JSON |
| `pqscan/bench`, `pqscan/baselines` | Modules F and G — judging, statistics, tool adapters, simple baselines |
| `docs/specification` | frozen taxonomy, policy, protocol, data dictionary |
| `benchmark/` | frozen repository manifest and pinned baseline manifest |
| `scripts/fetch_pinned.py` | re-creates repositories and baselines from pinned commits |

## Tests

```bash
.venv/Scripts/python -m pytest
```

## Reproducing external inputs

```bash
.venv/Scripts/python scripts/fetch_pinned.py repos .cache/repos
.venv/Scripts/python scripts/fetch_pinned.py baselines .cache/baselines
```

Test-split repositories are only fetched with `--include-test`, after the Phase 3 freeze.
