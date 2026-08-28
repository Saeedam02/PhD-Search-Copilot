"""Persistent human-approval utilities."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path
from uuid import uuid4

from .database import Database
from .models import ApprovalItem, ApprovalStatus, utc_now


def create_approval(
    db: Database,
    opportunity_id: str,
    action_type: str,
    artifact_path: Path | str,
    payload_preview: str,
) -> ApprovalItem:
    approval = ApprovalItem(
        id=f"approval-{uuid4().hex[:12]}",
        opportunity_id=opportunity_id,
        action_type=action_type,  # type: ignore[arg-type]
        artifact_path=str(artifact_path),
        payload_preview=payload_preview[:4000],
    )
    db.save_approval(approval)
    return approval


def decide_approval(
    db: Database,
    approval_id: str,
    approved: bool,
    reason: str = "",
) -> ApprovalItem:
    item = db.get_approval(approval_id)
    if item is None:
        raise KeyError(f"Unknown approval id: {approval_id}")
    if item.status != ApprovalStatus.PENDING:
        raise ValueError(f"Approval {approval_id} is already {item.status.value}")
    item.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
    item.decided_at = utc_now().astimezone(timezone.utc)
    item.rejection_reason = "" if approved else reason
    db.save_approval(item)
    return item
