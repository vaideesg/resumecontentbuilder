from __future__ import annotations

import math
from dataclasses import dataclass


SIGNAL_WEIGHTS = {
    "name": 0.20,
    "affiliation": 0.25,
    "collaborators": 0.25,
    "topic": 0.15,
    "geography": 0.05,
    "timeline": 0.04,
    "creator_role": 0.04,
    "cross_source": 0.02,
}


@dataclass(frozen=True)
class ConfidenceResult:
    score: float
    coverage: float
    label: str
    reasons: tuple[str, ...]


def score_identity(signals: dict[str, float | None]) -> ConfidenceResult:
    weighted_total = 0.0
    observed_weight = 0.0
    reasons: list[str] = []
    non_name_corrobators = 0

    for name, weight in SIGNAL_WEIGHTS.items():
        value = signals.get(name)
        if value is None:
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ValueError(f"Identity signal {name!r} must be a finite number")
        numeric = max(0.0, min(1.0, numeric))
        observed_weight += weight
        weighted_total += numeric * weight
        reasons.append(f"{name}={numeric:.2f}")
        if name != "name" and numeric >= 0.6:
            non_name_corrobators += 1

    if observed_weight == 0:
        return ConfidenceResult(0.0, 0.0, "excluded", ("no identity evidence",))

    score = weighted_total / observed_weight
    coverage = observed_weight

    if score >= 0.85 and coverage >= 0.60 and non_name_corrobators >= 2:
        label = "confirmed"
    elif score >= 0.70 and non_name_corrobators >= 1:
        label = "probable"
    elif score >= 0.50:
        label = "possible"
    elif score >= 0.30:
        label = "unlikely"
    else:
        label = "excluded"

    return ConfidenceResult(round(score, 4), round(coverage, 4), label, tuple(reasons))
