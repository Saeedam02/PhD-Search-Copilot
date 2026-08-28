from phd_search_agent.approvals import create_approval
from phd_search_agent.database import Database
from phd_search_agent.dashboard import generate_dashboard


def test_dashboard_unknown_deadline_and_pending_approval(tmp_path, good_opportunity):
    good_opportunity.deadline = None
    with Database(tmp_path / "db.sqlite") as db:
        db.upsert_opportunity(good_opportunity)
        create_approval(db, good_opportunity.id, "send_email", "mail.md", "preview")
        path = generate_dashboard(db, tmp_path / "dashboard.html")
    text = path.read_text()
    assert "?" in text
    assert "send_email" in text
