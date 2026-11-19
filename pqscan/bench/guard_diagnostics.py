"""Descriptive repository-gap diagnostics for the coverage-gap guard (analysis plan v1.0.1-r2 Sec. 7.2; second review G10).

The pre-specified guard (pqscan.bench.h2.coverage_gap / guard_active) uses the SIGNED, repository-balanced gap
g = (1/K_e) sum_r (R_F,r - R_M,r) / n_r. These diagnostics are reported next to it and NEVER change the guard, p or
any decision. They show what the signed average can hide: opposite-direction repositories (mean absolute gap) and the
repository where F's coverage advantage is smallest (minimum gap). This module is outside the E30 calibration closure.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Mapping, Sequence


def repository_gaps(results: Sequence[Mapping]) -> list[Fraction]:
    """(R_F,r - R_M,r) / n_r for every estimable repository (n_common >= 1), as exact fractions."""
    return [Fraction(int(r["R_f"]) - int(r["R_m"]), int(r["n_common"])) for r in results if int(r["n_common"]) >= 1]


def diagnostics(results: Sequence[Mapping]) -> dict:
    gaps = repository_gaps(results)
    if not gaps:
        return {"K_e": 0, "signed_mean": None, "mean_absolute": None, "minimum": None, "maximum": None,
                "opposite_direction_repositories": 0, "descriptive_only": True}
    signed = sum(gaps, Fraction(0)) / len(gaps)
    return {"K_e": len(gaps), "signed_mean": signed, "mean_absolute": sum(map(abs, gaps), Fraction(0)) / len(gaps),
            "minimum": min(gaps), "maximum": max(gaps),
            "opposite_direction_repositories": sum(1 for x in gaps if (x < 0) != (signed < 0) and x != 0),
            "descriptive_only": True}
