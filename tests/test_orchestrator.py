from datetime import date, timedelta

import asyncio

from phd_search_agent.database import Database
from phd_search_agent.models import (
    ApplicationPackage,
    DiscoveryBatch,
    EvidenceItem,
    FilterDecision,
    FitScores,
    FundingStatus,
    InterviewPack,
    MoneyAmount,
    QAReport,
    ScoringConfig,
    SupervisorReport,
    VerificationReport,
)
from phd_search_agent.orchestrator import Orchestrator, apply_verification


class FakeRuntime:
    def __init__(self, opportunity, *, qa_verdict="pass"):
        self.opportunity = opportunity
        self.qa_verdict = qa_verdict

    async def extract_profile(self, bundle):
        raise NotImplementedError

    async def discover(self, profile, preferences, max_results):
        return DiscoveryBatch(opportunities=[self.opportunity])

    async def verify(self, opportunity, preferences):
        return VerificationReport(
            opportunity_id=opportunity.id,
            still_open=True,
            official_url=opportunity.url,
            funding_status=FundingStatus.FULLY_FUNDED,
            stipend=MoneyAmount(amount=3200, currency="EUR", period="month"),
            tuition_waiver=True,
            deadline=date.today() + timedelta(days=60),
            supervisor="Prof. X",
            topics=["autonomous systems", "robotics"],
            methods=["model predictive control"],
            mandatory_gre=False,
            application_fee=0,
            evidence=[
                EvidenceItem(
                    claim="Official vacancy confirms funding and deadline",
                    source_url=opportunity.url,
                    authority="official_university",
                    verified=True,
                )
            ],
        )

    async def fit(self, profile, opportunity, preferences):
        return FitScores(
            research_fit=9,
            supervisor_fit=9,
            methods_fit=9,
            skills_fit=8.5,
            funding_quality=10,
            location_fit=9,
            deadline_practicality=9,
            competitiveness=8,
            evidence_quality=9,
        )

    async def research_supervisor(self, profile, opportunity):
        return SupervisorReport(
            opportunity_id=opportunity.id,
            supervisor="Prof. X",
            overall_fit=9,
            contact_priority="HIGH",
        )

    async def draft_application(self, profile, opportunity, supervisor_report):
        return ApplicationPackage(
            opportunity_id=opportunity.id,
            outreach_email_subject="PhD inquiry",
            outreach_email_body="Specific research email",
            tailored_cv_markdown="# Academic CV",
            cover_letter_markdown="# Cover",
            statement_of_purpose_markdown="# SOP",
            research_statement_markdown="# Research",
            application_answers_markdown="# Answers",
        )

    async def review_application(self, profile, opportunity, supervisor_report, package):
        return QAReport(opportunity_id=opportunity.id, verdict=self.qa_verdict)

    async def prepare_interview(self, profile, opportunity, supervisor_report):
        return InterviewPack(opportunity_id=opportunity.id)


def test_full_cycle_creates_approval(tmp_path, candidate, preferences, good_opportunity):
    scoring = ScoringConfig(
        weights={
            "research_fit": 0.3,
            "supervisor_fit": 0.2,
            "methods_fit": 0.1,
            "skills_fit": 0.1,
            "funding_quality": 0.1,
            "location_fit": 0.05,
            "deadline_practicality": 0.05,
            "competitiveness": 0.05,
            "evidence_quality": 0.05,
        },
        priority_thresholds={"high": 8, "medium": 6.5},
    )
    with Database(tmp_path / "db.sqlite") as db:
        orchestrator = Orchestrator(
            workspace=tmp_path,
            db=db,
            runtime=FakeRuntime(good_opportunity),
            profile=candidate,
            preferences=preferences,
            scoring=scoring,
        )
        run = asyncio.run(orchestrator.run_cycle())
        assert run.status == "success"
        assert run.discovered == 1
        assert run.eligible == 1
        assert run.researched == 1
        assert run.drafted == 1
        assert run.approvals_created == 2
        saved = db.get_opportunity(good_opportunity.id)
        assert saved.filter_decision == FilterDecision.PASS
        assert saved.priority == "HIGH"
        assert len(db.list_approvals("pending")) == 2


def test_qa_revision_does_not_queue_external_action(
    tmp_path, candidate, preferences, good_opportunity
):
    scoring = ScoringConfig(weights={"research_fit": 1.0})
    preferences.automation["auto_prepare_application_threshold"] = 8.5
    with Database(tmp_path / "db.sqlite") as db:
        orchestrator = Orchestrator(
            workspace=tmp_path,
            db=db,
            runtime=FakeRuntime(good_opportunity, qa_verdict="needs_revision"),
            profile=candidate,
            preferences=preferences,
            scoring=scoring,
        )
        run = asyncio.run(orchestrator.run_cycle())
        assert run.drafted == 1
        assert run.approvals_created == 0


def test_apply_verification_preserves_unknowns(good_opportunity):
    original_deadline = good_opportunity.deadline
    report = VerificationReport(opportunity_id=good_opportunity.id)
    updated = apply_verification(good_opportunity, report)
    assert updated.deadline == original_deadline


def test_second_cycle_does_not_duplicate_approvals(tmp_path, candidate, preferences, good_opportunity):
    scoring = ScoringConfig(weights={"research_fit": 1.0})
    preferences.automation["auto_prepare_application_threshold"] = 8.5
    with Database(tmp_path / "db.sqlite") as db:
        runtime = FakeRuntime(good_opportunity)
        orchestrator = Orchestrator(
            workspace=tmp_path,
            db=db,
            runtime=runtime,
            profile=candidate,
            preferences=preferences,
            scoring=scoring,
        )
        first = asyncio.run(orchestrator.run_cycle())
        second = asyncio.run(orchestrator.run_cycle())
        assert first.approvals_created == 2
        assert second.approvals_created == 0
        assert len(db.list_approvals("pending")) == 2
