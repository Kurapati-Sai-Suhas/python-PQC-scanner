# Paper figures (content-first; template styling pending)

These are vector figures (SVG and PDF; text kept as text) produced by `make_figures.py`. The PNG files are previews only.

- They are **not** styled to an IEEE template. Restyle after the owner provides the sample paper (`author_decisions.md` D1).
- They are byte-identical across rebuilds (no embedded timestamps).

```bash
.venv/Scripts/python docs/paper/figures/make_figures.py
```

| Figure | Files | Content source | What it must not imply |
|---|---|---|---|
| Fig. 1 Architecture | `fig1_architecture.{svg,pdf}` | `pqscan/` package layout; tracing bound from `pqscan/semantic/consumers.py` (`MAX_CALL_DEPTH = 2`) | That F–G run during a scan (they are drawn in a separate, dashed group) |
| Fig. 2 Role and tier flow | `fig2_role_tier_flow.{svg,pdf}` | `pqscan/roles/classifier.py` (docstring and rules), `pqscan/policy/engine.py` (order: UNKNOWN → tier → hybrid → class), `policy_v1_1.yaml` | That PROTOCOL_CONFIG is detected (the footnote states it is not) |
| Fig. 3 Protocol timeline | `fig3_protocol_timeline.{svg,pdf}` | protocol v1.0.4 stage sequence; `owner_action_checklist.md` | Any result. Step 12 is marked NOT AVAILABLE. |
| Fig. 4 Calibration | `fig4_calibration.{svg,pdf}` | Parsed directly from `docs/implementation/acceptance/statistical_acceptance.md` (26 Type I cells, 8 FWER configurations, 3 two-stratum configurations; the script asserts the counts) | Scanner accuracy. The title says "SIMULATION under the assumed planning model — not evidence of scanner accuracy"; S16 is shown greyed and labelled "not calibrated, not claimed". |

**Style:**
- one hue (blue `#2a78d6`) for data and completed items, neutral greys for reference lines, pending items and notes;
- status in Fig. 3 is encoded by marker shape and text label, not by color alone;
- one axis per panel; nominal levels drawn as dashed reference lines; ± 3 Monte Carlo SE shown, as in the acceptance criterion.
