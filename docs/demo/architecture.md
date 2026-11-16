# pqscan architecture (one page)

Derived from the code at tag `phase2-complete` (`pqscan/` package, version `0.1.0.dev0`). File references
are to that package. Nothing below describes Phase 3 work.

```
 repository (directory)
   │  safe walk: root-confined, no symlinks/junctions, skips .git/.venv/build/…, size limit,
   │  each file analysed in a spawned worker process with a per-file time limit   (pipeline.py)
   │
   ├──► Module A  Semgrep CE 1.185.0, 28 bundled rules           (detect/runner.py, detect/rules/*.yaml)
   │      pyca.yaml (14), pycryptodome.yaml (12), common.yaml (2)        │
   │      explicit file list, --metrics=off, never the directory        │ joined to Module B sites
   │                                                                     │ by (file, line)
   └──► Module B  Python `ast` semantic evidence                  (semantic/*.py)
          imports → receiver typing → algorithm arguments → key provenance
          → bounded consumer tracing → PQ/T hybrid evidence  ==> SiteEvidence per site
                          │
                          ▼
        Module C  role decision table + evidence tier T0–T3      (roles/classifier.py)
          role ∈ {SIGN, VERIFY, KEY_ESTABLISHMENT, PK_ENCRYPT, PK_DECRYPT, KEY_MATERIAL_ONLY, UNKNOWN}
          ablation arms: method-only | method+args | method+args+recv | full (default)
                          │
                          ▼
        Module D  policy v1.1 as YAML + engine                   (policy/policy_v1_1.yaml, policy/engine.py)
          RECOMMEND {SIG → ML-DSA | KEM → ML-KEM | KEM_DEM → ML-KEM + KDF + AEAD}
          FLAG_NO_TARGET {INVENTORY | NO_ACTION_HYBRID}
          ABSTAIN  (role UNKNOWN, or tier below the threshold τ, default T2)
                          │
                          ▼
        Module E  exporters                                      (export/cbom.py, sarif.py, jsonout.py)
          CycloneDX 1.6 CBOM (schema-validated before writing) | SARIF 2.1.0 | full JSON | text summary
```

## Detection (Modules A and B)

- **Module A — Semgrep.** `detect/runner.py` runs Semgrep with the bundled rules on an explicit,
  root-confined list of `.py` files (never on the directory, because Semgrep would otherwise follow Windows
  junctions and apply its own ignore list). Flags: `--json --quiet --metrics=off --no-git-ignore
  --max-target-bytes 2000000 --timeout 30 --disable-version-check`. Each match becomes a `Candidate`
  (rule id, library, kind, algorithm, API). Snippets are truncated and PEM-like lines are redacted.
- **Module B — AST evidence.** `semantic/evidence.py` discovers the same kinds of sites *independently* from
  the AST (operation calls `.sign/.verify/.exchange/.encrypt/.decrypt`, key generation, key loading, key
  construction, PyCryptodome signer/cipher objects) for PyCA `cryptography` and PyCryptodome. For each
  site it records:
  - **receiver typing** (`typer.py`, `model.py`): is the receiver a key object, of which algorithm,
    private or public, and where did it come from (generated, loaded from PEM/DER/SSH/JWK/certificate,
    constructed, parameter, attribute);
  - **algorithm-specific arguments** (`args.py`): e.g. `PSS`, `OAEP`, `PKCS1v15`, `ec.ECDSA(...)`, `ec.ECDH()`;
  - **consumers** (`consumers.py`): bounded, flow-insensitive tracing of where a key goes (two call levels
    when leaving a class; public functions and properties count as an *escape*);
  - **hybrid evidence** (`hybrid.py`): whether a classical secret/signature is combined with ML-KEM/ML-DSA
    output in the same block.
- The pipeline (`pipeline.py`) joins Semgrep candidates to Module B sites by `(file, line)`. Semgrep matches
  with no semantic site are listed separately as `semgrep_only`. Imports of out-of-scope libraries
  (python-rsa, python-ecdsa, pyOpenSSL, `ssl`, paramiko, …) are listed as `unsupported`, never guessed at.

## Role classification and evidence tiers (Module C)

`roles/classifier.py` is a deterministic decision table.

