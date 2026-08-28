import pytest

from phd_search_agent.approvals import create_approval, decide_approval
from phd_search_agent.database import Database
from phd_search_agent.models import ApprovalStatus


def test_create_and_approve(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        item = create_approval(db, "opp", "send_email", "mail.md", "hello")
        assert item.status == ApprovalStatus.PENDING
        approved = decide_approval(db, item.id, True)
        assert approved.status == ApprovalStatus.APPROVED


def test_reject_records_reason(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        item = create_approval(db, "opp", "send_email", "mail.md", "hello")
        rejected = decide_approval(db, item.id, False, "needs rewrite")
        assert rejected.status == ApprovalStatus.REJECTED
        assert rejected.rejection_reason == "needs rewrite"


def test_cannot_decide_twice(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        item = create_approval(db, "opp", "send_email", "mail.md", "hello")
        decide_approval(db, item.id, True)
        with pytest.raises(ValueError):
            decide_approval(db, item.id, True)


def test_unknown_approval_raises(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        with pytest.raises(KeyError):
            decide_approval(db, "missing", True)
