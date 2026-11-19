# Third AI specification review: combined report and closure matrix (19 Nov 2026)

**How it was run.** Two AI reviewer agents with fresh contexts. Neither had access to the implementing conversation, the owner's messages or the other agent's work.
- **Package A** reviewed the current specification without its history: 29 findings, TA01–TA29.
- **Package B** audited the closure record of F01–F21 and G01–G11: 12 findings, TB01–TB12.

Both were read-only and barred from labels and protected material, and both had to cite file and line evidence. Their reports are preserved verbatim in `package_A_specification_review.md` and `package_B_closure_audit.md`.

**What this is not.** The reviewers are the same model family as the assistant that built the project. This is **not** independent review and **not** the external human review the protocol requires before F1; that remains pending.

## 1. Headline

- **Package B:** every F01–F21 and G01–G11 closure is supported by repository evidence. No hypothesis, threshold, estimand, test, family, sampling rule or label outcome changed, archives and adoption hashes are intact, simulations are never presented as accuracy, and AI reviews are never presented as human validation. The one major item, TB01 (G08), is now **resolved by explicit owner confirmation**.
- **Package A:** the specification is detailed and mostly consistent, and the H2 machinery matches the code. It found:
  - 1 code/specification mismatch (TA02, fixed);
  - 3 paper inaccuracies (TA12, TA13, TA29, fixed);
  - one paper-relevant acceptance gap (TA01: S16 has no written exemption; the paper wording is corrected, and the exemption is an owner item before F1);
  - a set of underdefined rules that must be settled **before F1**: H1a numerator, H3 harmful-rate definition, H4 quantifier and split, κ rule, and labelling rules for protocol configuration, escaped single-purpose keys and the PyCryptodome cipher idiom.

## 2. Critical and major issue register

| ID | Severity | Issue (short) | Status |
|---|---|---|---|
| TB01 | major | G08 marked CLOSED although the owner's wording might differ from the implemented set | **Resolved:** owner confirmed exactly eight F-A baselines (`docs/audit/owner_decision_g08_confirmation_2026-11-19.md`; revision r4) |
| TA01 | major | S16 exceeds the plan's acceptance criterion; the exemption is not written | **Open: owner decision and formal plan revision before F1.** Paper now says so |
| TA02 | major | `fa.py` printed the withdrawn "independent pairs" assumption | **Corrected:** text aligned with plan Sec. 9; pinned by a test |
| TA03 | major | H3 "harmful rate" definition; always-recommend comparison confounded by coverage | **Open: owner decision (run specification H-5) before F1** |
| TA04 | major | H4 quantifier (one operator for all tools, or per tool) | **Open: owner decision (H-6) before F1** |
| TA05 | major | H4 includes synthetic-dev base cases; split not specified | **Open: owner decision (H-6) before F1** |
| TA06 | major | Taxonomy's PROTOCOL_CONFIG examples name out-of-scope calls | **Open: guide/taxonomy revision before annotation** |
| TA07 | major | Escaped single-purpose key: guide says UNKNOWN, scanner says the algorithm's role | **Open: guide revision before annotation (affects scoring)** |
| TA08 | major | H1a numerator undefined | **Open: owner decision (H-2) before F1** |
| TA09 | major | Which κ triggers the reliability rule | **Open: protocol wording (the code uses intra-rater κ)** |
| TA10 | major | `api_coverage.md` not hashed at F1 | **Open: add to the F1 hash list (protocol revision)** |
| TA11 | major | PyCryptodome split idiom (`cipher = PKCS1_OAEP.new(key)`; `cipher.encrypt`) | **Open: guide revision before annotation** |
| TA12 | major | Paper misstated the amendment history | **Corrected in the paper** |

## 3. Minor findings

| ID | Short | Status / required route |
|---|---|---|
| TA13 | Paper: confirmatory scope | **Corrected in the paper** |
| TA14 | "Two-thirds app" holds only when the quota is reached | Protocol wording (revision) |
| TA15 | Estimand wording when failures exist | Protocol wording (revision) |
| TA16 | Monte Carlo rule scope | Plan wording (revision) |
| TA17 | K taken from the input length in `h2.py` | Owner decision: `h2.py` is in the E30 calibration closure; alternatively assert K = 7 in the future E driver |
| TA18 | B2 "always recommend" wording | Run-specification wording (revision) |
| TA19 | `hybrid_component` allowed for any role | Guide/schema rule (revision) |
| TA20 | v1.0.3 paired-test traceability note | Protocol note (revision) |
| TA21 | Matching hash timing | Plan wording or code (revision) |
| TA22 | Unresolved bounding not applied to F-A or H1 | Owner decision |
| TA23 | AI-review isolation is self-recorded | Protocol wording (revision) |
| TA24 = TB04 | Attestation does not cover manual scanner runs | Protocol wording (revision) |
| TA25 | Seed derivation not stated | Protocol wording (revision) |
| TA26 = TB02 | "Every baseline": H1b versus H4 sets | **Resolved:** documented in the run specification (r4) |
| TA27 | F_F,r undefined | Plan wording (revision) |
| TA28 | H3 bootstrap procedure | Owner decision (H-5) before F1 |
| TA29 | Paper: labels "never committed"; forbidden-token exception | **Corrected in the paper** |
| TB03 | "T0 comparators" read as a criterion | **Resolved:** roles reworded (r4) |
| TB05 | Test-split attribution path stated three ways | Protocol/guide wording (revision) |
| TB06 | G03 bound applies to the DV pool only | Recorded; the paper already scopes the count to the DV frames |
| TB07 | G01 frame count has no saved artefact | Recorded; does not affect the closure |
| TB08 | G10 "pre-specified" is self-attested | **Corrected in the paper** (self-attested wording) |
| TB09 | Stale test docstring | **Corrected** (archived copy kept) |
| TB10 | Execution records rewritten in place (E01) | Recorded; future records use appended updates |
| TB11 | N1 not in the protocol threats | Owner decision on N1 pending; disclosed in the paper |
| TB12 | Package B omitted some code a closure relies on | Recorded; future packets list every cited file |

## 4. Changes made in response (revision v1.0.5-r4, 19 Nov 2026)

- **Run specification (MD and JSON):** the G08 confirmation, the inclusion criterion, and why the H1b and H4 sets differ. The eight-member set is unchanged.
- **`pqscan/bench/h4.py`:** docstring and `REPORTED_SEPARATELY`.
- **`pqscan/bench/fa.py`:** F-A assumptions text (TA02).
- **Tests:** `tests/test_g08_confirmation_and_fa_assumptions.py` (new); docstring fix in `tests/test_second_review_closure.py`.
- **Records:** `docs/audit/owner_decision_g08_confirmation_2026-11-19.md` (new); a dated pointer appended to `owner_decisions_g02_g03_g08_g10.md`; adoption record `adoption_record_v1.0.5-r4.json`.
- **Archives:** pre-change texts in `docs/specification/archive/v1.0.5-r3/`; both third-review packets still reproduce.
- **Paper:** TA01 wording, TA12, TA13, TA29, TB08, the G08 sentence, the third-review status in Fig. 3 and in the threats paragraph.

## 5. Changes that would need a formal protocol revision (not made; owner decisions before F1 or annotation)

TA01, TA03–TA11, TA14–TA25 (except TA17's code route), TA27, TA28, TB04/TA24, TB05, TB11. None of them changes a threshold. Several (TA03, TA04, TA05, TA08) settle how an existing hypothesis is computed and must be decided **before F1**. TA06, TA07, TA11 and TA19 change labelling rules and must be decided **before any annotation**.
