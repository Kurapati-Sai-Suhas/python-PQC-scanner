# Run log: final demonstration (17 Nov 2026)

Two independent fresh-environment runs were made. Both built a new venv from `git archive HEAD`, not the working tree. pqscan's code (`pqscan/`) is identical in both snapshots, and identical to the accepted commit aa9d6b0.

| Run | Snapshot | Started → finished (UTC) | How | Result |
|---|---|---|---|---|
| 1 (recorded) | a89743a | 17:45:10 → 17:51:34 | the steps of `run_final_demo.sh`, run from a scratch copy with absolute paths | outputs committed in `outputs/`; transcript `outputs/transcript.txt` |
| 2 (script check) | 5d78a06 | 17:55:55 → 18:00:44 | `bash docs/final/demo/run_final_demo.sh <scratch>`, exactly as committed | script exit 0. Lecturer demo 7/7 IDENTICAL. All 8 real-code outputs byte-identical to run 1. Both CBOMs deterministic. |

**Machine:** Windows 11 Home (10.0.26300), Python 3.12.10.

## Environment of the fresh venv (run 1; from `pip freeze` in the transcript)

| Component | Version |
|---|---|
| pqscan | 0.1.0.dev0 (installed from the `git archive` snapshot) |
| Semgrep | 1.185.0 (pinned) |
| cyclonedx-python-lib | 11.12.0 |
| jsonschema, PyYAML, typer, pydantic | 4.25.1, 6.0.3, 0.29.1, 2.14.3 |
| cryptography (resolved for the venv) | 50.0.2 |

The scanned library copies came from the **project** venv: cryptography **47.0.0** and pycryptodome **4.4.0**. The fresh venv's own cryptography 50.0.2 was not scanned.

| Scanned copy | `.py` files | Tree SHA-256 (path + LF-normalised content) | Licence |
|---|---:|---|---|
| cryptography-47.0.0 | 77 | `f5f0572113c515567829249d71d7c30c7125bb04ef8ecb973cf7d29e17452a9b` | Apache-2.0 OR BSD-3-Clause |
| pycryptodome-4.4.0 | 228 | `1bc95ddc444287b886f4b6f70661393f311761dd8d72b45e25c19c4502432199` | BSD-2-Clause AND Unlicense AND MIT |

## Steps and exit codes (run 1)

Every command exited 0, as shown in the transcript.

| Step | Wall time |
|---|---|
| venv | 18 s |
| pip upgrade | 26 s |
| pip install of the snapshot | 165 s |
| 7 lecturer-demo commands | 3–4 s each |
| cryptography summary | 4 s |
| PyCryptodome summary | 25 s |
| PyCryptodome JSON, CBOM, CBOM again, SARIF | 24–26 s each |

## Lecturer-demo reproduction

`docs/demo/outputs/01`–`07` (recorded 16 Nov from the `phase2-complete` snapshot) compared with the fresh outputs: **7/7 byte-identical in both runs**.

## SHA-256 of the real-code outputs (raw, as written)

```
c3ec701bf4018d17a7c6e40261179646c8cc75586eb594cb36c751842bc0d18f  cryptography-47.0.0_summary.txt
0fe8decf99821263ab21e5066995bb5cf66862f40d8c33c2d69471a6998091d9  cryptography-47.0.0_scan.json
e45163e8e6ec2fcfd2d5ba2aa354f433fadc6dbbc3adabd3879a5e3f652df715  cryptography-47.0.0_cbom.json
710ea5366278c7d2fb99d12731330214e4c43952ce574688b62525890f816d37  cryptography-47.0.0_scan.sarif
ac98cb0b78702e3511ad53e7fc41161243c908a79e7107a8dc168875d10050e4  pycryptodome-4.4.0_summary.txt
3efb0a18010c5408b8fee671eaa0b12f7ba7036ef65ffa1f992acb922a834e6d  pycryptodome-4.4.0_scan.json    (committed as .gz)
b9206df73e71422654e86f9daf34e7e0dc537fd3d2f8fe859d016d4e94631699  pycryptodome-4.4.0_cbom.json    (committed as .gz)
3ecc61bad1002ae04d189aa9c4a2078b1146eefd12f6ef306aac18a1aa41150d  pycryptodome-4.4.0_scan.sarif   (committed as .gz)
```

