"""Deterministic manager for one autonomous PhD-search cycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import uuid4

from .agent_runtime import AgentRuntime
from .approvals import create_approval
from .artifacts import (
    opportunity_dir,
    write_application_package,
    write_qa_report,
    write_supervisor_report,
)
from .database import Database
from .filters import apply_hard_filters
from .models import (
    FilterDecision,
    FundingStatus,
    Opportunity,
    OpportunityStatus,
    RunRecord,
    SearchPreferences,
    SupervisorReport,
    utc_now,
)
from .scoring import priority_for, weighted_score


@dataclass
class CycleContext:
    workspace: Path
    db: Database
    runtime: AgentRuntime
    profile: object
    preferences: SearchPreferences
    scoring: object


def apply_verification(opportunity: Opportunity, report) -> Opportunity:
    """Apply a VerificationReport without overwriting known values with empties.

    Verification may refresh facts on every autonomous cycle, but it must not
    regress a progressed application (for example SUBMITTED) back to VERIFIED.
    """

    previous_status = opportunity.status
    if report.official_url:
        opportunity.url = report.official_url
    if report.position_type:
        opportunity.position_type = report.position_type
    if report.funding_status != FundingStatus.UNKNOWN:
        opportunity.funding_status = report.funding_status
    if report.stipend.amount is not None:
        opportunity.stipend = report.stipend
    if report.tuition_waiver is not None:
        opportunity.tuition_waiver = report.tuition_waiver
    if report.funding_years is not None:
        opportunity.funding_years = report.funding_years
    if report.deadline is not None:
        opportunity.deadline = report.deadline
    if report.start_date is not None:
        opportunity.start_date = report.start_date
    if report.supervisor:
        opportunity.supervisor = report.supervisor
    if report.lab:
        opportunity.lab = report.lab
    if report.topics:
        opportunity.topics = report.topics
    if report.methods:
        opportunity.methods = report.methods
    if report.requirements:
        opportunity.requirements = report.requirements
    if report.mandatory_gre is not None:
        opportunity.mandatory_gre = report.mandatory_gre
    if report.application_fee is not None:
        opportunity.application_fee = report.application_fee
    if report.english_only is not None:
        opportunity.english_only = report.english_only
    opportunity.evidence.extend(report.evidence)
    opportunity.verified = bool(report.evidence) and any(e.verified for e in report.evidence)

    early_states = {
        OpportunityStatus.DISCOVERED,
        OpportunityStatus.VERIFIED,
        OpportunityStatus.REVIEW,
        OpportunityStatus.ELIGIBLE,
        OpportunityStatus.SHORTLISTED,
    }
    if report.still_open is False and previous_status in early_states:
        opportunity.status = OpportunityStatus.EXPIRED
    elif previous_status in {
        OpportunityStatus.DISCOVERED,
        OpportunityStatus.VERIFIED,
        OpportunityStatus.REVIEW,
    }:
        opportunity.status = (
            OpportunityStatus.VERIFIED if opportunity.verified else OpportunityStatus.REVIEW
        )
    else:
        opportunity.status = previous_status
    opportunity.updated_at = utc_now()
    return opportunity


class Orchestrator:
    def __init__(
        self,
        *,
        workspace: Path,
        db: Database,
        runtime: AgentRuntime,
        profile,
        preferences: SearchPreferences,
        scoring,
    ):
        self.workspace = workspace
        self.db = db
        self.runtime = runtime
        self.profile = profile
        self.preferences = preferences
        self.scoring = scoring

    async def run_cycle(self) -> RunRecord:
        run = RunRecord(id=f"run-{uuid4().hex[:12]}")
        self.db.save_run(run)
        supervisor_cache: dict[str, SupervisorReport] = {}
        try:
            automation = self.preferences.automation
            max_results = int(automation.get("maximum_new_positions_per_cycle", 20))
            batch = await self.runtime.discover(self.profile, self.preferences, max_results)
            run.discovered = len(batch.opportunities)

            for discovered in batch.opportunities:
                try:
                    existing = self.db.find_by_url(discovered.url)
                    opportunity = existing or discovered
                    if existing is None:
                        self.db.upsert_opportunity(opportunity)

                    report = await self.runtime.verify(opportunity, self.preferences)
                    opportunity = apply_verification(opportunity, report)
                    run.verified += 1

                    if opportunity.status == OpportunityStatus.EXPIRED:
                        self.db.upsert_opportunity(opportunity)
                        continue

                    filter_result = apply_hard_filters(opportunity, self.preferences, today=date.today())
                    opportunity.filter_decision = filter_result.decision
                    opportunity.filter_reasons = filter_result.reasons
                    early_pipeline = opportunity.status in {
                        OpportunityStatus.DISCOVERED,
                        OpportunityStatus.VERIFIED,
                        OpportunityStatus.REVIEW,
                        OpportunityStatus.ELIGIBLE,
                        OpportunityStatus.SHORTLISTED,
                    }
                    if filter_result.decision == FilterDecision.FAIL:
                        if early_pipeline:
                            opportunity.status = OpportunityStatus.REVIEW
                        self.db.upsert_opportunity(opportunity)
                        continue
                    if filter_result.decision == FilterDecision.REVIEW:
                        if early_pipeline:
                            opportunity.status = OpportunityStatus.REVIEW
                    else:
                        if early_pipeline:
                            opportunity.status = OpportunityStatus.ELIGIBLE
                        run.eligible += 1

                    scores = await self.runtime.fit(self.profile, opportunity, self.preferences)
                    opportunity.fit_scores = scores
                    opportunity.ranking_score = weighted_score(scores, self.scoring)
                    opportunity.priority = priority_for(opportunity.ranking_score, self.scoring)  # type: ignore[assignment]
                    self.db.upsert_opportunity(opportunity)

                    research_threshold = float(automation.get("auto_research_priority_threshold", 8.0))
                    research_file = opportunity_dir(
                        self.workspace, opportunity.id
                    ) / "supervisor_report.json"
                    if (
                        opportunity.ranking_score >= research_threshold
                        and opportunity.supervisor
                        and not research_file.exists()
                        and opportunity.status
                        not in {
                            OpportunityStatus.CONTACTED,
                            OpportunityStatus.APPLYING,
                            OpportunityStatus.SUBMITTED,
                            OpportunityStatus.INTERVIEW,
                            OpportunityStatus.OFFER,
                            OpportunityStatus.REJECTED,
                            OpportunityStatus.WITHDRAWN,
                            OpportunityStatus.EXPIRED,
                        }
                    ):
                        sup = await self.runtime.research_supervisor(self.profile, opportunity)
                        supervisor_cache[opportunity.id] = sup
                        write_supervisor_report(self.workspace, sup)
                        opportunity.status = OpportunityStatus.RESEARCHED
                        run.researched += 1
                        self.db.upsert_opportunity(opportunity)
                    elif research_file.exists():
                        supervisor_cache[opportunity.id] = SupervisorReport.model_validate_json(
                            research_file.read_text(encoding="utf-8")
                        )

                    prepare_enabled = bool(automation.get("auto_prepare_applications", True))
                    prepare_threshold = float(automation.get("auto_prepare_application_threshold", 8.7))
                    require_verified_funding = bool(
                        automation.get("require_verified_funding_before_preparation", True)
                    )
                    funding_verified = opportunity.funding_status != FundingStatus.UNKNOWN
                    already_external = opportunity.status in {
                        OpportunityStatus.APPROVAL_PENDING,
                        OpportunityStatus.CONTACTED,
                        OpportunityStatus.APPLYING,
                        OpportunityStatus.SUBMITTED,
                        OpportunityStatus.INTERVIEW,
                        OpportunityStatus.OFFER,
                        OpportunityStatus.REJECTED,
                        OpportunityStatus.WITHDRAWN,
                        OpportunityStatus.EXPIRED,
                    }
                    if (
                        prepare_enabled
                        and not already_external
                        and filter_result.decision == FilterDecision.PASS
                        and opportunity.ranking_score >= prepare_threshold
                        and (funding_verified or not require_verified_funding)
                    ):
                        package = await self.runtime.draft_application(
                            self.profile,
                            opportunity,
                            supervisor_cache.get(opportunity.id),
                        )
                        files = write_application_package(self.workspace, package)
                        opportunity.status = OpportunityStatus.DRAFTED
                        run.drafted += 1

                        qa = await self.runtime.review_application(
                            self.profile,
                            opportunity,
                            supervisor_cache.get(opportunity.id),
                            package,
                        )
                        write_qa_report(self.workspace, qa)
                        if qa.verdict == "pass":
                            email_approval = create_approval(
                                self.db,
                                opportunity.id,
                                "send_email",
                                files["email"],
                                package.outreach_email_body,
                            )
                            submission_approval = create_approval(
                                self.db,
                                opportunity.id,
                                "submit_application",
                                files["manifest"],
                                "Application package passed independent QA and is ready for final human review.",
                            )
                            opportunity.status = OpportunityStatus.APPROVAL_PENDING
                            run.approvals_created += 2
                            # Both approvals are persisted; the autonomous cycle performs
                            # no external action.
                            _ = (email_approval, submission_approval)
                        self.db.upsert_opportunity(opportunity)
                except Exception as exc:  # one bad opportunity should not kill a daily cycle
                    run.errors.append(f"{discovered.id}: {type(exc).__name__}: {exc}")

            run.status = "partial" if run.errors else "success"
        except Exception as exc:
            run.status = "failed"
            run.errors.append(f"cycle: {type(exc).__name__}: {exc}")
        finally:
            run.finished_at = utc_now()
            self.db.save_run(run)
        return run
