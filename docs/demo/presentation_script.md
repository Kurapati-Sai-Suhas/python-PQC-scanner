# Presentation script (target 10 minutes; fits 8–12)

Speaker: project owner. Audience: lecturer. Live terminal open at the repository root with the demo venv
activated (see `checklist.md`). Backup: `screenshots/` and `outputs/`.

Base paper (cite on slide 1 and when introducing the problem): Lei Zhang, "Toward Quantum-Safe Software
Engineering: A Vision for Post-Quantum Cryptography Migration", ICSE-Companion '26, pp. 402–403,
DOI 10.1145/3774748.3795653.

| Time | Section | Show |
|---|---|---|
| 0:00–1:30 | 1. Problem | slide |
| 1:30–3:00 | 2. Why role-aware recommendations | slide with the RSA/EC table |
| 3:00–4:30 | 3. Architecture | `architecture.md` diagram |
| 4:30–8:00 | 4. Live demo (incl. abstention) | terminal |
| 8:00–9:00 | 5. Limitations | slide |
| 9:00–10:00 | 6. What Phase 3 will add; questions | slide |

---

## 1. Problem (0:00–1:30)

> "RSA and elliptic-curve cryptography — RSA signatures, ECDSA, ECDH, X25519 — are broken by a large enough
> quantum computer running Shor's algorithm. NIST has standardised replacements: ML-KEM in FIPS 203 for key
> establishment, and ML-DSA in FIPS 204 for signatures. NIST IR 8547 deprecates the classical algorithms
> after 2030 and disallows them after 2035. Key exchange is urgent because of harvest-now-decrypt-later:
> traffic recorded today can be decrypted later.
>
> Zhang's ICSE-Companion 2026 vision paper argues that migration is a software-engineering problem, and its
> first pillar is PQC-aware detection that understands the protocol role of each use and produces an
> enriched inventory. My project implements part of that first pillar for Python projects. It does not do
> automatic refactoring or verification — those are the paper's other pillars."

## 2. Why role-aware recommendations matter (1:30–3:00)

> "The replacement depends on what the key is *used for*, not on which algorithm it is. RSA can sign — that
> needs ML-DSA — or it can encrypt a session key — that needs an ML-KEM-based redesign. Elliptic curves can
> sign with ECDSA — ML-DSA — or agree a key with ECDH — ML-KEM. A scanner that maps 'RSA → ML-KEM, EC →
> ML-DSA' gives the wrong family half the time.
>
> And RSA encryption has no drop-in replacement: ML-KEM encapsulates, it does not encrypt arbitrary data.
> So for RSA encryption we recommend a KEM plus KDF plus AEAD redesign, and we say explicitly that the call
> shape cannot be preserved.
>
> Finally, a static tool sometimes cannot know the role. Then the honest answer is 'I don't know, and here
> is why' — abstention — rather than a confident wrong recommendation."

Slide: the table in `expected_outputs.md` §1 (RSA and EC each appear with both targets).

## 3. Architecture (3:00–4:30)

Show the diagram in `architecture.md`.

> "The scanner never imports or runs the code. Module A is Semgrep with 28 rules for PyCA cryptography and
> PyCryptodome. Module B parses the code with Python's `ast` and collects evidence for each site: is the
> receiver really a key object, which algorithm, which padding or curve argument, where the key came from,
> and where it goes.
>
> Module C turns that evidence into a role and an evidence tier, T0 to T3. T0 means we only have a method
> name; T3 means typed receiver, algorithm-specific arguments and a concrete key origin, with no conflict.
> Tiers are ordinal labels, not probabilities.
>
> Module D is a versioned policy file. Signatures map to ML-DSA, key establishment to ML-KEM, RSA
> encryption to KEM+KDF+AEAD. If the role is UNKNOWN, or the tier is below a threshold — T2 by default —
> it abstains. The engine refuses to load a policy that would map a signature to a KEM or vice versa.
>
> Module E exports a CycloneDX 1.6 CBOM, SARIF for code-scanning tools, and full JSON."

## 4. Live demo (4:30–8:00)

