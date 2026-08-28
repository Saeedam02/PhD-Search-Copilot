"""Command-line interface for local and scheduled agent operation."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .agent_runtime import OpenAIAgentRuntime
from .analytics import deadline_alerts, outcome_statistics
from .approvals import decide_approval
from .artifacts import write_interview_pack
from .config import (
    DEFAULT_WORKSPACE,
    initialize_workspace,
    load_candidate,
    load_preferences,
    load_scoring,
    write_yaml,
)
from .database import Database
from .dashboard import generate_dashboard
from .mailer import send_email
from .models import (
    ApprovalStatus,
    CandidateProfile,
    OutcomeLearningReport,
    OutcomeRecord,
    Opportunity,
    OpportunityStatus,
    SupervisorReport,
)
from .orchestrator import Orchestrator
from .profile_ingest import collect_candidate_documents
from .scheduler import run_daemon
from .state_machine import validate_transition

app = typer.Typer(no_args_is_help=True, help="Autonomous PhD Search Copilot agent.")
console = Console()


def _load_env() -> None:
    load_dotenv(override=False)


def _db(workspace: Path) -> Database:
    return Database(workspace / "state" / "phd_agent.db")


def _orchestrator(workspace: Path) -> Orchestrator:
    _load_env()
    return Orchestrator(
        workspace=workspace,
        db=_db(workspace),
        runtime=OpenAIAgentRuntime(),
        profile=load_candidate(workspace),
        preferences=load_preferences(workspace),
        scoring=load_scoring(workspace),
    )


@app.command("init")
def init_workspace(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
    force: Annotated[bool, typer.Option("--force", help="Overwrite local example configs.")] = False,
) -> None:
    """Create the Git-ignored private workspace and example configuration."""

    created = initialize_workspace(workspace=workspace, force=force)
    console.print(f"[green]Workspace ready:[/green] {workspace}")
    console.print(f"Created/checked {len(created)} paths.")


@app.command("ingest")
def ingest(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Extract candidate documents and build candidate.yaml with the Profile Agent."""

    async def _run() -> CandidateProfile:
        _load_env()
        bundle = collect_candidate_documents(workspace / "private")
        if not bundle.documents:
            raise typer.BadParameter(
                f"No PDF/DOCX/MD/TXT files found under {workspace / 'private'}"
            )
        empty = [doc.path for doc in bundle.documents if not doc.text.strip()]
        if empty:
            console.print(
                "[yellow]Warning:[/yellow] some files contained no extractable text. "
                "Scanned PDFs may require OCR before ingestion."
            )
            for path in empty:
                console.print(f"  - {path}")
        runtime = OpenAIAgentRuntime()
        return await runtime.extract_profile(bundle)

    profile = asyncio.run(_run())
    target = workspace / "config" / "candidate.yaml"
    write_yaml(target, profile)
    console.print(f"[green]Candidate profile written:[/green] {target}")
    console.print("Review it before running applications; the agent must not invent missing facts.")


