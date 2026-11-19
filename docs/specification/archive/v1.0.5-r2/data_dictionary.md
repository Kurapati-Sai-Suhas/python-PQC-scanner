# Data dictionary (v1.1)

Project: Post-quantum crypto scanner for Python projects. Companion to `role_taxonomy.md`, `recommendation_policy.md`, `evaluation_protocol.md`.

## 1. Benchmark site record (`benchmark_schema.json`, one object per site)

| Field | Type | Values / notes |
|---|---|---|
| `site_id` | string | unique; synthetic `S-<base>-<variant>`, real `R-<repo>-<n>`, pilot `P..`/`J..` |
| `dataset` | enum | `synthetic`, `real-dev`, `real-val`, `real-test`, `pilot` |
| `repo`, `commit` | string | frozen; synthetic uses `benchmark` + generator version hash |
| `file`, `line_start`, `line_end` | string, int, int | 1-based inclusive |
| `library` | enum | `pyca`, `pycryptodome` (others recorded as `out-of-scope:<name>`) |
| `algorithm` | enum | `RSA`, `EC`, `X25519`, `X448`, `Ed25519`, `Ed448`, `DH`, `DSA`, `ML-KEM`, `ML-DSA`, `other` |
| `api_call`, `method`, `arguments` | string | normalised call text; arguments as `name=value;` list |
| `key_provenance` | enum | `role_taxonomy.md` Sec. 5 |
| `ultimate_provenance` | list | optional resolved set for `attribute`/`parameter` |
| `gt_role` | enum | `SIGN`,`VERIFY`,`KEY_ESTABLISHMENT`,`PK_ENCRYPT`,`PK_DECRYPT`,`KEY_MATERIAL_ONLY`,`PROTOCOL_CONFIG`,`UNKNOWN`,`NONE` (ineligible) |
| `secondary_roles` | list | same-family alternatives |
| `possible_roles` | list | required when `gt_role = UNKNOWN` |
| `assessability` | enum | `DETERMINATE`, `INDETERMINATE` |
| `eligible` | bool | recommendation scoring applies |
| `hybrid_component` | bool | |
| `scope` | enum | `app`, `test`, `vendored`, `example` |
| `obvious_from_name` | bool | |
| `evidence_needed` | enum | `none`, `argument-resolution`, `downstream-usage`, `protocol-context`, `runtime-value` |
| `evidence_scope` | enum | `call`, `function`, `cross-function`, `cross-module`, `runtime-value` |
| `base_case`, `transformation` | string | synthetic only: base id and operator (`alias-import`, `wrapper-function`, `class-method`, `loaded-key`, `cross-function`, `dict-dispatch`, `identity`) |
| (annotation records) | — | v1.1: labels are not fields of this record. Each label is an envelope `{"site": <this record>, "meta": {...}}` (meta schema `docs/benchmark/meta_schema.json`; annotation guide Sec. 5), kept in the git-ignored work tree `benchmark/annotation/<phase>/<repo>/` (`primary_*`, `ai_review_*`, `adjudication_*`, `final_*`), with a hash-chained ledger `benchmark/ledger/<phase>/ledger_<repo>.jsonl` (hashes only). `meta.annotator` is `owner` or `ai_review`; `meta.label_kind` is `primary`, `packet_first`, `relabel`, `final` or `ai_review`. Single-investigator design: there is no second human annotator. |
| `notes` | string | |

Variants sharing a `base_case` are correlated; statistics cluster on `base_case` (synthetic) and `repo` (real).

## 2. Tool result record (`results/<tool>/<dataset>.jsonl`, one per site × tool)

