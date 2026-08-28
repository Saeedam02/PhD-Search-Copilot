"""Generate a self-contained local HTML dashboard from SQLite state."""

from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path

from .database import Database
from .models import ApprovalStatus


def _days(deadline: date | None) -> str:
    if deadline is None:
        return "?"
    return str((deadline - date.today()).days)


def generate_dashboard(db: Database, output_path: Path) -> Path:
    opportunities = db.list_opportunities()
    approvals = db.list_approvals(status=ApprovalStatus.PENDING.value)

    rows = []
    for opp in opportunities:
        score = "" if opp.ranking_score is None else f"{opp.ranking_score:.2f}"
        rows.append(
            "<tr>"
            f"<td>{escape(opp.priority)}</td>"
            f"<td>{escape(opp.title)}</td>"
            f"<td>{escape(opp.university)}</td>"
            f"<td>{escape(opp.country)}</td>"
            f"<td>{escape(opp.funding_status.value)}</td>"
            f"<td>{escape(str(opp.deadline or 'unknown'))}</td>"
            f"<td>{escape(_days(opp.deadline))}</td>"
            f"<td>{escape(opp.filter_decision.value)}</td>"
            f"<td>{escape(score)}</td>"
            f"<td>{escape(opp.status.value)}</td>"
            f"<td><a href='{escape(opp.url)}'>source</a></td>"
            "</tr>"
        )

    approval_rows = []
    for item in approvals:
        approval_rows.append(
            "<tr>"
            f"<td>{escape(item.id)}</td>"
            f"<td>{escape(item.opportunity_id)}</td>"
            f"<td>{escape(item.action_type)}</td>"
            f"<td>{escape(item.artifact_path)}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>PhD Search Copilot</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.4; }}
h1, h2 {{ margin-top: 1.4em; }}
table {{ border-collapse: collapse; width: 100%; overflow-x: auto; display: block; }}
th, td {{ border: 1px solid #ddd; padding: .55rem; text-align: left; white-space: nowrap; }}
th {{ background: #f4f4f4; position: sticky; top: 0; }}
code {{ background: #f3f3f3; padding: .1rem .25rem; }}
.small {{ color: #666; }}
</style>
</head>
<body>
<h1>PhD Search Copilot</h1>
<p class='small'>Local dashboard. Generated from the private SQLite workspace.</p>
<h2>Opportunities ({len(opportunities)})</h2>
<table>
<thead><tr><th>Priority</th><th>Position</th><th>University</th><th>Country</th><th>Funding</th><th>Deadline</th><th>Days</th><th>Filter</th><th>Score</th><th>Status</th><th>Link</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<h2>Pending approvals ({len(approvals)})</h2>
<table>
<thead><tr><th>ID</th><th>Opportunity</th><th>Action</th><th>Artifact</th></tr></thead>
<tbody>{''.join(approval_rows)}</tbody>
</table>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
