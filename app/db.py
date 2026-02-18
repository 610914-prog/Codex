from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, List

from app.models import Agent, AgentCreate, AgentStatus

DB_PATH = Path("agents.db")


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                deployment_target TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_agent(payload: AgentCreate) -> Agent:
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT INTO agents (name, system_prompt, model, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.system_prompt,
                payload.model,
                AgentStatus.draft.value,
                datetime.utcnow().isoformat(),
            ),
        )
        agent_id = int(cursor.lastrowid)
        row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
    return _row_to_agent(row)


def list_agents() -> List[Agent]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM agents ORDER BY id DESC").fetchall()
    return [_row_to_agent(r) for r in rows]


def get_agent(agent_id: int) -> Agent | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
    if not row:
        return None
    return _row_to_agent(row)


def update_agent_status(agent_id: int, status: AgentStatus, deployment_target: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE agents SET status = ?, deployment_target = ? WHERE id = ?",
            (status.value, deployment_target, agent_id),
        )


def _row_to_agent(row: sqlite3.Row) -> Agent:
    return Agent(
        id=row["id"],
        name=row["name"],
        system_prompt=row["system_prompt"],
        model=row["model"],
        status=AgentStatus(row["status"]),
        deployment_target=row["deployment_target"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
