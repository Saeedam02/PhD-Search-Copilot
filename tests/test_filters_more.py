from datetime import date, timedelta

from phd_search_agent.filters import apply_hard_filters
from phd_search_agent.models import FilterDecision, MoneyAmount


def test_tuition_false_fails(good_opportunity, preferences):
    good_opportunity.tuition_waiver = False
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_tuition_unknown_reviews(good_opportunity, preferences):
    good_opportunity.tuition_waiver = None
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_unknown_stipend_reviews(good_opportunity, preferences):
    good_opportunity.stipend = MoneyAmount()
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_stipend_period_mismatch_reviews(good_opportunity, preferences):
    good_opportunity.stipend = MoneyAmount(amount=40000, currency="EUR", period="year")
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_minimum_funding_years(good_opportunity, preferences):
    preferences.funding["minimum_funding_years"] = 4
    good_opportunity.funding_years = 3
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL
    good_opportunity.funding_years = None
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_excluded_city(good_opportunity, preferences):
    preferences.locations["excluded_cities"] = ["Delft"]
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_deadline_bounds(good_opportunity, preferences):
    preferences.deadlines["earliest_deadline"] = (date.today() + timedelta(days=80)).isoformat()
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL
    preferences.deadlines.pop("earliest_deadline")
    preferences.deadlines["latest_deadline"] = (date.today() + timedelta(days=30)).isoformat()
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_excluded_method(good_opportunity, preferences):
    preferences.research["excluded_methods"] = ["model predictive control"]
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL
