"""Explicit opportunity state transitions.

The state machine prevents accidental jumps such as DISCOVERED -> SUBMITTED
without verification/drafting/approval history.
"""

from __future__ import annotations

from .models import OpportunityStatus

ALLOWED_TRANSITIONS: dict[OpportunityStatus, set[OpportunityStatus]] = {
    OpportunityStatus.DISCOVERED: {OpportunityStatus.VERIFIED, OpportunityStatus.REVIEW, OpportunityStatus.EXPIRED},
    OpportunityStatus.VERIFIED: {OpportunityStatus.ELIGIBLE, OpportunityStatus.REVIEW, OpportunityStatus.EXPIRED},
    OpportunityStatus.REVIEW: {OpportunityStatus.VERIFIED, OpportunityStatus.ELIGIBLE, OpportunityStatus.EXPIRED, OpportunityStatus.WITHDRAWN},
    OpportunityStatus.ELIGIBLE: {OpportunityStatus.SHORTLISTED, OpportunityStatus.RESEARCHED, OpportunityStatus.WITHDRAWN, OpportunityStatus.EXPIRED},
    OpportunityStatus.SHORTLISTED: {OpportunityStatus.RESEARCHED, OpportunityStatus.DRAFTED, OpportunityStatus.WITHDRAWN, OpportunityStatus.EXPIRED},
    OpportunityStatus.RESEARCHED: {OpportunityStatus.DRAFTED, OpportunityStatus.CONTACTED, OpportunityStatus.WITHDRAWN, OpportunityStatus.EXPIRED},
    OpportunityStatus.DRAFTED: {OpportunityStatus.APPROVAL_PENDING, OpportunityStatus.APPLYING, OpportunityStatus.WITHDRAWN},
    OpportunityStatus.APPROVAL_PENDING: {OpportunityStatus.CONTACTED, OpportunityStatus.APPLYING, OpportunityStatus.WITHDRAWN},
    OpportunityStatus.CONTACTED: {OpportunityStatus.APPLYING, OpportunityStatus.SUBMITTED, OpportunityStatus.WITHDRAWN, OpportunityStatus.EXPIRED},
    OpportunityStatus.APPLYING: {OpportunityStatus.SUBMITTED, OpportunityStatus.WITHDRAWN, OpportunityStatus.EXPIRED},
    OpportunityStatus.SUBMITTED: {OpportunityStatus.INTERVIEW, OpportunityStatus.OFFER, OpportunityStatus.REJECTED, OpportunityStatus.WITHDRAWN},
    OpportunityStatus.INTERVIEW: {OpportunityStatus.OFFER, OpportunityStatus.REJECTED, OpportunityStatus.WITHDRAWN},
    OpportunityStatus.OFFER: {OpportunityStatus.WITHDRAWN},
    OpportunityStatus.REJECTED: set(),
    OpportunityStatus.WITHDRAWN: set(),
    OpportunityStatus.EXPIRED: set(),
}


def can_transition(current: OpportunityStatus, target: OpportunityStatus) -> bool:
    return target == current or target in ALLOWED_TRANSITIONS.get(current, set())


def validate_transition(current: OpportunityStatus, target: OpportunityStatus) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Invalid opportunity transition: {current.value} -> {target.value}")
