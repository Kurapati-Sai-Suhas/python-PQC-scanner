# Data dictionary (v1.0)

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
| `annotator_1`, `annotator_2`, `adjudicated` | string / bool | labels per annotator kept in `labels/` with the same site_id |
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
- Harmful rate = INCORRECT / eligible sites (denominator stated with every figure).
- Coverage = (RECOMMEND) / eligible sites; abstention rate = ABSTAIN / eligible sites.
- End-to-end correct per eligible site = CORRECT / eligible sites.
- Undecided rate, unjustified rate, missed rate, detected-only rate: each / eligible sites.
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
  labels/<annotator>/*.jsonl, adjudicated.jsonl
results/<tool>/<dataset>.jsonl
reports/figures/*.png, tables/*.md
```
