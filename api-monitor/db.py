"""SQLite data layer for API Monitor.

Tables:
    api_call_logs  -- per-call usage and cost log
    api_keys       -- locally stored API keys (plain text; local only)
    api_settings   -- user-defined project / purpose labels per (service, model)

All datetime values are stored as ISO-8601 strings in UTC.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "api_log.db"


def get_db_path() -> Path:
    """Return the configured DB path (env override > default)."""
    env_path = os.environ.get("API_MONITOR_DB_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_DB_PATH


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = get_db_path()
    _ensure_parent(path)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS api_call_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    service         TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    project         TEXT,
    purpose         TEXT,
    input_tokens    INTEGER NOT NULL DEFAULT 0,
    output_tokens   INTEGER NOT NULL DEFAULT 0,
    cost_usd        REAL    NOT NULL DEFAULT 0.0,
    response_ms     INTEGER,
    content_preview TEXT,
    status          TEXT    NOT NULL DEFAULT 'ok',
    error_message   TEXT
);

CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_call_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_logs_service   ON api_call_logs(service);
CREATE INDEX IF NOT EXISTS idx_api_logs_model     ON api_call_logs(model);

CREATE TABLE IF NOT EXISTS api_keys (
    service     TEXT PRIMARY KEY,
    api_key     TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS api_settings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    service     TEXT NOT NULL,
    model       TEXT NOT NULL,
    project     TEXT NOT NULL,
    purpose     TEXT,
    updated_at  TEXT NOT NULL,
    UNIQUE(service, model, project)
);
"""


def init_db() -> None:
    """Create tables and indexes if they do not exist."""
    with connect() as conn:
        conn.executescript(SCHEMA_SQL)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# api_call_logs
# ---------------------------------------------------------------------------

def insert_call_log(
    *,
    service: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    project: str | None = None,
    purpose: str | None = None,
    response_ms: int | None = None,
    content_preview: str | None = None,
    status: str = "ok",
    error_message: str | None = None,
    timestamp: str | None = None,
) -> int:
    """Insert a row into api_call_logs and return the new row id."""
    ts = timestamp or _now_iso()
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO api_call_logs (
                timestamp, service, model, project, purpose,
                input_tokens, output_tokens, cost_usd,
                response_ms, content_preview, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts, service, model, project, purpose,
                int(input_tokens), int(output_tokens), float(cost_usd),
                response_ms, content_preview, status, error_message,
            ),
        )
        return int(cur.lastrowid)


def fetch_call_logs(limit: int | None = None) -> pd.DataFrame:
    """Return call logs as a DataFrame ordered by newest first."""
    query = "SELECT * FROM api_call_logs ORDER BY timestamp DESC"
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    with connect() as conn:
        df = pd.read_sql_query(query, conn)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df


def summary_current_month() -> dict[str, Any]:
    """Return aggregate metrics for the current UTC month."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")
    with connect() as conn:
        row = conn.execute(
            """
            SELECT
                COALESCE(SUM(cost_usd), 0)                    AS total_cost,
                COALESCE(SUM(input_tokens + output_tokens), 0) AS total_tokens,
                COUNT(*)                                       AS total_calls
            FROM api_call_logs
            WHERE timestamp >= ?
            """,
            (month_start,),
        ).fetchone()
        top_model_row = conn.execute(
            """
            SELECT model, COUNT(*) AS cnt
            FROM api_call_logs
            WHERE timestamp >= ?
            GROUP BY model
            ORDER BY cnt DESC
            LIMIT 1
            """,
            (month_start,),
        ).fetchone()
    return {
        "total_cost_usd": float(row["total_cost"] or 0),
        "total_tokens": int(row["total_tokens"] or 0),
        "total_calls": int(row["total_calls"] or 0),
        "top_model": (top_model_row["model"] if top_model_row else None),
    }


def daily_cost_by_service() -> pd.DataFrame:
    """Return daily cost grouped by service (long format)."""
    with connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT DATE(timestamp) AS date, service, SUM(cost_usd) AS cost
            FROM api_call_logs
            GROUP BY DATE(timestamp), service
            ORDER BY date ASC
            """,
            conn,
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def service_cost_share() -> pd.DataFrame:
    """Return total cost per service (current month)."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(timespec="seconds")
    with connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT service, SUM(cost_usd) AS cost
            FROM api_call_logs
            WHERE timestamp >= ?
            GROUP BY service
            """,
            conn,
            params=(month_start,),
        )
    return df


# ---------------------------------------------------------------------------
# api_keys
# ---------------------------------------------------------------------------

def upsert_api_key(service: str, api_key: str) -> None:
    """Insert or update an API key for a service."""
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO api_keys (service, api_key, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(service) DO UPDATE SET
                api_key    = excluded.api_key,
                updated_at = excluded.updated_at
            """,
            (service, api_key, _now_iso()),
        )


def get_api_key(service: str) -> str | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT api_key FROM api_keys WHERE service = ?",
            (service,),
        ).fetchone()
    return row["api_key"] if row else None


def list_api_keys() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT service, api_key, updated_at FROM api_keys ORDER BY service"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_api_key(service: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM api_keys WHERE service = ?", (service,))


# ---------------------------------------------------------------------------
# api_settings (project / purpose labels)
# ---------------------------------------------------------------------------

def upsert_setting(service: str, model: str, project: str, purpose: str | None = None) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO api_settings (service, model, project, purpose, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(service, model, project) DO UPDATE SET
                purpose    = excluded.purpose,
                updated_at = excluded.updated_at
            """,
            (service, model, project, purpose, _now_iso()),
        )


def list_settings() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, service, model, project, purpose, updated_at "
            "FROM api_settings ORDER BY service, model, project"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_setting(setting_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM api_settings WHERE id = ?", (int(setting_id),))


# ---------------------------------------------------------------------------
# Entry point for ad-hoc init: `python -m db`  /  `python db.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print(f"[api-monitor] initialized DB at: {get_db_path()}")
