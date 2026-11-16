# What the scanner actually reported, and why

Everything quoted here is from the files in `outputs/`, produced on 2026-11-16 by the commands in
`commands.md` (environment in `outputs/RUN_LOG.md`). The fixture is synthetic, so this shows **how pqscan
behaves**, not how accurate it is on real projects (that is Phase 3, which has no results yet).

## 1. Default scan (`outputs/01_summary.txt`)

```
pqscan 0.1.0.dev0 | policy 1.1 | threshold T2 | arm full
files scanned: 7, skipped: 0, execution failures: 0, semgrep: ok
sites: 23 (ABSTAIN=2, FLAG_NO_TARGET=1, RECOMMEND=20); excluded non-PK sites: 2; unsupported-library imports: 0 (none)
target classes: ABSTAIN=2, INVENTORY=1, KEM=6, KEM_DEM=6, SIG=8
```

23 role-bearing sites: **8 → ML-DSA (SIG)**, **6 → ML-KEM (KEM)**, **6 → ML-KEM-based KEM+KDF+AEAD redesign
(KEM_DEM)**, **1 inventory**, **2 abstentions**. Two further sites were *excluded* (not public-key
recommendation sites, see §1.6). Semgrep matched 25 times (`outputs/08_semgrep_raw.json`); every match
joined to a Module B site, so `semgrep_only` is empty in `02_scan.json`.

The ML-KEM vs ML-DSA choice is made from the **role**, never from the algorithm name. RSA appears on both
sides, and so does elliptic-curve cryptography:

| Algorithm | Role found | Target | Sites |
|---|---|---|---|
| RSA | SIGN / VERIFY | ML-DSA | `signing_service.py:9,11,13`, `legacy_pycryptodome.py:11,13`, `ambiguous.py:21` |
| RSA | PK_ENCRYPT / PK_DECRYPT | ML-KEM KEM+KDF+AEAD | `envelope.py:9,11,12`, `legacy_pycryptodome.py:17,19`, `ambiguous.py:22` |
| EC (P-256) | SIGN | ML-DSA | `ecdsa_tokens.py:9,10` |
| EC (P-384) | KEY_ESTABLISHMENT | ML-KEM | `key_agreement.py:14,15,16` |
| X25519 | KEY_ESTABLISHMENT | ML-KEM | `key_agreement.py:8,9,10` |

A tool that maps "RSA → ML-KEM, EC → ML-DSA" (the common algorithm-family convention, baseline B1 in the
Phase 2 report) would give the wrong family for RSA signing and for ECDH here.

### 1.1 Signatures → ML-DSA (`signing_service.py`, `ecdsa_tokens.py`, `legacy_pycryptodome.py:11,13`)

Example, `signing_service.py:11` (from `02_scan.json`):

- reason: `operation .sign() -> SIGN; receiver resolved: pyca:RSA:private:generated; arguments: padding=PSS, hash=SHA256`
- tier **T3**: receiver is a typed key object *and* there is an algorithm-specific argument (`PSS`) *and*
  the key's origin is concrete (`rsa.generate_private_key` at line 9).
- recommendation: `RECOMMEND SIG`, parameter set `ML-DSA-65 (category 3) by default; …`. The rationale cites
  NIST IR 8547 Table 2 (RSA signing deprecated after 2030, disallowed after 2035).

The key-generation line 9 is itself a site: its key reaches only signature consumers (`.sign()` line 11,
`.verify()` line 13), so it is `SIGN` (secondary role `VERIFY`) at T3. The verification at line 13 is
`VERIFY` → SIG with the "add ML-DSA verification; keep legacy verification only for already-issued
signatures" rationale.

PyCryptodome is handled the same way: `legacy_pycryptodome.py:13` (`pkcs1_15.new(key).sign(digest)`) has
receiver `pcd:signer:pkcs1_15(pycryptodome:RSA:private:generated)` and argument `padding=pkcs1_15` → SIGN,
T3, ML-DSA.

### 1.2 Key establishment → ML-KEM (`key_agreement.py`)

- `key_agreement.py:10` (`ours.exchange(theirs.public_key())`): `operation .exchange() -> KEY_ESTABLISHMENT;
  receiver resolved: pyca:X25519:private:generated` → T3, `RECOMMEND KEM`, `ML-KEM-768`. X25519 is a
  single-purpose algorithm, so it counts as the algorithm-specific evidence even with no padding argument.
- `key_agreement.py:16` (ECDH): receiver `pyca:EC:private:generated`, argument `ECDH` → T3, KEM.
- The four key-generation lines (8, 9, 14, 15) reach only key-establishment consumers — the peer keys are
  traced as `consumer peer key of .exchange()` — so they are KEY_ESTABLISHMENT at T3 as well.
- The rationale says ML-KEM uses encapsulate/decapsulate, "not a symmetric exchange(peer) call": the
  recommendation is a redesign, and a PQ/T hybrid via an approved combiner is named as a transitional option.

### 1.3 RSA encryption → KEM + KDF + AEAD, never a drop-in (`envelope.py`, `legacy_pycryptodome.py:17,19`)

