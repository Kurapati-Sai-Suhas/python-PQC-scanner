# Test-split qualification, round 3: a second PyCryptodome repository (14 Nov 2026)

Purpose: resolve manifest open condition 1. The protocol asks for two PyCryptodome-using test repositories, and only `saltstack/salt` qualified in rounds 1–2 (13 Nov 2026).

**When this is allowed.** Qualification is repository-level and mechanical:
- GitHub metadata and licence;
- a shallow clone, deleted afterwards;
- counts of Python files, regex candidates and imports.

No call site is read, labelled or scanned by pqscan or any baseline. The six earlier test repositories were qualified the same way. The sampling frame is part of the pre-test freeze F1 (evaluation protocol v1.0.1 Sec. 6), so this round had to finish before F1, and it did.

## Search

1. GitHub code search, Python only, up to 100 hits each, for:
   - `from Crypto.PublicKey import RSA`
   - `from Crypto.Signature import pkcs1_15`
   - `from Crypto.Cipher import PKCS1_OAEP`
   - `from Crypto.PublicKey import ECC`
   - `from Cryptodome.PublicKey import RSA`
   
   This gave 388 distinct repositories.
2. Metadata filter (GraphQL): ≥ 100 stars, not archived, not a fork. 100 repositories remained.
3. Manual exclusion, by repository description only, of anything that is not application or library software suitable for a benchmark:
   - CTF archives and write-ups;
   - exploit, proof-of-concept and malware code;
   - DRM-bypass and scraping-script collections;
   - personal script bundles;
   - course projects;
   - the PyCryptodome library itself;
   - repositories that also appear in a baseline's tuning corpus.

   `lowRISC/opentitan` was not attempted: it is a hardware SDK, very large, and its Python is build tooling.
4. The remaining 12 were run through `experiments/bench/verify_candidates.py` (same thresholds as rounds 1–2: ≥ 100 stars, ≥ 10 regex candidates in crypto-importing files, OSI licence, not archived, not in a baseline corpus). One addition: `pycryptodome_pk_imports` counts PyCryptodome public-key imports (`Crypto.PublicKey`, `Crypto.Signature`, `PKCS1_OAEP` / `PKCS1_v1_5` ciphers), so that AES-only or hash-only use does not count as RSA/ECC use.

Results: `candidate_verification_round3.{json,md}`.
- 8 accepted: Demonware/jose, CZ-NIC/pyoidc, tsileo/microblog.pub, hclivess/bismuth, LinOTP/LinOTP, mautrix/python, binref/refinery and kokarare1212/librespot-python. Of these, LinOTP and librespot-python have only 2 PyCryptodome public-key imports each.
- Rejected: fzlee/alipay (licence unverified), simon-weber/gpsoauth and delta-mpc/python-psi (fewer than 10 candidates), okta/okta-sdk-python (2 candidates; its first clone failed on Windows path length and was retried with `core.longpaths` for that process only).

## Selection rule and result

The rule was stated before choosing: take the accepted candidate with the most PyCryptodome public-key imports. Result: **`hclivess/bismuth`** at commit `328a6b9d61337b19d9b4635fd889535d540bde45` (2026-10-18). It is a blockchain node and wallet, GPL-3.0 and 177 stars, with 55 regex candidates and 19 PyCryptodome public-key imports. It adds a domain (blockchain signatures) not covered by the other test repositories.

It was added to `benchmark/real/manifest.json` → `splits.test`, with an `amendments` entry, and open condition 1 is marked resolved. Like every test repository, it is fetched only with `--include-test` after F1.

Alternates, in rule order, if bismuth turns out unusable after F1 (for example, too few eligible sites):
1. mautrix/python (4)
2. tsileo/microblog.pub (4)
3. Demonware/jose (4; unmaintained since 2016)
4. CZ-NIC/pyoidc (3)
5. binref/refinery (3)

Any substitution after F1 must be recorded as a deviation.
