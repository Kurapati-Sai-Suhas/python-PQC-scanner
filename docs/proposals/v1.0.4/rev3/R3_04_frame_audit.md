# R3-04 Frame audit, redesigned (PROPOSED, revision 3) — descriptive, not confirmatory

**Question.** Within crypto-importing Python files of the 6 development and validation repositories at their pinned commits, what share of eligible sites (annotation guide v1.1) is absent from the candidate pool?

**Not asked, and not answerable here:**
- recall over all Python cryptographic usage;
- recall in files importing no supported library;
- recall in the test split;
- errors shared by the owner and the pool.

| Item | Specification |
|---|---|
| Sampling frame | every `.py` file in the 6 development/validation repositories at the pinned commits that imports pyca or PyCryptodome (the qualification and sampler regex), excluding nothing else. The frame list and its SHA-256 are recorded |
| File selection | per repository, a seeded random order of its frame files (seed `20261113:frame:<repo>`). Files are taken round-robin across repositories in a seeded repository order, one per repository per round. Stop once **≥ 60 eligible sites** have been audited **and** every repository has contributed **≥ 1 file**. The minimum is therefore 6 files from 6 repositories. Files with zero eligible sites are kept and count as audited |
| Identification | the owner reads the whole selected file, blind to the pool: no candidate markers, no tool output. Every eligible site (guide v1.1 Step A–E, evidence lines required) is recorded in the standard envelope with `meta.audit = true` |
| Matching | a script maps each audited site to its enclosing-statement start line and checks pool membership (same rule as the pool builder). It records `in_pool` and, if absent, the reason category: regex pattern not matched; file outside the regex domain; multi-line statement offset; other |
| AI review | not required. Optionally, the same files go through the ChatGPT review procedure, reported separately |
| Estimate | missed share = Σ absent / Σ audited eligible. The interval is a **file-level cluster bootstrap** (resampling files within repositories, 2,000 resamples, seed `20261113:frame`), and per-file counts are always shown. A Wilson interval is shown only alongside, labelled "assumes independent sites (not valid under clustering)" |
| Zero misses | reported as "0 of n audited sites in k files", with the rule-of-three bound 3/n given as a heuristic under independence only, not as a confidence statement |
| Status | **descriptive.** It informs the threats-to-validity section and the interpretation of "missed" counts. It is not a pre-registered hypothesis test, and it is never called a representative estimate of Python cryptographic usage |
