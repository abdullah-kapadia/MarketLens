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
    support: list[float]  # Required for frontend
    resistance: list[float]  # Required for frontend
    stop_loss: float  # Required for frontend
    target: float  # Required for frontend
    
    # Optional detailed levels for internal use
    immediate_support: Optional[list[float]] = None
    secondary_support: Optional[list[float]] = None
    immediate_resistance: Optional[list[float]] = None
    targets: Optional[list[float]] = None


class TradingStrategy(BaseModel):
    bias: str
    entry_zones: Optional[list[str]] = None
    profit_taking: Optional[str] = None
    invalidation: Optional[str] = None


class DetailedAnalysis(BaseModel):
    trend: str  # Required for frontend
    momentum: str  # Required for frontend
    key_levels: str  # Required for frontend
    volume_context: str  # Required for frontend
    market_context: str  # Required for frontend
    
    # Optional detailed fields for internal use
    price_structure: Optional[str] = None
    market_relative: Optional[str] = None


class ChartDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    sma_9: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi: Optional[float] = None
    upper_bb: Optional[float] = None
    lower_bb: Optional[float] = None


class ChartConfig(BaseModel):
    ticker: str
    period: str
    overlays: Optional[list[str]] = []
    annotations: Optional[list[str]] = []
    fibonacci: Optional[dict] = None
    channels: Optional[list[dict]] = None
    style: Literal["dark", "light"] = "dark"
    data: Optional[list[ChartDataPoint]] = []


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
    final_commentary: str  # Required for frontend
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
