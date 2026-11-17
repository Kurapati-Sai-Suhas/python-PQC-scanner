# Worked example for the manuscript (Sec. VI-F)

- `token_service.py` is an **original synthetic file** written for the paper. It is not from the pilot or from any development, validation or test repository.
- pqscan only parses it; nothing is executed.
- Every role, tier and action below is **pqscan's actual output** for the `pqscan/` tree last changed in commit 3e8ee67 (identical at the accepted commit aa9d6b0 and at HEAD), not a hand-written expectation. Captured on 18 Nov 2026:

```bash
cd docs/paper/example
../../../.venv/Scripts/pqscan scan .                                         # output_summary.txt (full arm, τ = T2)
../../../.venv/Scripts/pqscan scan . --format json -o output_scan.json       # reasons and evidence
../../../.venv/Scripts/pqscan scan . --tier-threshold T0                     # output_summary_full_T0.txt (H2-1 provenance arm)
../../../.venv/Scripts/pqscan scan . --arm method+args --tier-threshold T0   # output_summary_method_args_T0.txt (H2-1 comparator)
```

## Sites and outcomes (full arm, τ = T2)

| Site | Line | Code | Evidence found (from `output_scan.json`) | Role, tier | Action |
|---|---|---|---|---|---|
| K1 | 17 | `serialization.load_pem_private_key(pem, …)` in the private helper `_load_signing_key` | Provenance loaded-PEM. The key is returned to the in-module caller `TokenSigner.__init__`, stored in `self._key` and consumed by `self._key.sign(...)`. Consumer families {SIG}; no escape. | SIGN, T3 | RECOMMEND, SIG (ML-DSA). Algorithm `ANY`: a PEM loader does not reveal RSA vs EC, but the role does not depend on it. |
| O1 | 25 | `self._key.sign(payload, PSS, SHA256)` | Receiver resolved through the attribute to K1 (`pyca:ANY:private:loaded-PEM`); PSS argument | SIGN, T3 | RECOMMEND, SIG |
| O2 | 33 | `key.sign(payload, PKCS1v15, SHA256)` in `sign_with(key, …)` | Receiver is an untyped parameter (unresolved); the RSA-specific padding is visible | SIGN, **T1** | **ABSTAIN** (tier T1 < T2). The role is inferred but not acted on. |
| K2 | 37 | `rsa_alias.generate_private_key(...)` returned from the public `make_key()` | Provenance generated. The key leaves the analysed scope (returned from a public function; external callers possible); no consumer seen. RSA is multi-purpose. | **UNKNOWN**, T1 | **ABSTAIN**. Possible roles SIGN, VERIFY, PK_ENCRYPT, PK_DECRYPT. |
| K3 | 42 | `rsa_alias.generate_private_key(...)` stored in `Envelope._k` | Consumers `self._k.sign` (SIG) and `self._k.decrypt` (PKE): two families | **UNKNOWN**, T2 | **ABSTAIN**. Possible roles PK_DECRYPT, SIGN, VERIFY. |
| O3 | 45 | `self._k.sign(message, PSS, SHA256)` | Receiver resolved to K3; the origin also feeds another family, so the tier is capped | SIGN, T2 | RECOMMEND, SIG |
| O4 | 49 | `self._k.decrypt(ciphertext, OAEP)` | As O3 | PK_DECRYPT, T2 | RECOMMEND, KEM_DEM ("redesign as KEM + KDF + AEAD; not a drop-in") |

## The same file under the H2-1 comparison (illustration only, not a result)

| Site | `full` at T0 | `method+args` at T0 |
|---|---|---|
| K1 | RECOMMEND SIG (T3) | ABSTAIN (UNKNOWN, T1: key material without provenance has no role) |
| O1 | RECOMMEND SIG (T3) | RECOMMEND SIG (T1) |
| O2 | RECOMMEND SIG (T1) | RECOMMEND SIG (T1) |
| K2 | ABSTAIN (UNKNOWN) | ABSTAIN (UNKNOWN) |
| K3 | ABSTAIN (UNKNOWN) | ABSTAIN (UNKNOWN) |
| O3 | RECOMMEND SIG (T2) | RECOMMEND SIG (T1) |
| O4 | RECOMMEND KEM_DEM (T2) | RECOMMEND KEM_DEM (T1) |
| **RECOMMEND count** | R_F = 5 | R_M = 4 |

Matching (equation 1) gives k = min(5, 4) = 4, so `full` withdraws e = 1 recommendation. Its lowest recommended tier is T1, and only O2 is there. So the boundary tier b = T1, with j = 1 and m = 1, and O2 is withdrawn with probability w = j/m = 1 (equation 2a). It is then scored as ABSTAIN. Whether this helps or hurts δ̃_r depends on the human label of each site. No labels exist for this file, so **no correctness figure is implied**.
