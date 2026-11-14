# Synthetic benchmark, Dataset A (checklist B3)

Generator: `pqscan/bench/synth.py` (version 1.0). Tests: `tests/test_synth.py` (13 tests; module coverage 99%). Dataset: `benchmark/synthetic/`. Built 14 Nov 2026 on branch `phase3-preparation`.

```bash
.venv/Scripts/python -m pqscan.bench.synth --out benchmark/synthetic --seed 20261113
```

## Contents

| Item | Value |
|---|---|
| Base cases | 61: 26 key-site, 22 operation-site and 13 negative idioms; pyca (RSA, EC, X25519, X448, Ed25519, Ed448) and PyCryptodome (RSA, ECC) |
| Instances | 388: each positive base case × 6 invariance operators + `loaded-key`; each negative × `identity`, `alias-import`, `wrapper-function`, `class-method` |
| Ground-truth roles | SIGN 140, NONE 52, KEY_MATERIAL_ONLY 42, KEY_ESTABLISHMENT 42, VERIFY 35, PK_DECRYPT 28, PK_ENCRYPT 28, UNKNOWN 21 |
| Split | by base case, stratified by kind: 31 `synthetic-dev`, 30 `synthetic-holdout` (`manifest.json` → `split`) |
| Validation subset | 78 instances (20%, stratified by operator), blind (`validation_subset.csv`: locations only) |
| Provenance | `manifest.json`: generator version and source SHA-256, seed, and per-instance base case, operator, split and file SHA-256; each record's `commit` is `generator-<first 12 hex of the generator hash>` |

## Ground truth by construction

Labels follow `role_taxonomy.md` v1.0.1:
- **Key sites** inherit the role of their consumers (rule 1). Sign plus verify gives SIGN with secondary VERIFY.
- **Consumers of two families selected by the runtime `alg` parameter** give UNKNOWN / INDETERMINATE, with `possible_roles` (rule 2).
- **Export-only keys** are KEY_MATERIAL_ONLY (rule 3).
- **Operation sites** take their role from the method (rule 4).
- **Negatives** are NONE and ineligible (rule 8). They are:
  - padding or signature-algorithm objects;
  - `isinstance` checks;
  - AEAD and Fernet encryption;
  - an unrelated `.sign` method;
  - a crypto-like local function name;
  - string and comment mentions;
  - python-ecdsa (out of scope);
  - PyCryptodome AES and hashing.

The six operators keep role, assessability, possible and secondary roles, eligibility and the hybrid flag. A test checks this for every base case.

`loaded-key` replaces generation with `load_pem_private_key` / `import_key`. It changes provenance to `loaded-PEM`, and for X25519/X448/Ed25519/Ed448 it changes the algorithm to `other`, because a PEM loader does not reveal which curve it is. The role stays fixed by the consumers. As the protocol requires, `loaded-key` is reported apart from the invariance operators.

The names of variables, attributes, classes and helpers vary with the seed. A test shows that changing the seed changes the code but not the labels. Negatives use neutral helper names, so no name suggests a key.

## Rules for use (no leakage)

- The dataset is only parsed. Generated code is never imported or executed, and the tests check this by parsing alone.
- `synthetic-holdout` base cases must not be scanned by pqscan, or looked at to tune it, before the pre-test freeze F1. `synthetic-dev` cases may be used during development.
- All statistics on Dataset A cluster on `base_case` (cluster bootstrap; invariance per base case).
- The external annotator labels `validation_subset.csv` blind, using the annotation guide. Disagreements with the generated labels go through the adjudication procedure in `docs/review/README.md`. A confirmed label error is fixed in the generator, and the dataset is regenerated before F1.
- The dataset (manifest SHA-256) is hashed into the F1 freeze record.

## Known limits

- The idioms are small and single-file. Cross-module flows, PQ/T hybrids, DH and DSA are not covered; hybrids are covered by the real dataset and the unit tests.
- The ground truth is by construction. It is only as good as the generator, which is why the external validation of 20% matters. That validation has not happened yet (checklist A1).
