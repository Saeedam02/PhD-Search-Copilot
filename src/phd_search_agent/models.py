"""Typed data models shared by deterministic code and AI-agent stages.

The central design principle is provenance: an opportunity can contain unknown
fields and evidence records instead of forcing the model to invent a complete
record. This makes hard filtering and human review much safer.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    """Return an aware UTC timestamp."""

    return datetime.now(timezone.utc)


class FundingStatus(str, Enum):
    UNKNOWN = "unknown"
    FULLY_FUNDED = "fully_funded"
    PARTIALLY_FUNDED = "partially_funded"
    SELF_FUNDED = "self_funded"
    SALARIED = "salaried"
    SCHOLARSHIP = "scholarship"


class OpportunityStatus(str, Enum):
    DISCOVERED = "discovered"
    VERIFIED = "verified"
    REVIEW = "review"
    ELIGIBLE = "eligible"
    SHORTLISTED = "shortlisted"
    RESEARCHED = "researched"
    DRAFTED = "drafted"
    APPROVAL_PENDING = "approval_pending"
    CONTACTED = "contacted"
    APPLYING = "applying"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class FilterDecision(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    REVIEW = "review"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPATCHED = "dispatched"


class EvidenceItem(BaseModel):
    """One factual claim and the source used to support it."""

    claim: str
    source_url: str = ""
    source_title: str = ""
    authority: str = "unknown"
    verified: bool = False
    retrieved_at: datetime = Field(default_factory=utc_now)


class MoneyAmount(BaseModel):
    amount: float | None = None
    currency: str = ""
    period: Literal["month", "year", "hour", "total", "unknown"] = "unknown"


class EducationEntry(BaseModel):
    degree: str
    field: str = ""
    institution: str = ""
    country: str = ""
    start_year: int | None = None
    end_year: int | None = None
    thesis_title: str = ""
    grade: str = ""


class LanguageEntry(BaseModel):
    language: str
    level: str = ""
    evidence: str = ""


class CandidateContact(BaseModel):
    email: str = ""
    website: str = ""
    github: str = ""
    linkedin: str = ""


class CandidateProfile(BaseModel):
    """Structured candidate facts extracted from user-provided evidence."""

    name: str = ""
    headline: str = ""
    contact: CandidateContact = Field(default_factory=CandidateContact)
    education: list[EducationEntry] = Field(default_factory=list)
    research_interests: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(default_factory=dict)
    publications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    source_files: list[str] = Field(default_factory=list)
    supported_claims: list[str] = Field(default_factory=list)


class FitScores(BaseModel):
    """Semantic 0–10 dimensions used by deterministic weighted scoring."""

    research_fit: float = 0.0
    supervisor_fit: float = 0.0
    methods_fit: float = 0.0
    skills_fit: float = 0.0
    funding_quality: float = 0.0
    location_fit: float = 0.0
    deadline_practicality: float = 0.0
    competitiveness: float = 0.0
    evidence_quality: float = 0.0
    rationale: dict[str, str] = Field(default_factory=dict)

    @field_validator(
        "research_fit",
        "supervisor_fit",
        "methods_fit",
        "skills_fit",
        "funding_quality",
        "location_fit",
        "deadline_practicality",
        "competitiveness",
        "evidence_quality",
    )
    @classmethod
    def score_range(cls, value: float) -> float:
        if not 0.0 <= value <= 10.0:
            raise ValueError("fit scores must be in [0, 10]")
        return float(value)


class Opportunity(BaseModel):
    """Normalized PhD opportunity persisted across the complete workflow."""

    id: str
    title: str
    university: str
    country: str = ""
    city: str = ""
    url: str = ""
    source_type: str = "unknown"
    position_type: str = "unknown"
    supervisor: str = ""
    lab: str = ""
    funding_status: FundingStatus = FundingStatus.UNKNOWN
    stipend: MoneyAmount = Field(default_factory=MoneyAmount)
    tuition_waiver: bool | None = None
    funding_years: float | None = None
    deadline: date | None = None
    start_date: date | None = None
    topics: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    mandatory_gre: bool | None = None
    application_fee: float | None = None
    english_only: bool | None = None
    verified: bool = False
    evidence: list[EvidenceItem] = Field(default_factory=list)
    fit_scores: FitScores | None = None
    ranking_score: float | None = None
    priority: Literal["HIGH", "MEDIUM", "LOW", "UNRANKED"] = "UNRANKED"
    filter_decision: FilterDecision = FilterDecision.REVIEW
    filter_reasons: list[str] = Field(default_factory=list)
    status: OpportunityStatus = OpportunityStatus.DISCOVERED
    discovered_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DiscoveryBatch(BaseModel):
    opportunities: list[Opportunity] = Field(default_factory=list)
    search_summary: str = ""


class VerificationReport(BaseModel):
    """Structured verification patch produced from authoritative evidence."""

    opportunity_id: str
    still_open: bool | None = None
    official_url: str = ""
    position_type: str = ""
    funding_status: FundingStatus = FundingStatus.UNKNOWN
    stipend: MoneyAmount = Field(default_factory=MoneyAmount)
    tuition_waiver: bool | None = None
    funding_years: float | None = None
    deadline: date | None = None
    start_date: date | None = None
    supervisor: str = ""
    lab: str = ""
    topics: list[str] = Field(default_factory=list)
    methods: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    mandatory_gre: bool | None = None
    application_fee: float | None = None
    english_only: bool | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    verification_summary: str = ""


class FilterResult(BaseModel):
    decision: FilterDecision
    reasons: list[str] = Field(default_factory=list)


class SupervisorReport(BaseModel):
    opportunity_id: str
    supervisor: str = ""
    lab: str = ""
    overall_fit: float = 0.0
    strong_overlaps: list[str] = Field(default_factory=list)
    moderate_overlaps: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recent_research: list[str] = Field(default_factory=list)
    relevant_publications: list[str] = Field(default_factory=list)
    outreach_angle: str = ""
    contact_priority: Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"] = "UNKNOWN"
    evidence: list[EvidenceItem] = Field(default_factory=list)

    @field_validator("overall_fit")
    @classmethod
    def supervisor_score_range(cls, value: float) -> float:
        if not 0 <= value <= 10:
            raise ValueError("overall_fit must be in [0, 10]")
        return float(value)


class ApplicationPackage(BaseModel):
    opportunity_id: str
    outreach_email_subject: str = ""
    outreach_email_body: str = ""
    tailored_cv_markdown: str = ""
    cover_letter_markdown: str = ""
    statement_of_purpose_markdown: str = ""
    research_statement_markdown: str = ""
    application_answers_markdown: str = ""
    candidate_claims_used: list[str] = Field(default_factory=list)
    source_notes: list[str] = Field(default_factory=list)


class QAReport(BaseModel):
    opportunity_id: str
    verdict: Literal["pass", "needs_revision", "block"]
    unsupported_candidate_claims: list[str] = Field(default_factory=list)
    unsupported_external_claims: list[str] = Field(default_factory=list)
    inconsistencies: list[str] = Field(default_factory=list)
    generic_or_weak_language: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    revision_instructions: list[str] = Field(default_factory=list)
    summary: str = ""


class InterviewPack(BaseModel):
    opportunity_id: str
    two_minute_pitch: str = ""
    thesis_explanation: str = ""
    likely_research_questions: list[str] = Field(default_factory=list)
    likely_technical_questions: list[str] = Field(default_factory=list)
    papers_to_review: list[str] = Field(default_factory=list)
    candidate_gaps_to_prepare: list[str] = Field(default_factory=list)
    questions_to_ask: list[str] = Field(default_factory=list)
    suggested_research_directions: list[str] = Field(default_factory=list)


class ApprovalItem(BaseModel):
    id: str
    opportunity_id: str
    action_type: Literal[
        "send_email",
        "submit_application",
        "pay_fee",
        "withdraw_application",
        "accept_offer",
        "reject_offer",
    ]
    artifact_path: str = ""
    payload_preview: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    decided_at: datetime | None = None
    rejection_reason: str = ""


class RunRecord(BaseModel):
    id: str
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None
    status: Literal["running", "success", "partial", "failed"] = "running"
    discovered: int = 0
    verified: int = 0
    eligible: int = 0
    researched: int = 0
    drafted: int = 0
    approvals_created: int = 0
    errors: list[str] = Field(default_factory=list)


class OutcomeLearningReport(BaseModel):
    summary: str = ""
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    targeting_recommendations: list[str] = Field(default_factory=list)
    application_recommendations: list[str] = Field(default_factory=list)
    data_limitations: list[str] = Field(default_factory=list)
    proposed_weight_changes: dict[str, float] = Field(default_factory=dict)


class OutcomeRecord(BaseModel):
    opportunity_id: str
    outcome: Literal[
        "no_response",
        "rejected",
        "interview",
        "final_round",
        "offer",
        "withdrawn",
        "accepted",
        "declined",
    ]
    recorded_at: datetime = Field(default_factory=utc_now)
    notes: str = ""


class ExtractedDocument(BaseModel):
    path: str
    text: str
    kind: str


class CandidateDocumentBundle(BaseModel):
    documents: list[ExtractedDocument] = Field(default_factory=list)

    @property
    def combined_text(self) -> str:
        return "\n\n".join(
            f"===== FILE: {doc.path} =====\n{doc.text}" for doc in self.documents if doc.text.strip()
        )


class SearchPreferences(BaseModel):
    """Typed wrapper used by config loader; sections remain dictionaries.

    Keeping nested sections as dictionaries makes user configuration extensible
    while deterministic filters access documented keys defensively.
    """

    funding: dict[str, Any] = Field(default_factory=dict)
    locations: dict[str, Any] = Field(default_factory=dict)
    research: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, Any] = Field(default_factory=dict)
    application: dict[str, Any] = Field(default_factory=dict)
    deadlines: dict[str, Any] = Field(default_factory=dict)
    start_date: dict[str, Any] = Field(default_factory=dict)
    automation: dict[str, Any] = Field(default_factory=dict)


class ScoringConfig(BaseModel):
    weights: dict[str, float]
    priority_thresholds: dict[str, float] = Field(default_factory=lambda: {"high": 8.0, "medium": 6.5})

    @field_validator("weights")
    @classmethod
    def positive_weights(cls, weights: dict[str, float]) -> dict[str, float]:
        if not weights:
            raise ValueError("at least one scoring weight is required")
        if any(v < 0 for v in weights.values()):
            raise ValueError("scoring weights cannot be negative")
        if sum(weights.values()) <= 0:
            raise ValueError("sum of scoring weights must be positive")
        return {str(k): float(v) for k, v in weights.items()}
