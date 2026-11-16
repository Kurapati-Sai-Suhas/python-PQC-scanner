# DEMONSTRATION FIXTURE — synthetic, written for this demo

This folder is a **synthetic** Python "project" written only so that `pqscan` has something small and
readable to scan during the lecturer demonstration. It is **not** a real application, it is **not** part
of the Phase 3 benchmark, and it is **not** evidence of how `pqscan` performs on real code.

- **Never import or run these files.** They are only parsed by `pqscan` (Python `ast`) and Semgrep. `pqscan`
  itself never imports or executes scanned code.
- The files contain no key material, no PEM blocks, no passwords and no tokens. Keys are only "generated"
  in code that is never executed.
- The library calls follow the public APIs of PyCA `cryptography` and PyCryptodome, but nothing here has
  been run, so treat it as illustrative source, not as working sample code.

| File | What it shows | Libraries |
|---|---|---|
| `signing_service.py` | RSA-PSS signing and verification | PyCA `cryptography` |
| `envelope.py` | RSA-OAEP encryption and decryption (key transport) | PyCA `cryptography` |
| `ecdsa_tokens.py` | ECDSA signing (P-256) | PyCA `cryptography` |
| `key_agreement.py` | X25519 and ECDH (P-384) key exchange | PyCA `cryptography` |
| `key_inventory.py` | RSA key that is only generated and serialised (no consumer) | PyCA `cryptography` |
| `legacy_pycryptodome.py` | RSA PKCS#1 v1.5 signing and PKCS#1 OAEP encryption | PyCryptodome |
| `ambiguous.py` | Deliberately ambiguous cases: an untyped parameter, and one RSA key that reaches both signature and decryption consumers | PyCA `cryptography` |

What `pqscan` actually reported for these files is in `../outputs/` and is explained in
`../expected_outputs.md`.