- `envelope.py:11` (`recipient_key.public_key().encrypt(content_key, oaep)`): `PK_ENCRYPT`, receiver
  `pyca:RSA:public:generated`, `padding=OAEP`, T3 → `RECOMMEND KEM_DEM`, `ML-KEM-768 … with an approved KDF
  and AEAD`. The rationale states that "the existing encrypt(data) call shape cannot be preserved".
- `envelope.py:12` (`decrypt`) is the decapsulation side of the same redesign.
- KEM_DEM is in the **KEM family**, so RSA encryption is steered towards ML-KEM, never ML-DSA.

### 1.4 Inventory only (`key_inventory.py:10`)

`key material (RSA) with no consumer inside the analysed scope and no escape: inventory only` →
`KEY_MATERIAL_ONLY`, T2, `FLAG_NO_TARGET INVENTORY`: "No target is recommended; determine the downstream role
first." The key is only generated and its public half serialised; the scanner reports it but refuses to
guess a role. (Serialising with `public_bytes` is not counted as a consumer or an escape by the
bounded analysis, so this site is T2 rather than an abstention.)

### 1.5 Abstentions that the scanner really produced (`ambiguous.py`)

Two sites abstain under the default policy. Both reasons are generated by the tool:

1. **`ambiguous.py:15` — `key.sign(data)` on an untyped parameter → tier T0 → ABSTAIN.**
   Reason: `operation .sign() -> SIGN; receiver unresolved (untyped parameter); arguments: no parameters`.
   Rationale: "Evidence tier T0 is below the policy threshold T2: the receiver is not resolved to a key
   object and no algorithm-specific argument is visible. Inferred role (not acted on): SIGN."
   The method name says "sign", but `key` might be an HMAC object or anything else, so no target is given.
   In the CBOM this component is named `RSA-or-ECC (algorithm not statically resolved)`.

2. **`ambiguous.py:19` — one RSA key reaching two role families → role UNKNOWN → ABSTAIN.**
   Reason: `key material (RSA) reaches consumers of 2 families (PKE, SIG); the role depends on which path
   runs, so it is not statically determinable`. Possible roles listed: `PK_DECRYPT, SIGN, VERIFY`. "No single
   target is justified."

The two *operations* that use that key (`ambiguous.py:21` `.sign(…PKCS1v15…)` and `:22`
`.decrypt(…OAEP…)`) are themselves unambiguous, so they still get SIG and KEM_DEM respectively — but at
**T2, not T3**. Their reason ends with "…its origin is consumed by another role family or has conflicting
consumers, so the tier is capped at T2". This is the evidence-tier design working: provenance that is
inconsistent with downstream use lowers confidence even when the local call looks clear.

### 1.6 Excluded sites (`02_scan.json`, `excluded`)

- `legacy_pycryptodome.py:13` `signer-object`: "PyCryptodome signer object; the recommendation is attached to
  its sign/verify call".
- `legacy_pycryptodome.py:18` `cipher-object`: "PyCryptodome cipher object; the recommendation is attached to
  its encrypt/decrypt call".

These are not dropped silently; they are recorded with the reason, and the recommendation sits on the
operation (`:13` sign, `:19` encrypt).

### 1.7 Observations to mention honestly

These are real behaviours visible in the output. They do not change any target family, but a careful
audience may notice them:

- **`legacy_pycryptodome.py:17` is labelled `PK_DECRYPT`** although, in this file, the generated key is only
  used for encryption (through `key.publickey()` and `PKCS1_OAEP.new(...)` at line 18). In
  `roles/classifier.py` (`_key_material_role`), the consumer here is the constructor call
  `PKCS1_OAEP.new(key)`, not a `.encrypt()` method on the key, so the rule falls back on the key being
  private and picks the decryption side. Both PK_ENCRYPT and PK_DECRYPT map to KEM_DEM, so
  the recommendation is the same; the role label at the key-generation line is arguably imprecise.
- **Rationale wording for EC sites** reads "ECDSA/ECDH (elliptic-curve) signing …" for the ECDSA sites and
  "ECDSA/ECDH (elliptic-curve) key establishment …" for the ECDH sites: the policy template names the
  algorithm family, not the specific scheme. The CBOM component names are specific (`ECDSA`, `ECDH`).

## 2. Tier threshold T3 (`outputs/05_summary_threshold_T3.txt`)

```
sites: 23 (ABSTAIN=5, RECOMMEND=18); …
```

Exactly the three T2 sites change to ABSTAIN: `ambiguous.py:21` (SIGN), `ambiguous.py:22` (PK_DECRYPT) and
`key_inventory.py:10` (KEY_MATERIAL_ONLY). Every T3 site keeps its recommendation. The threshold is a single
policy knob that trades coverage for evidence strength, and the decision for each site is predictable
from its tier.

## 3. Ablation arm `method-only` (`outputs/06_summary_arm_method-only.txt`)

```
sites: 23 (ABSTAIN=23); …
```