Commands are in `commands.md`. Expected results in `expected_outputs.md`.

**4a. Show the fixture (20 s).** Open `docs/demo/demo_repo/README.md`.

> "This is a small synthetic project I wrote for this demo — it's labelled as such in every file. It is
> never executed; it's only scanned."

**4b. Versions (10 s).**

```powershell
pqscan --version
semgrep --version
```

**4c. Default scan (90 s).**

```powershell
pqscan scan docs\demo\demo_repo
```

> "Twenty-three sites. Look at RSA: `signing_service.py` lines 9–13 get SIG, that is ML-DSA, and
> `envelope.py` gets KEM_DEM, the ML-KEM redesign. Same algorithm, different targets, because the roles
> differ. Elliptic curves likewise: `ecdsa_tokens.py` → SIG, `key_agreement.py` ECDH → KEM. X25519 → KEM.
> `key_inventory.py` has a key that is generated but never used — the tool reports it as inventory and
> refuses to guess its role."

**4d. Abstention (60 s).** Point at the two `ambiguous.py` ABSTAIN lines.

> "Line 15 calls `key.sign(data)` on an untyped parameter. The method says 'sign', but `key` could be an
> HMAC object. Tier T0, so it abstains, and it says what evidence is missing. Line 19 is one RSA key that
> reaches a signature on one branch and a decryption on the other. Its role is UNKNOWN; the tool lists the
> possible roles and gives no target. The two operations on that key still get recommendations, but only
> at T2, because the key's origin is shared with another role family."

Optional: open `outputs/02_scan.json` and search for `ambiguous.py` to show the full reason text.

**4e. Threshold (30 s).**

```powershell
pqscan scan docs\demo\demo_repo --tier-threshold T3
```

> "Raise the threshold to T3 and exactly the three T2 sites switch to ABSTAIN. One policy knob trades
> coverage for evidence strength."

**4f. Exports (20 s).**

```powershell
pqscan scan docs\demo\demo_repo --format cbom -o $env:TEMP\bom.json
```

> "The CBOM is CycloneDX 1.6, validated against the schema before it's written, and byte-identical across
> runs. Each site carries its role, tier, recommendation and evidence."

(Optional if time: `--arm method-only` → all 23 sites abstain: the method name alone is not enough evidence.)

**Fallback:** if anything fails live, switch to `screenshots/02_summary_default.png` and
`03_summary_threshold_T3.png` — and say that they are rendered from the captured run output.

## 5. Limitations (8:00–9:00)

> "Honest limits. The analysis is flow-insensitive and bounded to about two call levels; keys that leave
> through a public function count as an escape and lower the tier. Only PyCA cryptography and PyCryptodome
> are analysed; TLS or SSH protocol configuration is out of scope, and other libraries are only listed as
> unsupported. The hybrid detection is deliberately conservative. On this demo you can also see two small
> things: a key-generation line labelled 'decrypt' although the key is only used to encrypt — same target
> family, but the label is imprecise — and policy wording that says 'ECDSA/ECDH' generically.
>
> Most importantly: this fixture is synthetic. It shows the behaviour, not the accuracy. The recommendations
> are migration guidance; they do not prove that a migrated system is secure."

## 6. What Phase 3 will add (9:00–10:00)

> "Phase 2 — the system — is complete and tagged. Phase 3 is the evaluation, and it has no results yet. It
> will build an annotated benchmark of real call sites from development and held-out open-source Python
> projects, under a frozen protocol, and compare pqscan against existing PQC scanners and simple baselines,
> including the algorithm-family mapping, measuring correct, harmful, and abstained recommendations. The
> ablation arms you saw will measure how much each kind of evidence contributes. The held-out repositories
> are kept untouched until the evaluation freeze so the results are not tuned to them."

Close: "Thank you — questions?"

---

### Do not say

- Any accuracy, precision or "correct %" figure: none exists for Phase 3.
- That the demo results generalise to real code.
- That the screenshots are live captures (they are rendered from captured output).
- That pqscan makes code quantum-safe or compliant.
