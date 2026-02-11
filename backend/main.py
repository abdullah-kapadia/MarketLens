from __future__ import annotations

import json
import os
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from agents.analyst_agent import run_analyst_agent
from database import get_report, get_report_pdf_path, get_reports, init_db
from models import ErrorDetail, ErrorResponse, HealthResponse, ReportDetail, ReportListResponse, StockListResponse, StockSummary
from tools.data_tools import load_config, load_dataframe, load_stock_data


load_dotenv()

app = FastAPI(title="MarketLens Backend", version="1.0.0")


def _debug_enabled() -> bool:
    return os.getenv("DEBUG", "false").lower() == "true"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _debug_enabled() else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


def _error_response(code: str, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump(),
    )


@app.post("/api/v1/analyze/{ticker}")
async def analyze_stock(ticker: str) -> EventSourceResponse:
    try:
        load_dataframe(ticker, "6M")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")

    async def event_generator() -> AsyncGenerator[dict, None]:
        async for step in run_analyst_agent(
            ticker,
            max_iterations=int(os.getenv("MAX_AGENT_ITERATIONS", "15")),
            timeout_seconds=int(os.getenv("AGENT_TIMEOUT_SECONDS", "120")),
        ):
            payload = {
                "type": step.type,
                "iteration": step.iteration,
                "timestamp": step.timestamp,
            }
            if step.type == "reasoning":
                payload["content"] = step.content
            elif step.type == "tool_call":
                payload["tool"] = step.tool_name
                payload["args"] = step.tool_input
            elif step.type == "observation":
                try:
                    payload["result"] = json.loads(step.content or "{}")
                except json.JSONDecodeError:
                    payload["result"] = step.content
            elif step.type == "complete":
                payload["run_id"] = step.report_id
                payload["analysis"] = step.analysis.model_dump() if step.analysis else None
                payload["execution_time_ms"] = step.execution_time_ms
                payload["tool_calls_count"] = step.tool_calls_count
            elif step.type == "error":
                payload["content"] = step.content
                payload["code"] = step.code

            yield {"event": step.type, "data": json.dumps(payload)}

    return EventSourceResponse(event_generator())


@app.get("/api/v1/reports", response_model=ReportListResponse)
async def list_reports(limit: int = 10, ticker: Optional[str] = None) -> ReportListResponse:
    reports = await get_reports(limit=min(limit, 50), ticker=ticker)
    return ReportListResponse(reports=reports, total=len(reports))


@app.get("/api/v1/reports/{report_id}", response_model=ReportDetail)
async def get_report_detail(report_id: str) -> ReportDetail:
    report = await get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return report


@app.get("/api/v1/reports/{report_id}/pdf")
async def get_report_pdf(report_id: str):
    pdf_path = await get_report_pdf_path(report_id)
    if not pdf_path:
        return _error_response("REPORT_NOT_FOUND", f"Report '{report_id}' not found.", status_code=404)
    return FileResponse(pdf_path, media_type="application/pdf")


@app.get("/api/v1/stocks", response_model=StockListResponse)
async def list_stocks() -> StockListResponse:
    config = load_config()
    stocks = []
    for ticker, meta in config["stocks"].items():
        try:
            data = load_stock_data(ticker, "1M")
            stocks.append(
                {
                    "ticker": ticker,
                    "name": meta["name"],
                    "sector": meta["sector"],
                    "current_price": data["current_price"],
                    "change_percent": data["change_percent"],
                    "last_updated": data["last_5_days"][-1]["date"] if data["last_5_days"] else "",
                }
            )
        except Exception:
            continue
    return StockListResponse(stocks=stocks)


@app.get("/api/v1/stocks/{ticker}/summary", response_model=StockSummary)
async def get_stock_summary(ticker: str) -> StockSummary:
    meta = load_config()["stocks"].get(ticker)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")

    df = load_dataframe(ticker, "6M")
    data = load_stock_data(ticker, "6M")

    return StockSummary(
        ticker=ticker,
        name=meta["name"],
        sector=meta["sector"],
        current_price=data["current_price"],
        change_percent=data["change_percent"],
        period_high=float(df["High"].max()),
        period_low=float(df["Low"].min()),
        avg_volume=int(df["Volume"].mean()),
        last_5_days=data["last_5_days"],
        indicators_snapshot={},
    )


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    config = load_config()
    return HealthResponse(
        status="ok",
        llm_provider=os.getenv("MODEL_PRIMARY", "claude-sonnet-4-20250514"),
        llm_fallback=os.getenv("MODEL_FALLBACK", "gpt-4o"),
        stocks_available=len(config["stocks"]),
        version="1.0.0",
    )


@app.get("/health", response_model=HealthResponse)
async def health_check_root() -> HealthResponse:
    return await health_check()
