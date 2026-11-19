# Pipeline and reproducibility check on demonstration material (19 Nov 2026, after r3 commit `161edd5`)

**Scope.** Development and demonstration material only: the synthetic lecturer-demo repository `docs/demo/demo_repo` and a copy of the installed pyca/cryptography 47.0.0 package's `.py` files (a dependency, not a benchmark repository). No benchmark repository of any split was scanned or opened. Nothing was written to `runs/` or `benchmark/`. Scratch outputs went to a temporary folder outside the repository.

**Environment.** The project virtual environment (Python 3.12, pqscan installed in editable mode, Semgrep 1.185.0) on Windows 11. The fresh-venv rebuild from `git archive` (`docs/final/demo/run_final_demo.sh`, recorded in `docs/final/demo/RUN_LOG.md`) was **not** repeated today.

| Check | Result |
|---|---|
| Seven lecturer-demo commands (summary, JSON, CBOM, SARIF, `--tier-threshold T3`, `--arm method-only`, `--no-semgrep`) against the committed `docs/demo/outputs` | All 7 **identical** after line-ending normalisation. Byte comparison differs only by CRLF on Windows, as `RUN_LOG.md` documents |
| CBOM determinism (two runs, demo repository) | Byte-identical |
| cryptography-47.0.0 JSON, CBOM, SARIF against the committed `docs/final/demo/outputs/real` | All 3 **identical** after line-ending normalisation |
| Independent validation (`docs/final/demo/validate_outputs.py`) | 3 CBOMs VALID (CycloneDX 1.6 strict); 3 SARIF VALID (SARIF 2.1.0) |
| Full test suite at `161edd5` | 725 passed, 1 skipped |
| Evidence recomputation (`docs/paper/verify_evidence.py`) | 110 values, 0 failed |

**Not repeated today:** the pycryptodome-4.4.0 scan (1,214 sites; its committed outputs are still validated above) and the fresh-environment rebuild.

**Interpretation.** These results show the pipeline is deterministic and its exports are valid. They are **not** evidence of scanner accuracy: there are no labels for this material, and the evaluation (F1, F2, E) has not been run.
