from __future__ import annotations

from datetime import date, timedelta
import pytest

from phd_search_agent.models import (
    CandidateProfile,
    EducationEntry,
    FundingStatus,
    MoneyAmount,
    Opportunity,
    SearchPreferences,
)


@pytest.fixture
def candidate() -> CandidateProfile:
    return CandidateProfile(
        name="Example Candidate",
        education=[EducationEntry(degree="MSc", field="Control Engineering")],
        research_interests=["autonomous systems", "robotics"],
        methods=["model predictive control", "control barrier functions"],
        skills={"programming": ["Python", "MATLAB"]},
        supported_claims=[
            "Completed an MSc in Control Engineering.",
            "Worked with model predictive control in an academic project.",
        ],
    )


@pytest.fixture
def preferences() -> SearchPreferences:
    return SearchPreferences(
        funding={
            "fully_funded_only": True,
            "tuition_waiver_required": True,
            "stipend_required": True,
            "minimum_stipend": {"amount": 2500, "currency": "EUR", "period": "month"},
        },
        locations={"allowed_countries": ["Netherlands", "Germany"], "excluded_countries": []},
        research={"required_topics": ["autonomous systems"], "excluded_topics": []},
        position={"named_supervisor_required": False},
        application={"avoid_mandatory_gre": True, "maximum_application_fee": 0},
        deadlines={"minimum_days_remaining": 14},
        automation={
            "maximum_new_positions_per_cycle": 10,
            "auto_research_priority_threshold": 7.5,
            "auto_prepare_application_threshold": 8.0,
            "auto_prepare_applications": True,
            "require_verified_funding_before_preparation": True,
        },
    )


@pytest.fixture
def good_opportunity() -> Opportunity:
    return Opportunity(
        id="opp-1",
        title="PhD in Safe Autonomous Systems",
        university="Example TU",
        country="Netherlands",
        city="Delft",
        url="https://example.edu/opp",
        supervisor="Prof. X",
        funding_status=FundingStatus.FULLY_FUNDED,
        stipend=MoneyAmount(amount=3200, currency="EUR", period="month"),
        tuition_waiver=True,
        deadline=date.today() + timedelta(days=60),
        topics=["autonomous systems", "robotics"],
        methods=["model predictive control"],
        mandatory_gre=False,
        application_fee=0,
        verified=True,
    )
