from datetime import date, timedelta

from phd_search_agent.filters import apply_hard_filters
from phd_search_agent.models import FilterDecision


def test_position_type_allowed(good_opportunity, preferences):
    preferences.position["allowed_types"] = ["salaried_phd"]
    good_opportunity.position_type = "salaried_phd"
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.PASS


def test_position_type_disallowed(good_opportunity, preferences):
    preferences.position["allowed_types"] = ["salaried_phd"]
    good_opportunity.position_type = "scholarship"
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_position_type_unknown_reviews(good_opportunity, preferences):
    preferences.position["allowed_types"] = ["salaried_phd"]
    good_opportunity.position_type = "unknown"
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_start_date_window(good_opportunity, preferences):
    preferences.start_date = {
        "earliest": (date.today() + timedelta(days=100)).isoformat(),
        "latest": (date.today() + timedelta(days=200)).isoformat(),
    }
    good_opportunity.start_date = date.today() + timedelta(days=50)
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL
    good_opportunity.start_date = date.today() + timedelta(days=250)
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_english_only_requirement(good_opportunity, preferences):
    preferences.application["english_only_acceptable"] = True
    good_opportunity.english_only = False
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_custom_deal_breaker(good_opportunity, preferences):
    preferences.application["custom_deal_breakers"] = ["security clearance"]
    good_opportunity.requirements.append("Must hold security clearance")
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL
