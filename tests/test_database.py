from phd_search_agent.database import Database
from phd_search_agent.models import ApprovalItem, OutcomeRecord, RunRecord


def test_opportunity_round_trip(tmp_path, good_opportunity):
    with Database(tmp_path / "db.sqlite") as db:
        db.upsert_opportunity(good_opportunity)
        loaded = db.get_opportunity(good_opportunity.id)
        assert loaded is not None
        assert loaded.title == good_opportunity.title
        assert db.find_by_url(good_opportunity.url).id == good_opportunity.id
        assert len(db.list_opportunities()) == 1


def test_upsert_updates_opportunity(tmp_path, good_opportunity):
    with Database(tmp_path / "db.sqlite") as db:
        db.upsert_opportunity(good_opportunity)
        good_opportunity.priority = "HIGH"
        db.upsert_opportunity(good_opportunity)
        assert db.get_opportunity(good_opportunity.id).priority == "HIGH"


def test_approval_round_trip(tmp_path):
    item = ApprovalItem(
        id="a1", opportunity_id="o1", action_type="send_email", artifact_path="email.md"
    )
    with Database(tmp_path / "db.sqlite") as db:
        db.save_approval(item)
        assert db.get_approval("a1").id == "a1"
        assert len(db.list_approvals("pending")) == 1


def test_outcome_and_run_round_trip(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        db.save_outcome(OutcomeRecord(opportunity_id="o1", outcome="interview"))
        db.save_run(RunRecord(id="r1", status="success"))
        assert db.list_outcomes()[0].outcome == "interview"
