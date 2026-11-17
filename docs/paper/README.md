# docs/paper: IEEE paper preparation (provisional)

**Status:**
- The manuscript is a provisional, template-neutral **implementation and pre-registered evaluation-design** draft.
- It is **not** a completed empirical paper: no labelled results exist.
- IEEE formatting waits for the owner's sample paper (`author_decisions.md` D1).

| File | Purpose |
|---|---|
| `ieee_manuscript_draft.md` | Provisional manuscript content (Sections I–XIV), with explicit NOT YET EVALUATED placeholders |
| `evidence_register.md` | Every important claim: value, source, verification, evidence class, safe-to-publish flag; test-count reconciliation |
| `verify_evidence.py` | Recomputes 81 manuscript values from raw files (`--write` → `evidence/evidence_values.json`); exit 1 on any mismatch |
| `evidence/test_log_a640c15.txt` | Test-suite log behind the 489 / 475 / 82 / 95 / 7 figures |
| `references.bib` | 54 verified BibTeX entries (Crossref, DataCite, NIST PDFs, Ecma, OASIS, JSTOR), each with a verification note |
| `related_work_matrix.md` | Prior work by category, with content-verification level; novelty provisional |
| `results_placeholders.md` | Every future table, figure and metric with its prerequisite |
| `author_decisions.md` | Decisions only the owner can make (format, title, scope, licence, …) |
| `owner_action_checklist.md` | Ordered owner-gated steps vs work Claude can do now |
| `peer_review.md` | Strict reviewer assessment and correction list |
| `related_work_fulltext_audit.md` | Full-text and pinned-source verification of related work, with pages and file:line; NOT FULL-TEXT VERIFIED list; scoped absence claim |
| `d7_rq_alignment.md` | Author decision D7: which comparisons are coverage-matched; two presentation options; recommendation |
| `example/` | Original synthetic worked example and pqscan's actual outputs (Sec. VI-F) |
| `figures/` | Figs. 1–4 as vector SVG/PDF, built by `make_figures.py` (template styling pending) |

Re-run before any edit to the manuscript's numbers:

```bash
.venv/Scripts/python docs/paper/verify_evidence.py --write
```
