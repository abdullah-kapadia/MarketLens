# MarketLens — API Contract Specification

**Version:** 1.0
**Status:** Definitive — both backend and frontend teams develop against this spec
**Last Updated:** February 2026

This document defines the **exact interface** between `marketlens-backend` (FastAPI/Python) and `marketlens-frontend` (Next.js/TypeScript). It is the **single source of truth** for all API communication. Both teams must implement to this spec precisely.

---

## 1. Base Configuration

| Setting | Value |
|---------|-------|
| Backend URL | `http://localhost:8000` |
| API Prefix | `/api/v1` |
| CORS Origins | `http://localhost:3000` |
| Default Content-Type | `application/json` |
| SSE Content-Type | `text/event-stream` |
| Character Encoding | UTF-8 |
| Date Format | ISO 8601 (`2026-02-10T14:30:00Z`) |

---

## 2. Endpoints

### 2.1 `POST /api/v1/analyze/{ticker}` — Stream Agent Analysis

The core endpoint. Triggers the AI analyst agent and streams its reasoning process via Server-Sent Events.

**Request:**

| Part | Detail |
|------|--------|
| Method | `POST` |
| Path Parameter | `ticker` — string, uppercase (e.g., `OGDC`, `TRG`) |
| Request Body | None |
| Content-Type | N/A |

**Response:**

| Part | Detail |
|------|--------|
| Status | `200 OK` (stream starts) |
| Content-Type | `text/event-stream` |
| Cache-Control | `no-cache` |
| Connection | `keep-alive` |

**SSE Event Format:**

Each event is a single `data:` line containing a JSON object, followed by two newlines:

```
data: {"type": "reasoning", "content": "...", "iteration": 1, "timestamp": "2026-02-10T14:30:01Z"}\n\n
```

**Event Types:**

#### `reasoning` — Agent's internal thinking

```json
{
  "type": "reasoning",
  "content": "Loading OGDC data for the last 6 months. The stock has been declining, so I want to assess the current trend and check for oversold conditions.",
  "iteration": 1,
  "timestamp": "2026-02-10T14:30:01Z"
}
```

#### `tool_call` — Agent decides to use a tool

```json
{
  "type": "tool_call",
  "tool_name": "calculate_indicator",
  "tool_input": {
    "ticker": "OGDC",
    "indicator": "RSI",
    "params": { "period": 14 }
  },
  "iteration": 2,
  "timestamp": "2026-02-10T14:30:03Z"
}
```

#### `observation` — Tool result returned to agent

```json
{
  "type": "observation",
  "tool_name": "calculate_indicator",
  "content": "RSI(14) = 32.1 — Oversold territory (below 30 is deeply oversold). Current RSI suggests selling pressure may be exhausting.",
  "iteration": 2,
  "timestamp": "2026-02-10T14:30:04Z"
}
```

#### `complete` — Agent has finished analysis

```json
{
  "type": "complete",
  "report_id": "rpt_a1b2c3d4",
  "analysis": {
    "thesis": "OGDC faces sustained bearish pressure with RSI in oversold territory near key support at PKR 115, but high selling volume and stock-specific weakness (vs flat KSE-100) suggest further downside risk before a reversal.",
    "signal": "BEARISH",
    "confidence": "HIGH",
    "summary": "OGDC has declined 15% over 6 months while KSE-100 remained flat, indicating stock-specific weakness. RSI at 32 shows oversold conditions but volume analysis reveals persistent selling pressure. Key support at 115 is only 3 points below current price — a break below would accelerate the decline.",
    "detailed_analysis": {
      "trend": "Strong downtrend. Price below SMA-50 and SMA-200. Lower highs and lower lows over 6 months.",
      "momentum": "RSI(14) at 32.1 — oversold but not yet showing bullish divergence. MACD below signal line with widening histogram.",
      "key_levels": "Support at 115 (pivot), 108 (Fibonacci 61.8%). Resistance at 128 (SMA-50), 135 (recent swing high).",
      "volume_context": "Volume trending 25% above 20-day average. Selling volume dominates with 3:1 ratio on down days.",
      "market_context": "KSE-100 flat over same period. Energy sector peers (PSO) also weak but less so. OGDC underperforming sector by 8%."
    },
    "key_levels": {
      "support": [115.0, 108.0],
      "resistance": [128.0, 135.0],
      "stop_loss": 112.0,
      "target": 108.0
    },
    "evidence_chain": [
      "Price declined 15% in 6 months (142 → 118.5)",
      "RSI(14) = 32.1 — oversold territory",
      "Support at 115 only 3 points below current price",
      "Selling volume 25% above average",
      "KSE-100 flat — stock-specific weakness confirmed",
      "Underperforming energy sector peers by 8%"
    ],
    "risk_factors": [
      "RSI oversold may trigger short-term bounce — contrarian risk",
      "Oil price movements (external factor not in data)",
      "Support at 115 has held twice before — potential reversal zone"
    ],
    "chart_config": {
      "ticker": "OGDC",
      "period": "6M",
      "overlays": ["SMA_200", "support_resistance"],
      "annotations": ["current_price", "rsi_oversold_zone"],
      "style": "dark"
    }
  },
  "execution_time_ms": 12400,
  "tool_calls_count": 6,
  "timestamp": "2026-02-10T14:30:12Z"
}
```

#### `error` — Agent encountered an error

```json
{
  "type": "error",
  "content": "Agent timeout after 60 seconds. Partial analysis available.",
  "code": "AGENT_TIMEOUT",
  "timestamp": "2026-02-10T14:31:01Z"
}
```

**Error Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Stream started successfully |
| `404` | Unknown ticker — returns JSON error body (not SSE) |
| `503` | LLM provider unavailable — returns JSON error body |
| `429` | Rate limited |

---

### 2.2 `GET /api/v1/reports` — List Past Reports

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Query Parameters | `limit` (int, default 10, max 50), `ticker` (string, optional filter) |

**Response: `200 OK`**

```json
{
  "reports": [
    {
      "id": "rpt_a1b2c3d4",
      "ticker": "OGDC",
      "signal": "BEARISH",
      "confidence": "HIGH",
      "thesis": "OGDC faces sustained bearish pressure with RSI in oversold territory near key support at PKR 115...",
      "generated_at": "2026-02-10T14:30:12Z",
      "tool_calls_count": 6,
      "execution_time_ms": 12400
    },
    {
      "id": "rpt_e5f6g7h8",
      "ticker": "TRG",
      "signal": "BULLISH",
      "confidence": "HIGH",
      "thesis": "TRG shows strong bullish momentum with ADX confirming trend strength...",
      "generated_at": "2026-02-10T14:25:00Z",
      "tool_calls_count": 5,
      "execution_time_ms": 10200
    }
  ],
  "total": 2
}
```

---

### 2.3 `GET /api/v1/reports/{report_id}` — Get Full Report

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Path Parameter | `report_id` — string (e.g., `rpt_a1b2c3d4`) |

**Response: `200 OK`**

```json
{
  "id": "rpt_a1b2c3d4",
  "ticker": "OGDC",
  "signal": "BEARISH",
  "confidence": "HIGH",
  "thesis": "OGDC faces sustained bearish pressure...",
  "generated_at": "2026-02-10T14:30:12Z",
  "tool_calls_count": 6,
  "execution_time_ms": 12400,
  "analysis": {
    "thesis": "...",
    "signal": "BEARISH",
    "confidence": "HIGH",
    "summary": "...",
    "detailed_analysis": { "..." : "..." },
    "key_levels": { "..." : "..." },
    "evidence_chain": ["..."],
    "risk_factors": ["..."],
    "chart_config": { "..." : "..." }
  },
  "reasoning_trace": [
    {
      "type": "reasoning",
      "content": "Loading OGDC data...",
      "iteration": 1,
      "timestamp": "2026-02-10T14:30:01Z"
    },
    {
      "type": "tool_call",
      "tool_name": "load_stock_data",
      "tool_input": { "ticker": "OGDC", "period": "6M" },
      "iteration": 1,
      "timestamp": "2026-02-10T14:30:02Z"
    }
  ],
  "pdf_url": "/api/v1/reports/rpt_a1b2c3d4/pdf"
}
```

