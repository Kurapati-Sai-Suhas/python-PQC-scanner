# R3-05 Scope classification and the non-app stratum (PROPOSED, revision 3)

## 1. Rule (one shared function for the sampler, the validator and the guide's Step F)

| Class | Matches (path relative to the repository root, forward slashes) |
|---|---|
| vendored | a directory `vendor`, `_vendor` or `third_party` |
| test | a directory `test`, `tests` or `testing`; or a file `test_*.py`, `*_test.py`, `test.py`, `tests.py`, `tests_*.py`, `tests-*.py`, `conftest.py` |
| example | a directory `example`, `examples`, `demo`, `demos` or `demo*` |
| app | none of the above |

**Precedence:** vendored > test > example > app.
- Vendored code is third-party code even when it contains tests.
- Tests placed under `examples/` are tests.

## 2. Evidence (development/validation only; `scripts/scope_rev3.py`, output in `results/scope_rev3.txt`)

- **Files:** 683 Python files.
  - Newly classified as test compared with the frozen rule: `authlib/docs/conftest.py` and jwcrypto `tests.py`, `tests-cookbook.py`, `tests_mldsa.py`. All four are genuine tests.
  - No path matches more than one class, so precedence is never exercised in development/validation.
  - asyncssh has 41 `examples/` files. None contains an S1 candidate.
- **S1 candidates under the rev3 rule:** 1,080 of 2,000 (54%) are test code:

| Repository | app | test | example | vendored |
|---|---|---|---|---|
| paramiko | 204 | 206 | 0 | 0 |
| python-jose | 55 | 62 | 0 | 0 |
| PyJWT | 111 | 282 | 0 | 0 |
| Authlib | 171 | 270 | 0 | 0 |
| jwcrypto | 236 | 143 | 0 | 0 |
| asyncssh | 143 | 117 | 0 | 0 |

- **Not checked:** the 7 test repositories (not accessed before F1). Their example and vendored content is unknown. Known theoretical false-positive risk: libraries that ship test helpers as public API (for example a `testing/` package) are classed as test.

## 3. Coverage implications of the combined one-third cap (V11)

- **Test code:** about 54% of the S1 pool, but at most one third of each repository's counted quota. Test code is therefore under-sampled relative to the pool. That is intended: migration matters most in application code. Test-scope claims rest on at most 8 sites per development/validation repository and 10 per test repository (≤ 70 test-split sites), so they are descriptive only.
- **Example and vendored:** zero in development/validation. In the test split they share the cap with test code and could crowd it out.
- **Reporting:** the three non-app classes are reported **separately** (counts, eligibility, per-method outcomes), even though they share one cap. No sub-quota is proposed, because their sizes are unknown before F1.
- **Acceptability:** acceptable for the primary aim (application code). It is a stated limitation for test, example and vendored code.
