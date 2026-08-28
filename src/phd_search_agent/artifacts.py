"""Write application and research artifacts to the private workspace."""

from __future__ import annotations

from pathlib import Path

from .models import ApplicationPackage, InterviewPack, QAReport, SupervisorReport


def _safe_name(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    cleaned = "".join(c if c in allowed else "-" for c in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "opportunity"


def opportunity_dir(workspace: Path, opportunity_id: str) -> Path:
    path = workspace / "applications" / _safe_name(opportunity_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_supervisor_report(workspace: Path, report: SupervisorReport) -> Path:
    path = opportunity_dir(workspace, report.opportunity_id) / "supervisor_report.json"
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return path


def write_application_package(workspace: Path, package: ApplicationPackage) -> dict[str, Path]:
    base = opportunity_dir(workspace, package.opportunity_id)
    files = {
        "email": base / "outreach_email.md",
        "cv": base / "academic_cv.md",
        "cover_letter": base / "cover_letter.md",
        "sop": base / "statement_of_purpose.md",
        "research_statement": base / "research_statement.md",
        "answers": base / "application_answers.md",
        "manifest": base / "package_manifest.json",
    }
    files["email"].write_text(
        f"# {package.outreach_email_subject}\n\n{package.outreach_email_body}\n", encoding="utf-8"
    )
    files["cv"].write_text(package.tailored_cv_markdown, encoding="utf-8")
    files["cover_letter"].write_text(package.cover_letter_markdown, encoding="utf-8")
    files["sop"].write_text(package.statement_of_purpose_markdown, encoding="utf-8")
    files["research_statement"].write_text(package.research_statement_markdown, encoding="utf-8")
    files["answers"].write_text(package.application_answers_markdown, encoding="utf-8")
    files["manifest"].write_text(package.model_dump_json(indent=2), encoding="utf-8")
    return files


def write_qa_report(workspace: Path, report: QAReport) -> Path:
    path = opportunity_dir(workspace, report.opportunity_id) / "qa_report.json"
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return path


def write_interview_pack(workspace: Path, pack: InterviewPack) -> Path:
    path = opportunity_dir(workspace, pack.opportunity_id) / "interview_pack.json"
    path.write_text(pack.model_dump_json(indent=2), encoding="utf-8")
    return path
