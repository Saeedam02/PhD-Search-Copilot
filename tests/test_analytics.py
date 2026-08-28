from datetime import date, timedelta

import pytest

from phd_search_agent.analytics import deadline_alerts, outcome_statistics
from phd_search_agent.models import OutcomeRecord


def test_deadline_alerts_sorted(good_opportunity):
    a = good_opportunity.model_copy(deep=True)
    b = good_opportunity.model_copy(deep=True)
    a.id = "a"
    b.id = "b"
    a.deadline = date.today() + timedelta(days=10)
    b.deadline = date.today() + timedelta(days=3)
    result = deadline_alerts([a, b], within_days=30)
    assert [x.id for x in result] == ["b", "a"]


def test_deadline_alerts_excludes_far_and_unknown(good_opportunity):
    far = good_opportunity.model_copy(deep=True)
    far.deadline = date.today() + timedelta(days=90)
    unknown = good_opportunity.model_copy(deep=True)
    unknown.id = "unknown"
    unknown.deadline = None
    assert deadline_alerts([far, unknown], within_days=30) == []


def test_deadline_alerts_rejects_negative_window():
    with pytest.raises(ValueError):
        deadline_alerts([], -1)


def test_outcome_statistics_by_priority(good_opportunity):
    good_opportunity.priority = "HIGH"
    outcomes = [
        OutcomeRecord(opportunity_id=good_opportunity.id, outcome="interview"),
        OutcomeRecord(opportunity_id=good_opportunity.id, outcome="offer"),
        OutcomeRecord(opportunity_id="missing", outcome="rejected"),
    ]
    stats = outcome_statistics([good_opportunity], outcomes)
    assert stats["total_outcomes"] == 3
    assert stats["outcome_counts"]["offer"] == 1
    assert stats["by_priority"]["HIGH"]["total"] == 2
    assert stats["by_priority"]["HIGH"]["interviews"] == 2
    assert stats["by_priority"]["HIGH"]["offers"] == 1