| Field | Values |
|---|---|
| `tool`, `tool_version`, `tool_commit`, `run_id` | pinned |
| `tool_action` | `RECOMMEND`, `FLAG_NO_TARGET`, `ABSTAIN`, `NO_FINDING`, `EXECUTION_FAILURE` |
| `raw_findings` | list of the tool's own records matched to the site (file/line window) |
| `rec_class` | `SIG`, `KEM`, `DUAL`, `PQC_ALREADY`, `NONE` |
| `rec_text` | verbatim tool text |
| `dropin_wording` | bool |
| `predicted_role`, `evidence_tier`, `abstain_reason` | our analyzer only; tier ∈ {T0,T1,T2,T3} |
| `judgment` | `CORRECT`, `INCORRECT`, `UNDECIDED`, `UNJUSTIFIED`, `UNASSESSABLE`, `MISSED`, `DETECTED_ONLY`, `FALSE_POSITIVE_SITE`, `N/A` |
| `harm_category` | `ROLE_INCOMPATIBLE`, `FALSE_ASSURANCE`, `OVER_RECOMMENDATION`, `UNSUPPORTED_DROP_IN`, `OTHER`, empty |

`EXECUTION_FAILURE` (tool crashed/timed out on the file) is recorded per file and is never counted as `MISSED`.

## 3. Evidence tiers (Module C output)

| Tier | Definition |
|---|---|
| `T0` | No meaningful evidence: candidate matched by name only, receiver and arguments unresolved. |
| `T1` | API/method evidence only: the call is a known operation or key API of a supported library; receiver type or provenance unknown. |
| `T2` | Resolved operation arguments and receiver/key evidence: receiver resolved to a public-key object of known algorithm; padding/hash/curve resolved; or key API with resolved provenance. |
| `T3` | T2 plus provenance and downstream-usage evidence that are mutually consistent (e.g. generated key reaches only `exchange` consumers). Conflicting evidence drops the tier to T1 and records the conflict. |

Tiers are ordinal; no numeric confidence is derived from them.

## 4. Metrics (Module F)

- Recommendation correctness = CORRECT / (eligible DETERMINATE sites with RECOMMEND).
- Harmful rate = INCORRECT / n_exec, where n_exec = eligible sites where the method ran (scoring policy Sec. 5; denominator stated with every figure).
- Coverage = (RECOMMEND) / n_exec; abstention rate = ABSTAIN / n_exec.
- End-to-end correct per eligible site = CORRECT / n_exec.
- Undecided rate, unjustified rate, missed rate, detected-only rate: each / n_exec. Execution failures are reported in their own column per method (scoring policy Sec. 5).
- Detection precision/recall at site level (any finding within the window) against eligible + ineligible sites.
- Role macro-F1 and confusion matrix (our analyzer and the method-only / method+args baselines).
- Provenance-edge precision/recall against `ultimate_provenance`.
- Risk–coverage curve: risk = harmful / recommended at each tier threshold; AURC by trapezoid; bootstrap CI clustered by repo / base_case.

## 5. File layout (Phase 2 onward)

```
benchmark/
  schema/benchmark_schema.json
  synthetic/cases/<base>/<variant>.py  + manifest.jsonl
  real/manifest.json (repos, commits, split)
  candidates/<split>/order_<repo>.json  (location-only seeded orders; v1.1)
  annotation/<phase>/<repo>/  (git-ignored labelling work tree; v1.1)
  ledger/<phase>/ledger_<repo>.jsonl  (hash-chained, hashes only; v1.1)
results/<tool>/<dataset>.jsonl
reports/figures/*.png, tables/*.md
```

## Changelog

- v1.0 (2026-11-12): initial dictionary.
- v1.1 (2026-11-18, before any labelling and any test-split access; owner-approved pre-F1 decision register `docs/audit/owner_decision_register_v1.0.5.md`): the obsolete two-annotator fields are replaced by the single-investigator record envelope, work tree and ledger (F13); rate denominators stated as n_exec, as in the frozen scoring policy (F13). No field of `benchmark_schema.json` changed. The v1.0 text is kept in `docs/specification/archive/v1.0.4/data_dictionary.md`.
