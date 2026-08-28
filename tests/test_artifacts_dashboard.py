from phd_search_agent.artifacts import (
    write_application_package,
    write_interview_pack,
    write_qa_report,
    write_supervisor_report,
)
from phd_search_agent.database import Database
from phd_search_agent.dashboard import generate_dashboard
from phd_search_agent.models import (
    ApplicationPackage,
    InterviewPack,
    QAReport,
    SupervisorReport,
)


def test_application_artifacts(tmp_path):
    package = ApplicationPackage(
        opportunity_id="opp-1",
        outreach_email_subject="PhD inquiry",
        outreach_email_body="Hello Professor",
        tailored_cv_markdown="# Academic CV",
        cover_letter_markdown="# Cover",
        statement_of_purpose_markdown="# SOP",
        research_statement_markdown="# Research",
        application_answers_markdown="# Answers",
    )
    files = write_application_package(tmp_path, package)
    assert files["email"].exists()
    assert "PhD inquiry" in files["email"].read_text()

    assert write_supervisor_report(tmp_path, SupervisorReport(opportunity_id="opp-1")).exists()
    assert write_qa_report(
        tmp_path, QAReport(opportunity_id="opp-1", verdict="pass")
    ).exists()
    assert write_interview_pack(
        tmp_path, InterviewPack(opportunity_id="opp-1")
    ).exists()


def test_dashboard_contains_opportunity_and_approval(tmp_path, good_opportunity):
    with Database(tmp_path / "db.sqlite") as db:
        db.upsert_opportunity(good_opportunity)
        path = generate_dashboard(db, tmp_path / "dashboard.html")
    text = path.read_text()
    assert "PhD in Safe Autonomous Systems" in text
    assert "Pending approvals" in text
