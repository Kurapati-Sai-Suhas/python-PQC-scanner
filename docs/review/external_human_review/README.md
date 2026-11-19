# External human review of the specification (protocol v1.0.5-r4): request and instructions

**Status: PENDING.** No human reviewer has been engaged, and no review has taken place. This folder is the handoff. It becomes evidence only when a named person outside the build team completes `feedback_form.md`.

The three earlier reviews (two isolated ChatGPT reviews and the third review by fresh-context AI agents) are **AI reviews**. They do not satisfy this requirement. Protocol Stage F1, item 9, says: "a review of the full specification by a human reviewer outside the build team… the AI specification review does not replace it, and the F1 record cannot be made without it" (F14).

## Who may review

- Not a member of the build team (the seven listed authors are the build team).
- Background in Python and basic public-key cryptography (signatures, key establishment, encryption), with an interest in empirical study design.
- A faculty member or an external researcher, for example via the lecturer request in `../lecturer_request.md`.
- Registers in `../review_register.md` before starting: name or supervisor-held pseudonymous ID, one-line background, conflict of interest, date.

## What to send the reviewer (draft request; edit before sending)

> Subject: Request for an independent specification review: pre-registered evaluation of a Python post-quantum migration scanner
>
> Dear [name],
>
> Our team has built pqscan, a static analyser that gives post-quantum migration guidance for Python code, and has specified, before any data labelling, how we will evaluate it. Our protocol requires one review of this specification by someone outside the team before we freeze it and open the held-out test repositories. AI reviews have been done, but they cannot replace a human review.
>
> We would be grateful if you could read the documents listed in `evidence_index.md` (repository: https://github.com/Kurapati-Sai-Suhas/python-PQC-scanner, commit 1cdc2d7) and answer the questions in `questions.md` using `feedback_form.md`. We estimate 4–6 hours. No results exist yet, so you would be reviewing the plan, not findings.
>
> Thank you,
> [name]

## Procedure

1. The reviewer copies `feedback_form.md` to `../forms/completed/external_spec_review_<reviewer-id>_<YYYY-MM-DD>.md` and answers every question. "No issue" is a valid answer; a blank is not.
2. The verdict is APPROVED, APPROVED WITH CHANGES (each listed) or CHANGES REQUIRED.
3. The build team answers each requested change in the same file. A change to an adopted document goes through a recorded revision (new adoption record; pre-change text archived).
4. The reviewer signs off the responses. Name or ID, date and verdict go into `../review_register.md`, in the reviewer's own entry.
5. Only then can the F1 record cite this review (`scripts/f1_readiness.py` checks for the completed form and the register row).

Nobody may record a review on another person's behalf. An AI tool must not draft the reviewer's answers.
