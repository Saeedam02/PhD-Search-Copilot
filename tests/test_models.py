import pytest

from phd_search_agent.models import FitScores, ScoringConfig


def test_fit_scores_accept_boundaries():
    scores = FitScores(research_fit=0, supervisor_fit=10)
    assert scores.research_fit == 0
    assert scores.supervisor_fit == 10


def test_fit_scores_reject_out_of_range():
    with pytest.raises(ValueError):
        FitScores(research_fit=10.1)


def test_scoring_config_rejects_negative_weight():
    with pytest.raises(ValueError):
        ScoringConfig(weights={"research_fit": -1})


def test_scoring_config_requires_positive_total():
    with pytest.raises(ValueError):
        ScoringConfig(weights={"research_fit": 0})
