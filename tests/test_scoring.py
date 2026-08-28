from phd_search_agent.models import FitScores, ScoringConfig
from phd_search_agent.scoring import priority_for, weighted_score


def config():
    return ScoringConfig(
        weights={"research_fit": 0.5, "skills_fit": 0.5},
        priority_thresholds={"high": 8, "medium": 6},
    )


def test_weighted_score():
    result = weighted_score(FitScores(research_fit=10, skills_fit=6), config())
    assert result == 8.0


def test_unknown_scoring_dimension_is_skipped():
    cfg = ScoringConfig(weights={"research_fit": 1, "future_dimension": 4})
    assert weighted_score(FitScores(research_fit=7), cfg) == 7


def test_priority_bands():
    cfg = config()
    assert priority_for(8.0, cfg) == "HIGH"
    assert priority_for(6.2, cfg) == "MEDIUM"
    assert priority_for(5.9, cfg) == "LOW"
