from datetime import date, timedelta

from phd_search_agent.filters import apply_hard_filters
from phd_search_agent.models import FilterDecision, FundingStatus, MoneyAmount


def test_good_opportunity_passes(good_opportunity, preferences):
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.PASS
    assert result.reasons == []


def test_self_funded_fails(good_opportunity, preferences):
    good_opportunity.funding_status = FundingStatus.SELF_FUNDED
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL
    assert any("not fully funded" in reason for reason in result.reasons)


def test_unknown_funding_requires_review(good_opportunity, preferences):
    good_opportunity.funding_status = FundingStatus.UNKNOWN
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.REVIEW


def test_country_outside_allowed_list_fails(good_opportunity, preferences):
    good_opportunity.country = "France"
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL


def test_missing_country_requires_review(good_opportunity, preferences):
    good_opportunity.country = ""
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.REVIEW


def test_deadline_too_close_fails(good_opportunity, preferences):
    good_opportunity.deadline = date.today() + timedelta(days=3)
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL


def test_expired_deadline_fails(good_opportunity, preferences):
    good_opportunity.deadline = date.today() - timedelta(days=1)
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL
    assert any("already passed" in reason for reason in result.reasons)


def test_missing_deadline_requires_review(good_opportunity, preferences):
    good_opportunity.deadline = None
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.REVIEW


def test_missing_required_topic_on_verified_position_fails(good_opportunity, preferences):
    good_opportunity.topics = ["computational chemistry"]
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL


def test_missing_required_topic_unverified_is_review(good_opportunity, preferences):
    good_opportunity.topics = ["computational chemistry"]
    good_opportunity.verified = False
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.REVIEW


def test_mandatory_gre_fails(good_opportunity, preferences):
    good_opportunity.mandatory_gre = True
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_unknown_gre_requires_review(good_opportunity, preferences):
    good_opportunity.mandatory_gre = None
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_application_fee_fails(good_opportunity, preferences):
    good_opportunity.application_fee = 30
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_unknown_application_fee_requires_review(good_opportunity, preferences):
    good_opportunity.application_fee = None
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_low_stipend_fails(good_opportunity, preferences):
    good_opportunity.stipend = MoneyAmount(amount=2000, currency="EUR", period="month")
    result = apply_hard_filters(good_opportunity, preferences)
    assert result.decision == FilterDecision.FAIL


def test_currency_mismatch_requires_review(good_opportunity, preferences):
    good_opportunity.stipend = MoneyAmount(amount=4000, currency="CHF", period="month")
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW


def test_excluded_topic_fails(good_opportunity, preferences):
    preferences.research["excluded_topics"] = ["weapons"]
    good_opportunity.topics.append("weapons autonomy")
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.FAIL


def test_named_supervisor_missing_requires_review(good_opportunity, preferences):
    preferences.position["named_supervisor_required"] = True
    good_opportunity.supervisor = ""
    assert apply_hard_filters(good_opportunity, preferences).decision == FilterDecision.REVIEW
