"""Module C — deterministic cryptographic role inference with ordinal evidence tiers (T0–T3).

The classifier is a decision table over Module B evidence. It never produces probabilities.
Ablation arms (evaluation_protocol.md, Experiment B) restrict which evidence the table may use.
"""
from .classifier import RoleDecision, classify, ARMS  # noqa: F401
