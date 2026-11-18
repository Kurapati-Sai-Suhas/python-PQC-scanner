# Research decisions and novelty status (18 Nov 2026)

**Scope.** This document covers the owner's D7 decision and the inspection behind D14 and D15. Nothing here changes protocol v1.0.4, annotation guide v1.1, the frozen baseline manifest or any confirmatory family. Every proposed change below waits for explicit owner approval.

## D7: research-question alignment — DECIDED: Option A (owner, 18 Nov 2026)

**Applied in:**
- manuscript Sec. I (after the verbatim RQ) and Sec. IX ("How the adopted RQ is operationalised");
- the decision log in `docs/paper/author_decisions.md`;
- `docs/paper/d7_rq_alignment.md` (status updated; the analysis of both options is kept as the historical record);
- `docs/paper/peer_review.md` R2.

**Wording now in force:**
- **F-B / H2a (and H2-3, H2-4)** compares the provenance-aware analysis with method/argument-based analysis at **matched recommendation volume** per repository.
- **F-A** compares the proposed system with the algorithm-name mapping, the method/argument-only mapping and the external tools at **natural coverage**, with coverage printed alongside.
- **Every F-A finding is described as a natural-coverage comparison.** No result is presented as superior correctness over algorithm-family baselines at comparable coverage.

The RQ text and the protocol are unchanged.

## D14: Mehl ESEM 2026 scanner — recommendation: exploratory, detection-level only, outside every confirmatory family (needs owner approval)

**What was inspected (read-only, GitHub API, 18 Nov 2026; nothing cloned or executed):**

| Question | Finding | Source |
|---|---|---|
| Is the source public? | Yes: `github.com/Lxkasmehl/pqc-scanner`, MIT licence, default branch `main` at `d8cf5bdc7eb4…` (committed 2026-07-30) | GitHub API repository and commit metadata |
| Why did we say "no source"? | The Zenodo record (all 4 versions, 1.0–3.0) contains only results: `raw.zip`, `aggregate.csv`, reports and the reference set. Its description links the GitHub source, and the paper (p. 1) says the supplement includes the scanner source. Our manifest reason "contains results only, no scanner source" is accurate about Zenodo but wrong as a general statement. | Zenodo API; paper p. 1 |
| Python compatibility | `requirements.txt` declares Python 3.11+. Our environment is 3.12. | `requirements.txt` |
| Dependencies | typer, python-dotenv, loguru, httpx; tree-sitter (+ java, go grammars) optional for Java/Go; pytest | `requirements.txt` |
| Local scanning | `cli.py scan local <path>`. A GitHub mode exists, plus an optional token in `.env`; neither is needed for local scans. | `cli.py` |
| Output | One JSON per repository with `findings`. Each Python finding has a line number, primitive, library, snippet and confidence (`scanner/detectors/python_detector.py`, the `_add(line, …)` calls) | source |
| What it decides | Classification only: post-quantum-vulnerable / quantum-safe / pqc-ready / unknown (`scanner/classifier.py`). **No migration target and no role.** The paper says it does not prescribe migration (p. 3). | source; paper |
| Fair evaluation under our frozen protocol? | **At detection level only.** Under the frozen judge its findings are FLAG_NO_TARGET, because it names no target. It can never be RECOMMEND-correct or harmful. That would be CORRECT only where the expected class is NONE (inventory and hybrid sites) and DETECTED_ONLY elsewhere. Including it in F-A would be uninformative for recommendation correctness, and it would change the frozen F-A family. | scoring policy Sec. 2 |
| Effort | About 1.5–2 h: pin commit d8cf5bd; venv; adapter for its JSON (file, line, primitive → text); failure profile on the errcheck fixture; one DV run (execution-level only, blinding). | estimate |
| Risk | Low technical risk (pure-Python `ast`). Process risk: adding any baseline needs approval. The adapter must not leak DV findings to the owner before labelling. | — |