- **Operation sites** take their role from the method (`sign`→SIGN, `verify`→VERIFY, `exchange`→
  KEY_ESTABLISHMENT, `encrypt`→PK_ENCRYPT, `decrypt`→PK_DECRYPT). The **tier** measures how sure we are
  that this is really a public-key operation:
  - **T0** receiver unresolved and no algorithm-specific argument;
  - **T1** only one of {receiver is a key object, algorithm-specific argument / single-purpose algorithm};
  - **T2** both;
  - **T3** T2 and the receiver's origin resolves to a concrete provenance (generated / loaded / constructed /
    certificate) with no conflict. Any conflict caps the tier at T1; a key that may also come from a
    parameter or reaches another role family is capped at T2.
- **Key-material sites** (generate/load/construct) take their role from the type-valid consumers found:
  one family and no escape → that family's role at T3; one family with an escape → T2; **two or more
  families → UNKNOWN** (possible roles listed); no consumer and no escape → **KEY_MATERIAL_ONLY**;
  single-purpose algorithms (X25519/X448/DH → key establishment, Ed25519/Ed448/DSA → signing) decide when
  consumers are out of scope.
- Tiers are **ordinal evidence labels, not probabilities**.
- **Ablation arms** restrict which evidence is used (`--arm`), so the contribution of each evidence type
  can be measured later.

## Policy engine and abstention (Module D)

`policy/policy_v1_1.yaml` (frozen 2026-11-12) maps roles to target classes; `policy/engine.py` applies it.

| Role | Class | Action | Target |
|---|---|---|---|
| SIGN, VERIFY | SIG | RECOMMEND | ML-DSA (FIPS 204), default ML-DSA-65 |
| KEY_ESTABLISHMENT | KEM | RECOMMEND | ML-KEM key-establishment redesign (FIPS 203, SP 800-227), ML-KEM-768 |
| PK_ENCRYPT, PK_DECRYPT | KEM_DEM | RECOMMEND | KEM + KDF + AEAD redesign — explicitly *not* a drop-in |
| KEY_MATERIAL_ONLY | INVENTORY | FLAG_NO_TARGET | inventory only; determine downstream role |
| UNKNOWN | ABSTAIN | ABSTAIN | no recommendation; reason and possible roles stated |

- **Abstention:** a site ABSTAINs if its role is UNKNOWN, or if its tier is below the threshold τ
  (default **T2**, override with `--tier-threshold T0|T1|T2|T3`). The abstention text names the missing
  evidence and the inferred role that was *not* acted on.
- **Load-time invariants:** the engine refuses a policy file in which SIGN/VERIFY map to anything but the
  SIG family, KEY_ESTABLISHMENT/PK_ENCRYPT/PK_DECRYPT to anything but the KEM family, or UNKNOWN to
  anything but ABSTAIN. This is what keeps ML-KEM and ML-DSA from being swapped.
- **Hybrids:** the classical half of an approved PQ/T hybrid (combined with ML-KEM or ML-DSA) is
  FLAG_NO_TARGET / NO_ACTION_HYBRID. (Not exercised by the demo fixture.)

## Exporters (Module E)

- **CycloneDX 1.6 CBOM** (`export/cbom.py`): one `cryptographic-asset` component per role-bearing site;
  role, tier, action, recommendation and evidence as `pqscan:*` properties; operation components depend on
  the key-material components their receiver was traced to. Validated against the bundled official schema
  before it is written (exit code 3 if invalid). No timestamp by default → byte-identical across runs.
- **SARIF 2.1.0** (`export/sarif.py`): one result per site; RECOMMEND = `warning`, ABSTAIN and
  FLAG_NO_TARGET = `note`.
- **JSON** (`export/jsonout.py`): the full evidence, decision and recommendation per site, plus excluded
  sites, Semgrep-only candidates, unsupported imports, execution failures and skipped files.
- **Summary** (`cli.py`): one line per site — `file:line  algorithm  role  tier  action  target-class`.

## Safety properties

Scanned code is parsed, never imported or executed. Outputs contain identifiers but no key bytes, no
source string literals and no source snippets (the CBOM/SARIF/JSON exporters). Unparsable or timed-out
files are recorded as execution failures, never as abstentions.
