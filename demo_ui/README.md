# PQScan demo UI

A local web page for demonstrating PQScan step by step. Every scan runs the real `pqscan` CLI on this computer; nothing is pre-recorded.

```powershell
.venv\Scripts\python demo_ui\server.py
```

Then open **http://127.0.0.1:8765** in a browser. Stop the server with Ctrl + C in its window. To use another port, run `$env:PQSCAN_UI_PORT=8766` first.

## The 8 steps on the page

1. What it does.
2. Choose code.
3. Run the scan (threshold, ablation arm, skip tests).
4. Overview: counts, actions, classes, roles, tiers and abstention reasons.
5. Findings table, with filters.
6. Explain one finding: the source line, a plain-English decision, and the evidence each module (A–E) contributed.
7. Exports: CBOM, SARIF and JSON, each validated against its official schema and downloadable.
8. Limits.

## Inputs (a fixed list)

| Input | Type |
|---|---|
| The demo project `docs/demo/demo_repo` | synthetic |
| The PQ/T combination example (generated from `docs/audit/e2e/make_fixtures.py`) | synthetic |
| The installed pyca/cryptography | real library source, read in place |
| The installed PyCryptodome | real library source, read in place |

The sealed benchmark repositories are never used.

## Safety

- The server listens on 127.0.0.1 only.
- The browser cannot choose arbitrary paths.
- The source viewer only reads files inside the selected input.
- The server uses the Python standard library only, plus pqscan's own dependencies for schema validation.

Counts shown are what pqscan reported, not accuracy (no labels exist for these inputs).