**Error: `404 Not Found`**

```json
{
  "error": {
    "code": "REPORT_NOT_FOUND",
    "message": "Report 'rpt_xyz' not found."
  }
}
```

---

### 2.4 `GET /api/v1/reports/{report_id}/pdf` — Download PDF

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Path Parameter | `report_id` — string |

**Response: `200 OK`**

| Part | Detail |
|------|--------|
| Content-Type | `application/pdf` |
| Content-Disposition | `inline; filename="MarketLens_OGDC_2026-02-10.pdf"` |
| Body | Binary PDF data |

**Error: `404 Not Found`** — same error format as 2.3

---

### 2.5 `GET /api/v1/stocks` — List Available Stocks

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Parameters | None |

**Response: `200 OK`**

```json
{
  "stocks": [
    {
      "ticker": "OGDC",
      "name": "Oil & Gas Development Company",
      "sector": "Energy",
      "current_price": 118.50,
      "change_percent": -2.3,
      "last_updated": "2026-02-10"
    },
    {
      "ticker": "TRG",
      "name": "TRG Pakistan (Systems Limited)",
      "sector": "Technology",
      "current_price": 145.75,
      "change_percent": 3.8,
      "last_updated": "2026-02-10"
    },
    {
      "ticker": "PSO",
      "name": "Pakistan State Oil",
      "sector": "Energy",
      "current_price": 215.00,
      "change_percent": -1.1,
      "last_updated": "2026-02-10"
    },
    {
      "ticker": "LUCK",
      "name": "Lucky Cement",
      "sector": "Cement",
      "current_price": 780.00,
      "change_percent": 0.5,
      "last_updated": "2026-02-10"
    },
    {
      "ticker": "ENGRO",
      "name": "Engro Corporation",
      "sector": "Conglomerate",
      "current_price": 320.50,
      "change_percent": 1.2,
      "last_updated": "2026-02-10"
    }
  ]
}
```

---

### 2.6 `GET /api/v1/stocks/{ticker}/summary` — Quick Stock Summary

Returns basic stats without running the agent. Used for the stock header display.

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Path Parameter | `ticker` — string |

**Response: `200 OK`**

```json
{
  "ticker": "OGDC",
  "name": "Oil & Gas Development Company",
  "sector": "Energy",
  "current_price": 118.50,
  "change_percent": -2.3,
  "period_high": 142.00,
  "period_low": 112.00,
  "avg_volume": 5200000,
  "last_5_days": [
    { "date": "2026-02-10", "open": 120.0, "high": 121.5, "low": 117.8, "close": 118.5, "volume": 5800000 },
    { "date": "2026-02-07", "open": 121.5, "high": 122.0, "low": 119.5, "close": 120.0, "volume": 4900000 },
    { "date": "2026-02-06", "open": 122.0, "high": 123.0, "low": 121.0, "close": 121.5, "volume": 5100000 },
    { "date": "2026-02-05", "open": 123.5, "high": 124.0, "low": 121.5, "close": 122.0, "volume": 5400000 },
    { "date": "2026-02-04", "open": 124.0, "high": 125.0, "low": 123.0, "close": 123.5, "volume": 4700000 }
  ],
  "indicators_snapshot": {
    "rsi_14": 32.1,
    "sma_50": 128.3,
    "sma_200": 133.7
  }
}
```

---

### 2.7 `GET /api/v1/health` — Health Check

**Request:**

| Part | Detail |
|------|--------|
| Method | `GET` |
| Parameters | None |

**Response: `200 OK`**

```json
{
  "status": "ok",
  "llm_provider": "anthropic",
  "llm_fallback": "openai",
  "stocks_available": 5,
  "version": "1.0.0"
}
```

---

## 3. Data Models

### 3.1 Shared Type Definitions

#### Python (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


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


