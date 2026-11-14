"""pqscan — Post-quantum crypto scanner for Python projects (research prototype).

Pipeline: detect (Semgrep candidates) -> semantic (ast/symtable resolution) -> roles
(deterministic classifier with evidence tiers) -> policy (versioned role->target table
with abstention) -> export (CycloneDX 1.6 / SARIF / JSON). bench/ and baselines/ hold
the evaluation harness. Nothing here executes or imports scanned code.
"""
__version__ = "0.1.0.dev0"
