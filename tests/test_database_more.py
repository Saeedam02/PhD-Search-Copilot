from phd_search_agent.database import Database
from phd_search_agent.models import ApprovalItem


def test_find_missing_and_upsert_many(tmp_path, good_opportunity):
    second = good_opportunity.model_copy(deep=True)
    second.id = "opp-2"
    second.url = "https://example.edu/opp2"
    with Database(tmp_path / "db.sqlite") as db:
        assert db.find_by_url("https://missing") is None
        db.upsert_many([good_opportunity, second])
        assert len(db.list_opportunities()) == 2


def test_list_all_approvals(tmp_path):
    with Database(tmp_path / "db.sqlite") as db:
        db.save_approval(ApprovalItem(id="a1", opportunity_id="o", action_type="send_email"))
        db.save_approval(ApprovalItem(id="a2", opportunity_id="o", action_type="submit_application"))
        assert len(db.list_approvals()) == 2
        assert db.get_approval("missing") is None