These hashes are of the files as written on Windows, where text outputs have CRLF line endings. Git stores the committed text files with LF endings (`core.autocrlf`). On another platform, convert to CRLF before hashing, or compare with line endings normalised. The `.gz` files are binary, and their contents are the raw CRLF files. The `.gz` files were written with `gzip -n -9`, so they carry no name or timestamp. `gzip -dc <file> | sha256sum` reproduces the raw hashes above.

## Edits made after the run

- `outputs/transcript.txt`: absolute scratch paths, which contain the local user name, were replaced with `<FD>` (33 places), and pip build-temp paths with `<PIPTMP>` (3 places). Nothing else was changed. SHA-256 of the unredacted transcript: `2779e1554c1f1352331a8539140faa27772b016ac75f1d156941d93e5f45c3cb`.
- The output files themselves were not edited. They contain only paths relative to the scan folder.

## Derived files

- `outputs/real/real_stats.json`: counts computed from the two `*_scan.json` files by a read-only script (action, target class, role, tier, algorithm, receiver library, site kind, scope, role × class, tier × action, abstain reasons, exclusions, Semgrep overlap).
- `outputs/validation.txt`: from `validate_outputs.py`. Every CBOM is valid (CycloneDX 1.6 strict) and every SARIF is valid (2.1.0), including the lecturer-demo fixture outputs.
- `screenshots/*.png`: from `screenshots/render_screenshots.py`, which renders the captured text files. They are not live screen captures.

## Regeneration in revision r5 (19 Nov 2026; owner decision TA07; appended, the record above is unchanged)

The classifier change of owner decision TA07 (taxonomy rule 10) changed exactly 5 PyCryptodome findings. Escaped `DSA.import_key` keys whose public/private status is not established went from SIGN/T2/RECOMMEND to UNKNOWN/T1/ABSTAIN:
- `Crypto/SelfTest/PublicKey/test_import_DSA.py` lines 368, 370 and 383;
- `Crypto/SelfTest/PublicKey/test_import_passphrase.py` line 175;
- `Crypto/SelfTest/Signature/test_dss.py` line 1200.

All other 1,209 findings and every top-level field are byte-identical. The cryptography outputs and the 7 demonstration outputs are unchanged. Totals for PyCryptodome: RECOMMEND 210 -> 205, ABSTAIN 573 -> 578, SIG 124 -> 119. This is a stricter evidence requirement; it says nothing about accuracy.

The outputs were regenerated with the project environment from the same copied library sources (source manifest unchanged). The pre-r5 outputs are archived in `outputs/archive/pre-r5/`, and `real_stats.json` is regenerated by `make_real_stats.py` (validated by reproducing the pre-r5 file byte-for-byte).

| Output (raw, as written on Windows) | SHA-256 |
|---|---|
| `pycryptodome-4.4.0_summary.txt` | `e37346bd2760732d21ba9980031a85368ba8b46242539b2a688f69b095cd2ee4` |
| `pycryptodome-4.4.0_scan.json` | `7e7d8e016b6c041305f4c2f435efb20a70ac8681ff74dbe3996627356b9065fd` |
| `pycryptodome-4.4.0_cbom.json` | `de2f8fb89b5ca10f80d7156cae331040c14d1854d94f36138f728fa5c7f5ed52` |
| `pycryptodome-4.4.0_scan.sarif` | `903de724b3fa3f4ee1e88db9bc965be56e116284c6cf433418f88dda892a717d` |
