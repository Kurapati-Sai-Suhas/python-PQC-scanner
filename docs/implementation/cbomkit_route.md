# CBOMkit: execution routes (checklist C3), investigated 14 Nov 2026

**Status: not run, so not evaluated.** No CBOMkit result exists, and none may be reported until it has been run at a pinned version.

## Facts checked

| Item | Finding |
|---|---|
| Upstream | `cbomkit/cbomkit-action` (formerly PQCA; Apache-2.0); latest release `v2.3.0` (2026-09-07). Scanning engine: `cbomkit/sonar-cryptography` (Apache-2.0). |
| Python coverage | pyca/cryptography only ("100%" per its README). **PyCryptodome is not supported**, so CBOMkit cannot find PyCryptodome sites by design. |
| Form | A Maven Java project (`pom.xml`, `src/`). The GitHub Action runs it in the container `ghcr.io/cbomkit/cbomkit-action:<tag>`. Inputs are environment variables (`GITHUB_WORKSPACE`, `GITHUB_OUTPUT`, `CBOMKIT_LANGUAGES=python`, `CBOMKIT_EXCLUDE`). By default it **excludes test files**; setting `CBOMKIT_EXCLUDE` to an empty string turns that off. |
| Output | CycloneDX CBOM (crypto assets with locations). There is no per-site migration text, so in Experiment A its sites are expected to judge as DETECTED_ONLY or MISSED, not CORRECT or INCORRECT. |
| This machine | Docker CLI 29.5.2 is installed, but the Docker Desktop engine (WSL distribution `docker-desktop`) is stopped. OpenJDK 21 is installed. Maven is not installed. |

## Routes (each needs a decision by the user)

1. **Docker Desktop (recommended).** The user starts Docker Desktop. The pinned image `ghcr.io/cbomkit/cbomkit-action:v2.3.0` is then pulled (a download, needs approval) and run on each repository directory with `GITHUB_WORKSPACE` pointing at it. This is closest to the published tool and adds an adapter (`load_cbom`) and a batch-runner entry.
2. **Local JVM build without Docker.** Download Apache Maven, or use a wrapper, and build `cbomkit-action` at tag `v2.3.0` with OpenJDK 21. Maven then downloads the dependency tree. That is many third-party downloads (needs approval), and the build may differ from the published image. It is acceptable only if the image route is impossible, and the build is recorded as a deviation.
3. **GitHub Actions.** Run the action in a workflow on a separate repository holding the pinned development or validation repositories. This puts benchmark repositories into a CI service and is outward-facing. It is **not suitable for the test split**, because sealed test outputs must be produced locally after F1.

## Pre-registration proposal (decide before F1)

If CBOMkit runs, report it twice:
- on all eligible sites (primary, like every other tool);
- on the subset inside its declared scope (pyca sites, with test-file exclusion either matched or switched off).

Its PyCryptodome misses then appear as scope limits rather than unexplained misses. This is a reporting rule, not a scoring change, and it has to be added to `scoring_policy.md` before F1 if adopted.

If no route is taken, CBOMkit stays "not run" in every table, with the reason.
