# Annotation guide v1.1, revision 4 — PROPOSED, NOT ADOPTED (guide v1.0 remains in force)

Base: revision 3 (`../rev3/R3_09_annotation_guide_v1.1_rev3_PROPOSED.md`). Every rule there applies, with the following changes.

1. **`context_used`, decided before the AI review is requested (Sec. 2 of revision 3, step 2).** Set it while labelling. Its value cannot be changed after the primary file is hashed.
   - `packet_sufficient`: every one of the 8 fields was decided from lines inside the packet the packet builder generates for this candidate (open the packet file, not only the repository).
   - `extended`: anything else. List every extra file:line range in `meta.context_extra`.
2. **Packet-first subset.** For candidates the script flags `packet_first = true` (a seeded 10% per phase, at least 50):
   - First record a P-label from the packet only, in `primary_packet_<repo>_B<n>.jsonl`, which is validated, hashed and pushed.
   - Then record the normal primary label (the F-label), which may use more context.
   - Never edit the P-label afterwards.
3. **Reliability re-label.** The script presents the re-label sample (per phase n = max(50, 10%)) in a new order, no earlier than 14 days after the latest primary label in the sample. Earlier labels must not be consulted.
4. **What the labels feed.** Owner-final labels define eligibility, the expected class (`eligible`, `gt_role`, `assessability`, `hybrid_component`) and H1a (`obvious_from_name`, `evidence_needed`). Tool outputs, tiers and coverage matching are never consulted while labelling.
5. **Reporting language** is unchanged: "single-investigator labels with a separately conducted AI-assisted review and investigator adjudication".