@app.command("run-cycle")
def run_cycle(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Run discovery -> verification -> filtering -> ranking -> preparation."""

    orchestrator = _orchestrator(workspace)
    try:
        record = asyncio.run(orchestrator.run_cycle())
    finally:
        orchestrator.db.close()
    console.print_json(record.model_dump_json(indent=2))
    if record.status == "failed":
        raise typer.Exit(code=1)


@app.command("daemon")
def daemon(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
    no_immediate: Annotated[bool, typer.Option("--no-immediate")] = False,
) -> None:
    """Continuously run autonomous cycles at the configured interval."""

    orchestrator = _orchestrator(workspace)
    interval = float(orchestrator.preferences.automation.get("discovery_interval_hours", 24))
    console.print(f"Running every {interval:g} hours. Ctrl+C to stop.")

    async def _cycle():
        record = await orchestrator.run_cycle()
        console.print(
            f"cycle={record.id} status={record.status} discovered={record.discovered} "
            f"eligible={record.eligible} approvals={record.approvals_created}"
        )
        return record

    try:
        asyncio.run(run_daemon(_cycle, interval, run_immediately=not no_immediate))
    except KeyboardInterrupt:
        console.print("Stopped.")
    finally:
        orchestrator.db.close()


@app.command("status")
def status(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Show ranked opportunity pipeline."""

    with _db(workspace) as db:
        opportunities = db.list_opportunities()
    table = Table(title="PhD opportunities")
    for column in ["Priority", "Score", "Status", "Filter", "Deadline", "University", "Position"]:
        table.add_column(column)
    for opp in opportunities:
        score = "-" if opp.ranking_score is None else f"{opp.ranking_score:.2f}"
        table.add_row(
            opp.priority,
            score,
            opp.status.value,
            opp.filter_decision.value,
            str(opp.deadline or "unknown"),
            opp.university,
            opp.title,
        )
    console.print(table)


@app.command("approvals")
def approvals(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
    all_items: Annotated[bool, typer.Option("--all")] = False,
) -> None:
    """List pending human approvals (or all approval history)."""

    with _db(workspace) as db:
        items = db.list_approvals(None if all_items else ApprovalStatus.PENDING.value)
    table = Table(title="Approval queue")
    for column in ["ID", "Status", "Action", "Opportunity", "Artifact"]:
        table.add_column(column)
    for item in items:
        table.add_row(item.id, item.status.value, item.action_type, item.opportunity_id, item.artifact_path)
    console.print(table)


@app.command("approve")
def approve(
    approval_id: str,
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Approve one queued external action. This does not silently dispatch it."""

    with _db(workspace) as db:
        item = decide_approval(db, approval_id, approved=True)
    console.print(f"[green]Approved:[/green] {item.id} ({item.action_type})")


@app.command("reject")
def reject(
    approval_id: str,
    reason: Annotated[str, typer.Option("--reason", "-r")] = "",
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Reject one queued external action."""

    with _db(workspace) as db:
        item = decide_approval(db, approval_id, approved=False, reason=reason)
    console.print(f"[yellow]Rejected:[/yellow] {item.id}")


@app.command("dashboard")
def dashboard(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Generate a private HTML dashboard."""

    target = workspace / "reports" / "dashboard.html"
    with _db(workspace) as db:
        generate_dashboard(db, target)
    console.print(f"[green]Dashboard written:[/green] {target}")


@app.command("import-example")
def import_example(
    path: Path,
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Import an opportunity YAML file (useful for demos and manual leads)."""

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    opportunity = Opportunity.model_validate(data)
    with _db(workspace) as db:
        db.upsert_opportunity(opportunity)
    console.print(f"Imported {opportunity.id}")


@app.command("set-status")
def set_status(
    opportunity_id: str,
    target: OpportunityStatus,
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Manually advance an opportunity through a valid workflow transition."""

    with _db(workspace) as db:
        opportunity = db.get_opportunity(opportunity_id)
        if opportunity is None:
            raise typer.BadParameter(f"Unknown opportunity id: {opportunity_id}")
        validate_transition(opportunity.status, target)
        opportunity.status = target
        db.upsert_opportunity(opportunity)
    console.print(f"{opportunity_id}: {target.value}")


@app.command("outcome")
def outcome(
    opportunity_id: str,
    result: Annotated[
        str,
        typer.Argument(help="no_response|rejected|interview|final_round|offer|withdrawn|accepted|declined"),
    ],
    notes: Annotated[str, typer.Option("--notes")] = "",
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Record an application outcome for future analysis."""

    record = OutcomeRecord(opportunity_id=opportunity_id, outcome=result, notes=notes)  # type: ignore[arg-type]
    with _db(workspace) as db:
        if db.get_opportunity(opportunity_id) is None:
            raise typer.BadParameter(f"Unknown opportunity id: {opportunity_id}")
        db.save_outcome(record)
    console.print(f"Recorded outcome: {result}")


@app.command("interview")
def interview(
    opportunity_id: str,
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Generate a role/supervisor-specific interview preparation pack."""

    async def _run():
        _load_env()
        profile = load_candidate(workspace)
        with _db(workspace) as db:
            opportunity = db.get_opportunity(opportunity_id)
        if opportunity is None:
            raise typer.BadParameter(f"Unknown opportunity id: {opportunity_id}")
        supervisor_file = workspace / "applications" / opportunity_id / "supervisor_report.json"
        supervisor = None
        if supervisor_file.exists():
            supervisor = SupervisorReport.model_validate_json(supervisor_file.read_text(encoding="utf-8"))
        runtime = OpenAIAgentRuntime()
        return await runtime.prepare_interview(profile, opportunity, supervisor)

    pack = asyncio.run(_run())
    path = write_interview_pack(workspace, pack)
    console.print(f"[green]Interview pack written:[/green] {path}")


@app.command("dispatch-email")
def dispatch_email(
    approval_id: str,
    to: Annotated[str, typer.Option("--to", help="Recipient email address.")],
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
    confirm: Annotated[bool, typer.Option("--confirm", help="Required explicit dispatch confirmation.")] = False,
) -> None:
    """Send an already-approved email draft through configured SMTP.

    This command deliberately requires both a persisted APPROVED record and an
    explicit `--confirm` flag. The autonomous cycle never calls it.
    """

    if not confirm:
        raise typer.BadParameter("Add --confirm after reviewing the approved draft and recipient")
    _load_env()
    with _db(workspace) as db:
        item = db.get_approval(approval_id)
        if item is None:
            raise typer.BadParameter(f"Unknown approval id: {approval_id}")
        if item.status != ApprovalStatus.APPROVED:
            raise typer.BadParameter("Email can be dispatched only after explicit approval")
        if item.action_type != "send_email":
            raise typer.BadParameter("Approval is not an email action")
        path = Path(item.artifact_path)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        subject = lines[0].removeprefix("# ").strip() if lines else "PhD inquiry"
        body = "\n".join(lines[1:]).strip()
        send_email(to=to, subject=subject, body=body)
        item.status = ApprovalStatus.DISPATCHED
        db.save_approval(item)
    console.print(f"[green]Email dispatched:[/green] {approval_id} -> {to}")


@app.command("validate")
def validate(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Validate local configuration without making any model/API call."""

    candidate = load_candidate(workspace)
    preferences = load_preferences(workspace)
    scoring = load_scoring(workspace)
    console.print("[green]Configuration valid.[/green]")
    console.print(
        json.dumps(
            {
                "candidate": candidate.name or "<unnamed>",
                "preference_sections": list(type(preferences).model_fields),
                "scoring_dimensions": list(scoring.weights),
            },
            indent=2,
        )
    )


@app.command("deadlines")
def deadlines(
    within: Annotated[int, typer.Option("--within", help="Show deadlines within N days.")] = 30,
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Show upcoming deadlines that need attention."""

    with _db(workspace) as db:
        items = deadline_alerts(db.list_opportunities(), within_days=within)
    table = Table(title=f"Deadlines within {within} days")
    for column in ["Days", "Priority", "Deadline", "University", "Position", "Status"]:
        table.add_column(column)
    from datetime import date as _date

    for opp in items:
        days = (opp.deadline - _date.today()).days if opp.deadline else -1
        table.add_row(str(days), opp.priority, str(opp.deadline), opp.university, opp.title, opp.status.value)
    console.print(table)


@app.command("analytics")
def analytics(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Show deterministic historical pipeline/outcome statistics."""

    with _db(workspace) as db:
        stats = outcome_statistics(db.list_opportunities(), db.list_outcomes())
    console.print_json(json.dumps(stats, indent=2))


@app.command("learn")
def learn(
    workspace: Annotated[Path, typer.Option("--workspace", "-w")] = DEFAULT_WORKSPACE,
) -> None:
    """Ask the Outcome Learning Agent for cautious targeting lessons."""

    async def _run() -> OutcomeLearningReport:
        _load_env()
        profile = load_candidate(workspace)
        with _db(workspace) as db:
            payload = {
                "opportunities": [opp.model_dump(mode="json") for opp in db.list_opportunities()],
                "outcomes": [out.model_dump(mode="json") for out in db.list_outcomes()],
            }
        runtime = OpenAIAgentRuntime()
        return await runtime.analyze_outcomes(profile, json.dumps(payload, indent=2))

    report = asyncio.run(_run())
    target = workspace / "reports" / "outcome_learning.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    console.print(f"[green]Outcome-learning report written:[/green] {target}")


if __name__ == "__main__":
    app()