class KeyLevels(BaseModel):
    support: list[float]
    resistance: list[float]
    stop_loss: float
    target: float


class DetailedAnalysis(BaseModel):
    trend: str
    momentum: str
    key_levels: str
    volume_context: str
    market_context: str


class ChartConfig(BaseModel):
    ticker: str
    period: str
    overlays: list[str]
    annotations: list[str]
    style: Literal["dark", "light"]


class AgentResult(BaseModel):
    thesis: str
    signal: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    summary: str
    detailed_analysis: DetailedAnalysis
    key_levels: KeyLevels
    evidence_chain: list[str]
    risk_factors: list[str]
    chart_config: ChartConfig


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
    pdf_url: str


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
```

#### TypeScript

```typescript
// lib/types.ts

export type Signal = "BULLISH" | "BEARISH" | "NEUTRAL";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";
export type StepType = "reasoning" | "tool_call" | "observation" | "complete" | "error";

export interface Stock {
  ticker: string;
  name: string;
  sector: string;
  current_price: number;
  change_percent: number;
  last_updated: string;
}

export interface AgentStep {
  type: StepType;
  content?: string;
  tool_name?: string;
  tool_input?: Record<string, unknown>;
  iteration: number;
  timestamp: string;
  // Only present on "complete" type
  report_id?: string;
  analysis?: AgentResult;
  execution_time_ms?: number;
  tool_calls_count?: number;
  // Only present on "error" type
  code?: string;
}

export interface KeyLevels {
  support: number[];
  resistance: number[];
  stop_loss: number;
  target: number;
}

export interface DetailedAnalysis {
  trend: string;
  momentum: string;
  key_levels: string;
  volume_context: string;
  market_context: string;
}

export interface ChartConfig {
  ticker: string;
  period: string;
  overlays: string[];
  annotations: string[];
  style: "dark" | "light";
}

export interface AgentResult {
  thesis: string;
  signal: Signal;
  confidence: Confidence;
  summary: string;
  detailed_analysis: DetailedAnalysis;
  key_levels: KeyLevels;
  evidence_chain: string[];
  risk_factors: string[];
  chart_config: ChartConfig;
}

export interface ReportSummary {
  id: string;
  ticker: string;
  signal: Signal;
  confidence: Confidence;
  thesis: string;
  generated_at: string;
  tool_calls_count: number;
  execution_time_ms: number;
}

export interface ReportDetail extends ReportSummary {
  analysis: AgentResult;
  reasoning_trace: AgentStep[];
  pdf_url: string;
}

export interface ReportListResponse {
  reports: ReportSummary[];
  total: number;
}

export interface StockListResponse {
  stocks: Stock[];
}

export interface StockSummary {
  ticker: string;
  name: string;
  sector: string;
  current_price: number;
  change_percent: number;
  period_high: number;
  period_low: number;
  avg_volume: number;
  last_5_days: DayData[];
  indicators_snapshot: {
    rsi_14: number;
    sma_50: number;
    sma_200: number;
  };
}

export interface DayData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    available_tickers?: string[];
  };
}

// SSE State Management Types

export type AgentStreamStatus =
  | "idle"
  | "connecting"
  | "streaming"
  | "generating_pdf"
  | "complete"
  | "error";

export interface AgentStreamState {
  status: AgentStreamStatus;
  steps: AgentStep[];
  currentReport: ReportDetail | null;
  error: string | null;
}

export type AgentStreamAction =
  | { type: "START_STREAM" }
  | { type: "ADD_STEP"; step: AgentStep }
  | { type: "STREAM_COMPLETE"; report: ReportDetail }
  | { type: "STREAM_ERROR"; error: string }
  | { type: "RESET" };
```

---

## 4. Error Response Format

All non-SSE error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description of what went wrong.",
    "available_tickers": ["OGDC", "TRG", "PSO", "LUCK", "ENGRO"]
  }
}
```

**Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNKNOWN_TICKER` | 404 | Ticker not in available stocks. Response includes `available_tickers`. |
| `REPORT_NOT_FOUND` | 404 | Report ID does not exist. |
| `LLM_UNAVAILABLE` | 503 | Both Claude and GPT-4o are unreachable. |
| `AGENT_TIMEOUT` | 200 (SSE) | Agent exceeded 60-second timeout. Sent as SSE error event. |
| `AGENT_MAX_ITERATIONS` | 200 (SSE) | Agent hit 15-iteration limit. Sent as SSE error event. |
| `ANALYSIS_IN_PROGRESS` | 409 | Another analysis for the same ticker is already running. |
| `RATE_LIMITED` | 429 | Too many requests. |
| `INTERNAL_ERROR` | 500 | Unexpected server error. |

---

## 5. SSE Connection Lifecycle

### 5.1 Normal Flow

```
Frontend                          Backend
   │                                 │
   │  POST /api/v1/analyze/OGDC     │
   │ ──────────────────────────────► │
   │                                 │ Agent starts
   │  data: {"type":"reasoning"...}  │
   │ ◄────────────────────────────── │
   │                                 │
   │  data: {"type":"tool_call"...}  │
   │ ◄────────────────────────────── │
   │                                 │
   │  data: {"type":"observation"..} │
   │ ◄────────────────────────────── │
   │                                 │
   │  ... (4-8 iterations) ...       │
   │                                 │
   │  data: {"type":"complete"...}   │
   │ ◄────────────────────────────── │
   │                                 │ Stream ends
   │  (Frontend closes connection)   │
   │                                 │
```

### 5.2 Error Flow

```
Frontend                          Backend
   │                                 │
   │  POST /api/v1/analyze/XYZ      │
   │ ──────────────────────────────► │
   │                                 │
   │  HTTP 404                       │
   │  {"error": {"code": "..."}}     │
   │ ◄────────────────────────────── │
   │                                 │
```

### 5.3 Mid-Stream Error

```
Frontend                          Backend
   │                                 │
   │  POST /api/v1/analyze/OGDC     │
   │ ──────────────────────────────► │
   │                                 │
   │  data: {"type":"reasoning"...}  │
   │ ◄────────────────────────────── │
   │                                 │
   │  data: {"type":"tool_call"...}  │
   │ ◄────────────────────────────── │
   │                                 │ LLM timeout
   │  data: {"type":"error"...}      │
   │ ◄────────────────────────────── │
   │                                 │ Stream ends
   │  (Frontend closes connection)   │
   │                                 │
```

### 5.4 Recovery

If the frontend's SSE connection drops mid-stream:

1. The backend continues running the agent to completion and stores the report.
2. The frontend can poll `GET /api/v1/reports?ticker=OGDC&limit=1` to check if the report completed.
3. If the report exists, fetch it via `GET /api/v1/reports/{id}` and display the result.

### 5.5 Frontend SSE Implementation Note

Since `EventSource` API does not support `POST` requests, the frontend must use `fetch()` with `ReadableStream` to consume the SSE stream:

```typescript
const response = await fetch(`${API_URL}/api/v1/analyze/${ticker}`, {
  method: "POST",
  headers: { "Accept": "text/event-stream" },
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split("\n");

  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const data = JSON.parse(line.slice(6));
      // Dispatch to state reducer
    }
  }
}
```

---

## 6. CORS Configuration

Backend must include these headers on all responses:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Accept
Access-Control-Max-Age: 3600
```

FastAPI implementation:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 7. Rate Limiting

| Endpoint | Limit |
|----------|-------|
| `POST /analyze/{ticker}` | 5 requests per minute |
| `GET /reports*` | 30 requests per minute |
| `GET /stocks*` | 30 requests per minute |

Rate limit headers on every response:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1707580260
```

---

*This is the definitive API contract. Backend implements it. Frontend consumes it. Any changes require updating this document and notifying both teams.*

*Reference: [PRD.md](PRD.md) Section 4 for feature requirements. [Backend TECH_SPEC.md](backend-docs/TECH_SPEC.md) for implementation details. [Frontend TECH_SPEC.md](frontend-docs/TECH_SPEC.md) for SSE consumption details.*
