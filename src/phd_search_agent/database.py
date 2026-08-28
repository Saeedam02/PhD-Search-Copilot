"""Small SQLite persistence layer for autonomous operation.

JSON payloads preserve rich Pydantic models while selected columns support
simple dashboard queries. SQLite keeps the project deployable without a server.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .models import ApprovalItem, OutcomeRecord, Opportunity, RunRecord


class Database:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *_args) -> None:
        self.close()

    def _init_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                university TEXT NOT NULL,
                country TEXT,
                deadline TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                ranking_score REAL,
                url TEXT,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                opportunity_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT NOT NULL,
                outcome TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                payload TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def upsert_opportunity(self, opportunity: Opportunity) -> None:
        self.connection.execute(
            """
            INSERT INTO opportunities
                (id, title, university, country, deadline, status, priority,
                 ranking_score, url, payload, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                university=excluded.university,
                country=excluded.country,
                deadline=excluded.deadline,
                status=excluded.status,
                priority=excluded.priority,
                ranking_score=excluded.ranking_score,
                url=excluded.url,
                payload=excluded.payload,
                updated_at=excluded.updated_at
            """,
            (
                opportunity.id,
                opportunity.title,
                opportunity.university,
                opportunity.country,
                opportunity.deadline.isoformat() if opportunity.deadline else None,
                opportunity.status.value,
                opportunity.priority,
                opportunity.ranking_score,
                opportunity.url,
                opportunity.model_dump_json(),
                opportunity.updated_at.isoformat(),
            ),
        )
        self.connection.commit()

    def get_opportunity(self, opportunity_id: str) -> Opportunity | None:
        row = self.connection.execute(
            "SELECT payload FROM opportunities WHERE id = ?", (opportunity_id,)
        ).fetchone()
        return Opportunity.model_validate_json(row["payload"]) if row else None

    def list_opportunities(self) -> list[Opportunity]:
        rows = self.connection.execute(
            "SELECT payload FROM opportunities ORDER BY ranking_score DESC, deadline ASC"
        ).fetchall()
        return [Opportunity.model_validate_json(row["payload"]) for row in rows]

    def find_by_url(self, url: str) -> Opportunity | None:
        if not url:
            return None
        row = self.connection.execute(
            "SELECT payload FROM opportunities WHERE url = ? LIMIT 1", (url,)
        ).fetchone()
        return Opportunity.model_validate_json(row["payload"]) if row else None

    def save_approval(self, approval: ApprovalItem) -> None:
        self.connection.execute(
            """
            INSERT INTO approvals (id, opportunity_id, action_type, status, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET status=excluded.status, payload=excluded.payload
            """,
            (
                approval.id,
                approval.opportunity_id,
                approval.action_type,
                approval.status.value,
                approval.model_dump_json(),
                approval.created_at.isoformat(),
            ),
        )
        self.connection.commit()

    def get_approval(self, approval_id: str) -> ApprovalItem | None:
        row = self.connection.execute(
            "SELECT payload FROM approvals WHERE id = ?", (approval_id,)
        ).fetchone()
        return ApprovalItem.model_validate_json(row["payload"]) if row else None

    def list_approvals(self, status: str | None = None) -> list[ApprovalItem]:
        if status:
            rows = self.connection.execute(
                "SELECT payload FROM approvals WHERE status = ? ORDER BY created_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = self.connection.execute(
                "SELECT payload FROM approvals ORDER BY created_at DESC"
            ).fetchall()
        return [ApprovalItem.model_validate_json(row["payload"]) for row in rows]

    def save_outcome(self, outcome: OutcomeRecord) -> None:
        self.connection.execute(
            "INSERT INTO outcomes (opportunity_id, outcome, recorded_at, payload) VALUES (?, ?, ?, ?)",
            (
                outcome.opportunity_id,
                outcome.outcome,
                outcome.recorded_at.isoformat(),
                outcome.model_dump_json(),
            ),
        )
        self.connection.commit()

    def list_outcomes(self) -> list[OutcomeRecord]:
        rows = self.connection.execute("SELECT payload FROM outcomes ORDER BY recorded_at").fetchall()
        return [OutcomeRecord.model_validate_json(row["payload"]) for row in rows]

    def save_run(self, run: RunRecord) -> None:
        self.connection.execute(
            """
            INSERT INTO runs (id, status, started_at, payload)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET status=excluded.status, payload=excluded.payload
            """,
            (run.id, run.status, run.started_at.isoformat(), run.model_dump_json()),
        )
        self.connection.commit()

    def upsert_many(self, opportunities: Iterable[Opportunity]) -> None:
        for opportunity in opportunities:
            self.upsert_opportunity(opportunity)
