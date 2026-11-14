# Real-repository split and ground-truth process (v0.9 — candidates proposed, freeze pending verification)

Status: the **process** is frozen (this document, `annotation_guide.md`, `evaluation_protocol.md` Sec. 2–3). The **repository list** is a proposal: each candidate must be verified (licence, star count, pyca/PyCryptodome usage, ≥ 10 regex candidates, clean clone at a recorded commit) by `experiments/bench/verify_candidates.py` in the first stage of Phase 2 and then written to `benchmark/real/manifest.json` with commit hashes **before Module C (role inference) is written**. Until that manifest exists, no repository is "frozen".

## 1. Exclusions (verified 12 Nov 2026 from the baseline tools' own files)

Repositories used by any baseline for tuning or validation are excluded from the **test** split (they may appear in development):

- pqcheck `tests/corpus/corpus.yaml` + `holdout.yaml` (Python entries): certbot/certbot, jpadilla/pyjwt, lepture/authlib, mpdavis/python-jose, oauthlib/oauthlib, paramiko/paramiko, sigstore/sigstore-python, borgbackup/borg, astral-sh/uv (see `docs/pilot/h1_pilot_analysis.md` for which list each pilot repo is on).
- Quantum-Safe Auditor evaluation corpus: mpdavis/python-jose, tlsfuzzer/python-ecdsa, sybrenstuvel/python-rsa (plus Java/JS repos).
- Mehl ESEM 2026 ground truth (Python entries): pyca/cryptography, tlsfuzzer/python-ecdsa, pyca/pyopenssl, tlsfuzzer/tlslite-ng, open-quantum-safe/liboqs-python, paramiko/paramiko, sybrenstuvel/python-rsa, jpadilla/pyjwt, mpdavis/python-jose.

## 2. Proposed split (to be verified)

| Split | Candidate repositories | Domain | Library (expected) | Role in study |
|---|---|---|---|---|
| development | paramiko/paramiko (pilot), mpdavis/python-jose (pilot), jpadilla/pyjwt, lepture/authlib | SSH, JOSE | pyca (+ python-rsa/ecdsa out of scope) | rule and resolver tuning |
| validation | latchset/jwcrypto, ronf/asyncssh, secure-systems-lab/securesystemslib | JOSE, SSH, supply-chain signing | pyca; securesystemslib also PyCryptodome? (verify) | τ threshold, operator choice |
| test (held-out) | Netflix/lemur, googleapis/google-auth-library-python, MatthiasValvekens/pyHanko, keylime/keylime, in-toto/in-toto, theupdateframework/python-tuf, mitmproxy/mitmproxy (crypto modules only), twisted/twisted (conch only) | PKI, cloud auth, PDF signing, attestation, supply chain, TLS proxy, SSH | pyca; PyCryptodome presence to be verified | frozen evaluation; never inspected before the Phase 3 freeze |

Rules: at least two test repositories must use PyCryptodome; if the candidates above do not provide them, PyCryptodome-dependent projects will be searched by `pip download` reverse-dependency listing and GitHub code search, and the choice documented before any labelling. Minimum per split: development ≥ 3, validation ≥ 2, test ≥ 4 repositories; test ≥ 150 eligible sites.

## 3. Ground-truth process

1. Candidate discovery per repository = union of: regex over-approximation (pattern list in `pqscan/bench/candidates.py`, identical to the qualification regex in `experiments/bench/verify_candidates.py`), every baseline's findings (adapters), our Module A. Deduplicate by enclosing statement (the "line window"). Earlier drafts named `experiments/bench/regex_candidates.py`, a script that was never created; the pool builder replaces it (2026-11-14).
1a. Sampling (protocol v1.0.3 Sec. 2; owner decisions D2 = O2, D3): seeded (20261113), stratified (S1-app, S1-test, S2), quota-based sequential batches. Eligible quota: 30 per test repository, 25 per development or validation repository. Test-path sites count up to one third of a quota; 10 fixed S2 candidates per repository; candidate cap 4 × quota; shortfalls reported. Annotators receive location-only lists (`pqscan.bench.candidates annotator_list`).
2. Two annotators label from source per `annotation_guide.md`; tool outputs hidden.
3. κ per field; adjudication; publication of all labels.
4. Test-split labels are produced **after** the Phase 3 freeze by annotators who have not seen the analyzer's output on those repositories, and are never used to repair the system.
5. A missed operation is an eligible adjudicated site with no tool finding in its window; execution failures are logged per file separately.

## 4. Candidate verification checklist (`verify_candidates.py` output per repo)

licence (OSI), stars, default-branch commit hash and date, Python file count, regex candidate count, pyca/PyCryptodome import counts, test-path share, presence in any exclusion list, decision (accept/reject with reason).
