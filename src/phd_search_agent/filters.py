"""Deterministic hard-filter engine.

No LLM is allowed to override this module. Unknown facts are represented as
`REVIEW` when the corresponding constraint cannot be safely evaluated.
"""

from __future__ import annotations

from datetime import date

from .models import FilterDecision, FilterResult, FundingStatus, Opportunity, SearchPreferences


def _norm(value: str) -> str:
    return " ".join(value.casefold().split())


def _contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = " | ".join(_norm(v) for v in values)
    return any(_norm(n) in haystack for n in needles if n)


def _minimum_stipend_result(opportunity: Opportunity, minimum: dict) -> tuple[bool | None, str]:
    amount = minimum.get("amount")
    if amount in (None, ""):
        return True, ""
    if opportunity.stipend.amount is None:
        return None, "Minimum stipend configured but stipend amount is unknown."
    wanted_currency = _norm(str(minimum.get("currency", "")))
    wanted_period = _norm(str(minimum.get("period", "unknown")))
    if wanted_currency and _norm(opportunity.stipend.currency) != wanted_currency:
        return None, "Stipend currency differs from configured minimum; automatic FX conversion is intentionally disabled."
    if wanted_period and wanted_period != "unknown" and _norm(opportunity.stipend.period) != wanted_period:
        return None, "Stipend period differs from configured minimum; automatic period conversion is intentionally disabled."
    return opportunity.stipend.amount >= float(amount), "Stipend is below the configured minimum."


def apply_hard_filters(
    opportunity: Opportunity,
    preferences: SearchPreferences,
    *,
    today: date | None = None,
) -> FilterResult:
    today = today or date.today()
    fail: list[str] = []
    review: list[str] = []

    funding = preferences.funding
    if funding.get("fully_funded_only", False):
        if opportunity.funding_status in {FundingStatus.SELF_FUNDED, FundingStatus.PARTIALLY_FUNDED}:
            fail.append("Position is not fully funded.")
        elif opportunity.funding_status == FundingStatus.UNKNOWN:
            review.append("Full funding is required but funding status is unverified.")

    if funding.get("tuition_waiver_required", False):
        if opportunity.tuition_waiver is False:
            fail.append("Tuition waiver is required but not provided.")
        elif opportunity.tuition_waiver is None:
            review.append("Tuition-waiver status is unknown.")

    if funding.get("stipend_required", False):
        if opportunity.stipend.amount is None and opportunity.funding_status not in {FundingStatus.SALARIED}:
            review.append("A stipend/salary is required but amount is unknown.")

    min_stipend = funding.get("minimum_stipend") or {}
    stipend_ok, stipend_reason = _minimum_stipend_result(opportunity, min_stipend)
    if stipend_ok is False:
        fail.append(stipend_reason)
    elif stipend_ok is None:
        review.append(stipend_reason)

    min_years = funding.get("minimum_funding_years")
    if min_years not in (None, ""):
        if opportunity.funding_years is None:
            review.append("Minimum funding duration is configured but duration is unknown.")
        elif opportunity.funding_years < float(min_years):
            fail.append("Funding duration is shorter than configured minimum.")

    locations = preferences.locations
    country = _norm(opportunity.country)
    city = _norm(opportunity.city)
    allowed = [_norm(v) for v in locations.get("allowed_countries", [])]
    excluded = [_norm(v) for v in locations.get("excluded_countries", [])]
    excluded_cities = [_norm(v) for v in locations.get("excluded_cities", [])]
    if country and excluded and country in excluded:
        fail.append(f"Country '{opportunity.country}' is excluded.")
    if allowed and country and country not in allowed:
        fail.append(f"Country '{opportunity.country}' is outside the allowed list.")
    if allowed and not country:
        review.append("Country is unknown but an allowed-country list is configured.")
    if city and city in excluded_cities:
        fail.append(f"City '{opportunity.city}' is excluded.")

    deadlines = preferences.deadlines
    if opportunity.deadline is None:
        if deadlines.get("minimum_days_remaining") or deadlines.get("latest_deadline") or deadlines.get("earliest_deadline"):
            review.append("Deadline is unknown.")
    else:
        if opportunity.deadline < today:
            fail.append("Deadline has already passed.")
        min_days = deadlines.get("minimum_days_remaining")
        if min_days not in (None, "") and (opportunity.deadline - today).days < int(min_days):
            fail.append("Fewer days remain than the configured preparation window.")
        earliest = deadlines.get("earliest_deadline")
        latest = deadlines.get("latest_deadline")
        if earliest and opportunity.deadline < date.fromisoformat(str(earliest)):
            fail.append("Deadline is earlier than the configured earliest deadline.")
        if latest and opportunity.deadline > date.fromisoformat(str(latest)):
            fail.append("Deadline is later than the configured latest deadline.")

    research = preferences.research
    required_topics = research.get("required_topics", [])
    excluded_topics = research.get("excluded_topics", [])
    excluded_methods = research.get("excluded_methods", [])
    if required_topics and not _contains_any(opportunity.topics, required_topics):
        if opportunity.verified:
            fail.append("Verified project topics do not include any required research topic.")
        else:
            review.append("Required-topic match cannot be confirmed before verification.")
    if excluded_topics and _contains_any(opportunity.topics, excluded_topics):
        fail.append("Project includes an excluded research topic.")
    if excluded_methods and _contains_any(opportunity.methods, excluded_methods):
        fail.append("Project includes an excluded method.")

    position = preferences.position
    allowed_types = [_norm(v) for v in position.get("allowed_types", [])]
    if allowed_types:
        if opportunity.position_type == "unknown":
            review.append("Position type is unknown but allowed position types are configured.")
        elif _norm(opportunity.position_type) not in allowed_types:
            fail.append(f"Position type '{opportunity.position_type}' is not allowed.")
    if position.get("named_supervisor_required", False) and not opportunity.supervisor:
        review.append("A named supervisor is required but none is verified.")

    start = preferences.start_date
    if opportunity.start_date is not None:
        earliest_start = start.get("earliest")
        latest_start = start.get("latest")
        if earliest_start and opportunity.start_date < date.fromisoformat(str(earliest_start)):
            fail.append("Start date is earlier than the configured window.")
        if latest_start and opportunity.start_date > date.fromisoformat(str(latest_start)):
            fail.append("Start date is later than the configured window.")

    application = preferences.application
    if application.get("avoid_mandatory_gre", False):
        if opportunity.mandatory_gre is True:
            fail.append("Mandatory GRE conflicts with preference.")
        elif opportunity.mandatory_gre is None:
            review.append("GRE requirement is unknown.")

    max_fee = application.get("maximum_application_fee")
    if max_fee not in (None, ""):
        if opportunity.application_fee is None:
            review.append("Application fee is unknown.")
        elif opportunity.application_fee > float(max_fee):
            fail.append("Application fee exceeds configured maximum.")

    if application.get("english_only_acceptable", False) and opportunity.english_only is False:
        fail.append("Position requires language conditions incompatible with English-only preference.")

    deal_breakers = application.get("custom_deal_breakers", [])
    searchable = opportunity.requirements + opportunity.topics + opportunity.methods
    if deal_breakers and _contains_any(searchable, deal_breakers):
        fail.append("Opportunity matches a configured custom deal-breaker phrase.")

    if fail:
        return FilterResult(decision=FilterDecision.FAIL, reasons=fail + review)
    if review:
        return FilterResult(decision=FilterDecision.REVIEW, reasons=review)
    return FilterResult(decision=FilterDecision.PASS, reasons=[])