With only the method name as evidence, operations drop to T0 and key-material sites become UNKNOWN (T1) —
except X25519 key generation, which stays KEY_ESTABLISHMENT because X25519 is single-purpose, but only at
T1. At the default threshold T2, **all 23 sites abstain**. This shows (on a synthetic fixture only) that
the receiver typing, arguments and provenance are what allow pqscan to make a recommendation; whether this
holds on real code is a Phase 3 question.

## 4. No Semgrep (`outputs/07_summary_no-semgrep.txt`)

Identical sites, roles, tiers and actions; the status line says `semgrep: not-run`. Module B discovers sites
from the AST itself; Semgrep (Module A) is the required detector whose rule ids are joined to the sites
(`semgrep_rules` in the JSON, `pqscan:semgrepRule` in the CBOM). This is the fallback if Semgrep fails on
demo day.

## 5. Exports

- **CBOM** (`outputs/03_cbom.json`): CycloneDX 1.6, 23 `cryptographic-asset` components, 11 dependency
  entries linking operation components to the key-material components their receiver was traced to (e.g.
  `ambiguous.py:21` and `:22` depend on `ambiguous.py:19`). Operations are `assetType: algorithm` (e.g.
  `envelope.py:11`: `primitive: pke`, `cryptoFunctions: [encrypt]`, `padding: oaep`); keys are
  `related-crypto-material` (e.g. `envelope.py:9`: `private-key`, size 3072). Role, tier, action, target,
  rationale and evidence are `pqscan:*` properties. Validated against the schema before writing;
  byte-identical on a second run.
- **SARIF** (`outputs/04_scan.sarif`): 23 results — 20 `warning` (RECOMMEND) and 3 `note` (2 ABSTAIN,
  1 FLAG_NO_TARGET); rule ids such as `pqscan/recommend/sign`, `pqscan/abstain/unknown`;
  `executionSuccessful: true`.
- **JSON** (`outputs/02_scan.json`): the full evidence trail per site (receiver, arguments, consumers,
  provenance, tier reason, recommendation), plus `excluded`, `semgrep_only`, `unsupported`,
  `execution_failures` and `files_skipped` (all empty except `excluded` here).
- None of the pqscan exports contain the source lines (`snippet` does not appear in 02/03/04).

## 6. What was *not* demonstrated (the fixture does not exercise it)

- PQ/T hybrids (`NO_ACTION_HYBRID`): the fixture uses no ML-KEM/ML-DSA, so no hybrid is reported.
- Unsupported libraries (python-rsa, `ssl`, paramiko, …): none imported, so `unsupported` is empty.
- Execution failures (unparsable/timed-out files) and skipped files: none occurred.
- Tier T1 under the full arm: no T1 site arose under the default arm in this fixture.

## 7. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `pqscan : The term 'pqscan' is not recognized…` | venv not activated. Run `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\Activate.ps1`, or call `& $env:USERPROFILE\.venvs\pqscan-demo\Scripts\pqscan.exe` directly. |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (this window only), or skip activation and use full paths. |
| Summary shows `semgrep: failed: semgrep executable not found; install semgrep==1.185.0 in the environment` (message text from `pqscan/detect/runner.py`; this failure did not occur in the recorded run) | Semgrep is not in the venv's `Scripts` folder or on `PATH`. Re-run `python -m pip install -e .` in the venv; check with `semgrep --version`. The scan still completes (Module B), as with `--no-semgrep`. |
| Summary shows `semgrep: failed: semgrep failed (exit …): …` (also from the code, not observed) | Semgrep started but errored, e.g. a broken install. Run `semgrep --version` to see the error; use `--no-semgrep` to continue the demo. |
| `semgrep --version` is slow (several seconds) | Normal: Semgrep's start-up took ~3–5 s per call on the run machine. Each `pqscan scan` call runs Semgrep once. |
| A different Semgrep version is found | `pqscan` prefers the `semgrep.exe` next to the running Python (the venv), then `PATH`. Use the venv's pqscan. Version 1.185.0 is pinned. |
| `UnicodeEncodeError` / garbled characters in the console | Set `$env:PYTHONIOENCODING = "utf-8"` (the recorded run did). Console code page can also be set with `chcp 65001`. |
| JSON file "invalid" after redirecting with `>` in Windows PowerShell 5.1 | `>` may write UTF-16. Use `-o file.json` (pqscan writes UTF-8) or `| Out-File -Encoding utf8`. |
| `error: not a directory: …`, exit code 2 | Wrong path; run from the repository root, or give an absolute path to `docs\demo\demo_repo`. |
| `py -3.12` not found | Install Python 3.12 (pqscan requires ≥ 3.12); the `py` launcher lists installed versions with `py -0`. |
| Rule ids in `08_semgrep_raw.json` have a long dotted prefix | Semgrep prefixes `check_id` with the dotted path of the rules folder; pqscan strips it. Expected. |
| `"lines": "requires login"` in raw Semgrep JSON | Semgrep CE behaviour without login; harmless. |
| Scan seems to hang | Each file has a 30 s analysis limit (`--file-timeout`); a stuck file is killed and recorded as an execution failure. On the 7-file fixture a scan took 3–5 s. |
| Antivirus pop-up on first `semgrep.exe` run | Windows Defender may scan the new executable once; allow it and retry. |
