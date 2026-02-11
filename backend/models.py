from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class Stock(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    change_percent: float
    last_updated: str


class AgentStep(BaseModel):
    type: Literal["reasoning", "tool_call", "observation", "complete", "error"]
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    iteration: int
    timestamp: str
    report_id: Optional[str] = None
    analysis: Optional[AgentResult] = None
    execution_time_ms: Optional[int] = None
    tool_calls_count: Optional[int] = None
    code: Optional[str] = None


class KeyLevels(BaseModel):
    immediate_support: Optional[list[float]] = None
    secondary_support: Optional[list[float]] = None
    immediate_resistance: Optional[list[float]] = None
    targets: Optional[list[float]] = None
    stop_loss: Optional[float] = None
    
    # Legacy fields for backwards compatibility
    support: Optional[list[float]] = None
    resistance: Optional[list[float]] = None
    target: Optional[float] = None


class TradingStrategy(BaseModel):
    bias: str
    entry_zones: Optional[list[str]] = None
    profit_taking: Optional[str] = None
    invalidation: Optional[str] = None


class DetailedAnalysis(BaseModel):
    price_structure: Optional[str] = None
    momentum: Optional[str] = None
    key_levels: Optional[str] = None
    volume: Optional[str] = None
    market_relative: Optional[str] = None
    
    # Legacy fields for backwards compatibility  
    trend: Optional[str] = None
    volume_context: Optional[str] = None
    market_context: Optional[str] = None


class ChartConfig(BaseModel):
    ticker: str
    period: str
    overlays: Optional[list[str]] = []
    annotations: Optional[list[str]] = []
    fibonacci: Optional[dict] = None
    channels: Optional[list[dict]] = None
    style: Literal["dark", "light"] = "dark"


class AgentResult(BaseModel):
    thesis: str
    signal: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    current_price: Optional[float] = None
    summary: str
    detailed_analysis: DetailedAnalysis
    key_levels: KeyLevels
    strategy: Optional[TradingStrategy] = None
    evidence_chain: list[str]
    risk_factors: list[str]
    chart_config: ChartConfig
    generated_at: Optional[str] = None


class ReportSummary(BaseModel):
    id: str
    ticker: str
    signal: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    thesis: str
    generated_at: str
    tool_calls_count: int
    execution_time_ms: int


class ReportDetail(ReportSummary):
    analysis: AgentResult
    reasoning_trace: list[AgentStep]
    pdf_url: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: list[ReportSummary]
    total: int


class StockListResponse(BaseModel):
    stocks: list[Stock]


class StockSummary(BaseModel):
    ticker: str
    name: str
    sector: str
    current_price: float
    change_percent: float
    period_high: float
    period_low: float
    avg_volume: int
    last_5_days: list[dict]
    indicators_snapshot: dict


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_fallback: str
    stocks_available: int
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    available_tickers: Optional[list[str]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