**Recommendation (owner decides):**
- **(a)** Keep it **outside F-A and F-B**.
- **(b)** If approved, run it as an **exploratory, detection-level** comparison (site-level detection recall and precision on labelled sites, reported separately), pinned to `d8cf5bd`, before F1.
- **(c)** In every case, **correct the stated reason** in the paper ("reported separately because it does not emit migration recommendations by design, so it cannot be judged on recommendation correctness"). The draft already says this.
- The frozen `benchmark/baselines_manifest.json` text is **not** edited. A dated amendment note, like the manifest's existing amendment mechanism, needs your approval.

## D15: which algorithm-name mapping enters F-A — recommendation: `B1-algorithm` (needs owner approval)

**Source** (`pqscan/baselines/simple.py` ll. 1–13 and 25–27; decision function `decide`):

| Variant | Mapping | Algorithm evidence used | Output on RSA / EC sites |
|---|---|---|---|
| `B1-algorithm` | RSA → KEM, EC → SIG; X25519/X448/XDH/DH → KEM; Ed25519/Ed448/EdDSA/DSA → SIG; unresolved → DUAL | `classify(ev, "method+args+recv").algorithm`, the best algorithm evidence without provenance | one family, chosen by name: always KEM for RSA, always SIG for EC |
| `B1-dual` | multi-purpose (RSA, EC, unresolved) → DUAL; single-purpose as above | same | DUAL: never role-incompatible, never correct |

**Scientific meaning:**
- **`B1-algorithm`** is the convention most inspected tools implement: pqcheck RSA → ML-KEM-768; qsafe RSA → ML-KEM 768; the common "RSA → ML-KEM, EC → ML-DSA" mapping. It answers "how good is choosing by algorithm name?". It can be right (RSA key transport, EC signing) or role-incompatible (RSA signing, ECDH). On the synthetic demo fixture, for example, it gives KEM for RSA signing and SIG for P-384 ECDH (`docs/final/demo/baselines/side_by_side.md`).
- **`B1-dual`** is the "refuse to choose" convention (pqc-audit, the Quantum-Safe Auditor: "ML-KEM / ML-DSA"). Under the frozen judge every RSA/EC site becomes UNDECIDED. Its harmful rate is therefore near zero by construction and its correct rate near zero too (pilot, circular: 2 correct, 1 harmful, 27 undecided of 30). As an F-A comparator it is close to a strawman for correctness.
- **Phase 2 rationale:** the Phase 2 report (Sec. 3) introduced the two as "pre-stated variants [to] avoid choosing a strawman".

**Recommendation:**
- **`B1-algorithm` is the protocol's "simple algorithm-name mapping" in F-A.** It is the single decisive name-based rule the RQ's "algorithm-family baselines" refers to.
- Report `B1-dual` **descriptively, outside F-A**, as the undecided convention. This keeps F-A at ≤ 8 members: B1-algorithm, the method/argument-only mapping, six tools.
- Record the choice in the run specification before F1. That is a clarification of the protocol's wording, not a change to it, but it still needs your approval.

## Related-work and novelty status (unchanged by today's work)

- Content verification is in `docs/paper/related_work_fulltext_audit.md`: 20 papers checked in full text and 6 tools in pinned source.
- **14 works remain NOT FULL-TEXT VERIFIED:**
  - ACM pages behind bot verification: Yuan et al., BF-CBOM, Lee et al., Von Nethen;
  - behind a CAPTCHA: Yamamuro;
  - server timeout or rate limit: Schmitt, Chow;
  - no open copy: Cryptolation, CryptoPyt, Cryptbara, CrySL, Ye et al., Joseph et al.;
  - only the extension read: MASC 2022.

  They are cited only at title level. No description of their content is invented.
- **Scope of the novelty claim:** it is scoped to the inspected set. No "first" or "no existing system" claim is made. The closest unverified works (Yuan et al.; CryptoPyt; Cryptbara) must be checked before any submission. The final novelty audit (D11) is still open.
