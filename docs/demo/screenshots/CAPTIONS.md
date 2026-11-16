# Screenshot captions

**These PNGs are rendered images, not live screen captures.** Each was drawn by
`render_screenshots.py` (Pillow 11.3.0, Consolas font, run 2026-11-16) from a text file that was captured
verbatim when the commands in `../commands.md` were run (see `../outputs/RUN_LOG.md`). The text is copied
unchanged; the only additions are a header line naming the command and a footer naming the source file.
The colours (green RECOMMEND, yellow ABSTAIN, cyan FLAG_NO_TARGET) are added by the renderer; pqscan's own
output is plain text.

| Image | Source file | Command | What it shows |
|---|---|---|---|
| `01_versions.png` | `../outputs/raw_run_transcript.txt`, lines 1–26 (lines over 120 characters wrapped) | `python --version`, `pqscan --version`, `semgrep --version`, package path and versions | Python 3.12.10, pqscan 0.1.0.dev0 (imported from the `phase2-complete` snapshot), Semgrep 1.185.0 |
| `02_summary_default.png` | `../outputs/01_summary.txt` | `pqscan scan docs/demo/demo_repo` | 23 sites: 20 RECOMMEND (SIG 8, KEM 6, KEM_DEM 6), 1 INVENTORY, 2 ABSTAIN |
| `03_summary_threshold_T3.png` | `../outputs/05_summary_threshold_T3.txt` | `pqscan scan docs/demo/demo_repo --tier-threshold T3` | the three T2 sites become ABSTAIN; 18 RECOMMEND, 5 ABSTAIN |
| `04_summary_arm_method-only.png` | `../outputs/06_summary_arm_method-only.txt` | `pqscan scan docs/demo/demo_repo --arm method-only` | method name alone: all 23 sites abstain |

To regenerate: `py -3.12 docs\demo\screenshots\render_screenshots.py` (needs Pillow).

If you prefer genuine screen captures for the slides, run the same commands live in Windows Terminal
(see `../commands.md`, sections 0, 1, 5 and 6) and capture with `Win+Shift+S`. Name them differently (e.g.
`live_*.png`) so rendered and captured images are never confused.
