# GitHub release record

No credentials appear in this file. Authentication used the GitHub CLI's existing keyring login (`gh auth status`: account `Kurapati-Sai-Suhas`, HTTPS).

## Phase 2 checkpoint (14 Nov 2026)

| Item | Value |
|---|---|
| Remote | `https://github.com/Kurapati-Sai-Suhas/python-PQC-scanner.git` (public) |
| Remote state before push | created 2026-11-14T08:01:15Z, empty (no commits, no README, no licence) |
| Local state before push | no git repository; `git init -b main` on 2026-11-14 |
| Branch | `main` (default branch on GitHub) |
| Commit | `81f561e34997dc56b2728241617cd19785210c85` "Phase 2 complete: pqscan system implementation snapshot" |
| Tag | `phase2-complete` (annotated; tag object `b8b8f72e5b8db10862f493570f1a27bbb544d6e8`; target `81f561e3…`) |
| Push | ordinary push of `main` and the tag; no force push |
| Commit identity | `Kurapati-Sai-Suhas`, GitHub no-reply e-mail (set in this repository's local git config, so a personal address is not published) |
| Files | 175 tracked files; 0.84 MiB loose objects before packing |
| Development branch | `phase3-preparation`, created from `81f561e3`; `main` stays the stable Phase 2 version |

This tag marks the Phase 2 checkpoint. It is **not** the Phase 3 freeze. That freeze uses the tag `phase3-pretest-freeze` (evaluation protocol v1.0.1, Sec. 6).

### Relation to the Phase 2 closure fingerprint

`docs/implementation/phase2_closure_fingerprint.json` (tree `5cbe7392…f437`, 92 files) was taken before publication. The committed tree hashes to `c46ac27f28239f5abd7b1df02317473cb4fb2484bf7124c6a8e238908f83202d` over the same 92 files. The only differing file is `README.md`, which gained a Status/Licence section and an updated hybrid-limit paragraph before the commit. No code, test, specification or manifest differs.

### Intentionally excluded (`.gitignore`)

| Excluded | Reason |
|---|---|
| `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `.coverage` | local environment and build or test artefacts; reproducible from `pyproject.toml` |
| `.cache/`, `node_modules/` | downloaded third-party repositories and baseline tools; re-created at pinned commits by `scripts/fetch_pinned.py` |
| `results/`, `runs/` | Phase 3 run outputs, committed only deliberately after the relevant freeze |
| `benchmark/labels/test/`, `benchmark/labels/*test*` | held-out labels stay out of git until the test-label freeze F2 |
| `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, editor folders | secrets and local configuration |

`.gitattributes` normalises text to LF and keeps `tests/fixtures/baseline_errors/**` byte-exact (null-byte, Latin-1 and syntax-error fixtures).

### Pre-commit audit

- **Secret scan** of the staged content (patterns for API keys, GitHub tokens, AWS keys, Slack tokens, bearer tokens, long base64 runs, personal e-mail). One hit: the deliberate dummy key `tests/fixtures/project/app/keys.py`, whose body is the string "testonly…". It is not a real key; the no-secrets tests depend on it.
- **PEM strings:** the remaining PEM strings are in pilot tool outputs (`docs/pilot/raw_tool_outputs/qsa_*.json`, `pqcaudit_paramiko.cbom.json`). They are only `-----BEGIN … PRIVATE KEY-----` header lines and key fingerprints that the tools quoted from public test files of paramiko (LGPL-2.1) and python-jose (MIT). None of the 18 snippets with long base64 runs contains key material; they are SSH key fingerprints.
- **Consensus API key:** it appears in no file. Documents mention only that it must be rotated.
- **Held-out test split:** no test repository was fetched, and no test labels, predictions or source snippets exist. The repository contains only the pre-registered sampling frame (`benchmark/real/manifest.json`: repositories and commits) and the Phase 1 repository-level qualification counts (`docs/benchmark/candidate_verification.{json,md}`: stars, licence, file and import counts).
- **Absolute paths:** some pilot tool outputs and the test log contain local paths (`C:\Users\Suhas\...`). They were left unchanged, because they are raw research artefacts.
- **Third-party files:**
  - CycloneDX 1.6 JSON schema (Apache-2.0) and OASIS SARIF 2.1.0 schema in `pqscan/export/schemas/`.
  - Short code snippets inside pilot tool outputs (from paramiko and python-jose, both open-source licences).
  - No fonts or binaries from third parties. The PDF builder takes DejaVu from the local environment, and the fonts embedded in the PDFs carry the DejaVu licence.

### Post-push verification

| Check | Result |
|---|---|
| `git ls-remote origin` | `refs/heads/main` and `refs/tags/phase2-complete^{}` both `81f561e3…` |
| Tag type via the API | `tag` (annotated) |
| GitHub default branch and visibility | `main`, PUBLIC |
| Required files present on the remote (API) | Phase 2 report PDF (130,915 bytes), `pqscan/semantic/hybrid.py`, `docs/specification/scoring_policy.md` |
| Fresh clone of `phase2-complete` | 175 files; none from `.venv`, egg-info, coverage or caches; failure fixtures byte-identical; tree hash `c46ac27f…` |
| Full test suite on the fresh clone (2026-11-14, pqscan imported from the clone) | **285 passed, 1 skipped** (the symlink privilege test), 88.9 s |

## Open decision for the user

- **Licence:** none was chosen, so the public code is "all rights reserved" by default. Choosing one (for example MIT or Apache-2.0) is the user's decision. The README says no licence is chosen.
