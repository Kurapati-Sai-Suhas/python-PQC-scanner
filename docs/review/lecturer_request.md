# Draft message to the lecturer (edit before sending)

Subject: Post-quantum crypto scanner project: request for independent reviewers and annotators

Dear [Lecturer name],

Our project "Post-quantum crypto scanner for Python projects" (base paper: Zhang, ICSE-Companion '26, DOI 10.1145/3774748.3795653) has finished its implementation phase (tag `phase2-complete` on GitHub). The tooling for the evaluation phase is also ready. Before we can freeze the method and run the held-out evaluation, the protocol requires independent human review, which our team cannot do itself. Could you help us find:

1. **An external annotator** (outside our team): comfortable reading Python and with basic public-key cryptography (signatures vs. key exchange vs. encryption). Estimated 26–34 hours in total, in batches, plus about 3 hours for a synthetic validation sample.
2. **An adjudicator**, ideally you or another faculty member with a security background, to settle disagreements between annotators. Estimated 14–22 hours.
3. **A specification reviewer** (outside our team, security or cryptography background) to review three short documents (role taxonomy, recommendation policy, scoring policy) and blind-label 31 pilot sites. Estimated 5–7 hours.

All hour figures are estimates from stated assumptions. The procedure, forms and independence rules are in `docs/review/` in the repository.

We would also be grateful for your guidance on:
- the annotation sample size: our proposal is 30 eligible sites per held-out repository (210 in total) plus 150 development/validation sites;
- whether a CBOMkit inventory comparison is needed, given that it gives no migration advice;
- who owns the project's IP, and whether we may add an open-source licence (MIT or Apache-2.0) to the public repository.

Thank you,
[Name]
