"""Deterministic weighted ranking for already-computed semantic fit scores."""

from __future__ import annotations

from .models import FitScores, ScoringConfig


def weighted_score(scores: FitScores, config: ScoringConfig) -> float:
    numerator = 0.0
    denominator = 0.0
    data = scores.model_dump(exclude={"rationale"})
    for key, weight in config.weights.items():
        if key not in data:
            continue
        numerator += float(weight) * float(data[key])
        denominator += float(weight)
    if denominator <= 0:
        raise ValueError("No configured scoring dimensions matched FitScores")
    return round(numerator / denominator, 3)


def priority_for(score: float, config: ScoringConfig) -> str:
    high = float(config.priority_thresholds.get("high", 8.0))
    medium = float(config.priority_thresholds.get("medium", 6.5))
    if score >= high:
        return "HIGH"
    if score >= medium:
        return "MEDIUM"
    return "LOW"
