"""Deterministic pipeline analytics and deadline monitoring."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from .models import Opportunity, OutcomeRecord


def deadline_alerts(opportunities: list[Opportunity], within_days: int = 30) -> list[Opportunity]:
    if within_days < 0:
        raise ValueError("within_days cannot be negative")
    today = date.today()
    return sorted(
        [
            opp
            for opp in opportunities
            if opp.deadline is not None and 0 <= (opp.deadline - today).days <= within_days
        ],
        key=lambda opp: opp.deadline,
    )


def outcome_statistics(
    opportunities: list[Opportunity], outcomes: list[OutcomeRecord]
) -> dict[str, object]:
    by_id = {opp.id: opp for opp in opportunities}
    counts = Counter(outcome.outcome for outcome in outcomes)
    priority = defaultdict(lambda: Counter(total=0, interviews=0, offers=0))
    for outcome in outcomes:
        opp = by_id.get(outcome.opportunity_id)
        if opp is None:
            continue
        bucket = priority[opp.priority]
        bucket["total"] += 1
        if outcome.outcome in {"interview", "final_round", "offer", "accepted", "declined"}:
            bucket["interviews"] += 1
        if outcome.outcome in {"offer", "accepted", "declined"}:
            bucket["offers"] += 1
    return {
        "total_outcomes": len(outcomes),
        "outcome_counts": dict(counts),
        "by_priority": {key: dict(value) for key, value in priority.items()},
    }
