from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import aiosqlite

from models import AgentStep, ReportDetail, ReportSummary


def _db_path() -> Path:
    db_path_str = os.getenv("DATABASE_PATH", "data/marketlens.db")
    db_path = Path(db_path_str)
    
    # If relative path, make it relative to project root (parent of backend/)
    if not db_path.is_absolute():
        backend_dir = Path(__file__).parent
        project_root = backend_dir.parent
        db_path = project_root / db_path
    
    return db_path


async def init_db() -> None:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                ticker TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence TEXT NOT NULL,
                thesis TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                pdf_path TEXT,
                analysis_json TEXT NOT NULL,
                reasoning_trace_json TEXT NOT NULL,
                tool_calls_count INTEGER NOT NULL,
                execution_time_ms INTEGER NOT NULL
            );
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                step_type TEXT NOT NULL,
                tool_name TEXT,
                tool_input_json TEXT,
                tool_output_json TEXT,
                reasoning_text TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            );
            """
        )
        await db.commit()


async def save_report(report: ReportDetail, pdf_path: str | None = None) -> None:
    db_path = _db_path()
    print(f"[DEBUG] Database path: {db_path}")
    print(f"[DEBUG] Saving report: {report.id} for {report.ticker}")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO reports (
                id, ticker, signal, confidence, thesis, generated_at, pdf_path,
                analysis_json, reasoning_trace_json, tool_calls_count, execution_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.id,
                report.ticker,
                report.signal,
                report.confidence,
                report.thesis,
                report.generated_at,
                pdf_path,
                report.analysis.model_dump_json(),
                json.dumps([step.model_dump() for step in report.reasoning_trace]),
                report.tool_calls_count,
                report.execution_time_ms,
            ),
        )
        await db.commit()
        print(f"[DEBUG] Report {report.id} committed to database")


async def get_reports(limit: int = 10, ticker: Optional[str] = None) -> list[ReportSummary]:
    db_path = _db_path()
    print(f"[DEBUG] Getting reports from: {db_path}")
    query = (
        "SELECT id, ticker, signal, confidence, thesis, generated_at, "
        "tool_calls_count, execution_time_ms FROM reports"
    )
    params = []
    if ticker:
        query += " WHERE ticker = ?"
        params.append(ticker)
    query += " ORDER BY generated_at DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            print(f"[DEBUG] Found {len(rows)} reports in database")

    return [
        ReportSummary(
            id=row["id"],
            ticker=row["ticker"],
            signal=row["signal"],
            confidence=row["confidence"],
            thesis=row["thesis"],
            generated_at=row["generated_at"],
            tool_calls_count=row["tool_calls_count"],
            execution_time_ms=row["execution_time_ms"],
        )
        for row in rows
    ]


async def get_report(report_id: str) -> Optional[ReportDetail]:
    db_path = _db_path()
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)) as cursor:
            row = await cursor.fetchone()

    if not row:
        return None

    analysis = json.loads(row["analysis_json"])
    reasoning_trace = json.loads(row["reasoning_trace_json"])

    return ReportDetail(
        id=row["id"],
        ticker=row["ticker"],
        signal=row["signal"],
        confidence=row["confidence"],
        thesis=row["thesis"],
        generated_at=row["generated_at"],
        tool_calls_count=row["tool_calls_count"],
        execution_time_ms=row["execution_time_ms"],
        analysis=analysis,
        reasoning_trace=reasoning_trace,
        pdf_url=f"/api/v1/reports/{row['id']}/pdf",
    )


async def get_report_pdf_path(report_id: str) -> Optional[str]:
    db_path = _db_path()
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT pdf_path FROM reports WHERE id = ?", (report_id,)) as cursor:
            row = await cursor.fetchone()
    if not row:
        return None
    return row[0]


async def save_agent_step(report_id: str, step: AgentStep, step_number: int) -> None:
    db_path = _db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO agent_runs (
                report_id, step_number, step_type, tool_name, tool_input_json,
                tool_output_json, reasoning_text, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                step_number,
                step.type,
                step.tool_name,
                json.dumps(step.tool_input) if step.tool_input else None,
                None,
                step.content,
                step.timestamp,
            ),
        )
        await db.commit()
