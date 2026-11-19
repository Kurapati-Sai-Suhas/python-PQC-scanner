# Branch consolidation into `main` (19 Nov 2026)

**Decision.** The owner decided on 19 Nov 2026 to consolidate the repository into one branch, `main`, so that every approved project commit is reachable from the default branch. The consolidation plan was approved before any step was executed.

**Before.**
- `main` = `81f561e34997dc56b2728241617cd19785210c85` (the Phase 2 snapshot; tag `phase2-complete`).
- `phase3-preparation` = `9cc87d518e5051e9224c16b7f5c8bcfabeeca83c`, 59 commits after `81f561e`, no merge commits; every commit attributed to the owner's GitHub account.
- No branch protection, rulesets or workflows on GitHub; `main` is the default branch.

**Baseline preserved.** Annotated tag `pre-consolidation-main-81f561e` → `81f561e34997dc56b2728241617cd19785210c85` (pushed before any branch changed). The existing annotated tag `phase2-complete` points to the same commit.

**Method.** Fast-forward only (`git merge --ff-only`; `git push origin main` without force). No rebase, squash, force-push or history rewriting; no commit lost. Two commits were added on top of the approved history: the consolidation commit (E01 checks, this record, README, release-record note, regression test) and the evidence-values commit recorded on `main`.

**Evidence.** `docs/paper/verify_evidence.py` E01 no longer asserts that `main` equals the baseline. It verifies, exactly: the tag `pre-consolidation-main-81f561e` is annotated and points to `81f561e…`; `phase2-complete` points to the same commit; `main` contains the baseline, has no merge commits since it, and contains the pre-consolidation head `9cc87d5…`; and this record exists. `tests/test_branch_consolidation.py` repeats these checks.

**After.** `phase3-preparation` is deleted locally and on GitHub only after every check passed on `main`. Draft pull request #1 (`phase3-preparation` → `main`) is closed by GitHub as merged when its commits reach `main`.

**Unchanged.** The scientific protocol (v1.0.5) and its companions, the scanner, every threshold, hypothesis and family, the adoption records, both review packets, the E30 calibration closure, the AI-review identity record and the F1/F2/E approval gates. Dated records written before 19 Nov 2026 that describe `main` as untouched or name `phase3-preparation` are historical and stay as written.
