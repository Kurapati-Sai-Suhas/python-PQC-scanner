# Evaluation summary

Results of evaluating the scanner against a curated ground-truth set of repositories.

## Counts

- Ground-truth rows: **19**
- Successfully evaluated: **19**
- Errors (e.g. clone failed): **0**

## Metrics (binary: has vulnerable / has PQC-ready)

### has_vulnerable

| Metric    | Value |
|-----------|-------|
| n         | 19 |
| TP / FP   | 14 / 0 |
| TN / FN   | 4 / 1 |
| Precision | 1.0000 |
| Recall    | 0.9333 |
| F1        | 0.9655 |

### has_pqc_ready

| Metric    | Value |
|-----------|-------|
| n         | 19 |
| TP / FP   | 7 / 0 |
| TN / FN   | 11 / 1 |
| Precision | 1.0000 |
| Recall    | 0.8750 |
| F1        | 0.9333 |

## Per-repo results

| Repo | Exp. vulnerable | Exp. PQC-ready | Pred. vulnerable | Pred. PQC-ready | OK |
|------|-----------------|----------------|------------------|-----------------|-----|
| fixtures | yes | yes | yes | yes | ✓ |
| pyca/cryptography | yes | no | yes | no | ✓ |
| golang/crypto | yes | no | yes | no | ✓ |
| tlsfuzzer/python-ecdsa | yes | no | yes | no | ✓ |
| pyca/pyopenssl | yes | no | yes | no | ✓ |
| tlsfuzzer/tlslite-ng | yes | no | yes | no | ✓ |
| open-quantum-safe/liboqs-python | no | yes | no | yes | ✓ |
| bcgit/bc-java | yes | yes | yes | yes | ✓ |
| paramiko/paramiko | yes | no | yes | no | ✓ |
| open-quantum-safe/liboqs-java | no | yes | no | yes | ✓ |
| open-quantum-safe/liboqs-go | no | yes | no | yes | ✓ |
| cloudflare/circl | yes | yes | yes | yes | ✓ |
| tink-crypto/tink | yes | yes | yes | no | ✗ |
| open-quantum-safe/liboqs | no | yes | no | yes | ✓ |
| sybrenstuvel/python-rsa | yes | no | yes | no | ✓ |
| jpadilla/pyjwt | yes | no | yes | no | ✓ |
| mpdavis/python-jose | yes | no | yes | no | ✓ |
| golang/go | yes | no | yes | no | ✓ |
| square/go-jose | yes | no | no | no | ✗ |
