# MarketLens Backend — Implementation Plan

**Document 6 of 12** | Backend-specific

---

## 1. Architecture Diagram

```
                         ┌──────────────────────────────────┐
                         │           FastAPI App             │
                         │           (main.py)               │
                         │                                    │
                         │  POST /analyze/{ticker} ──► SSE   │
                         │  GET  /reports          ──► JSON  │
                         │  GET  /reports/{id}     ──► JSON  │
                         │  GET  /reports/{id}/pdf ──► PDF   │
                         │  GET  /stocks           ──► JSON  │
                         │  GET  /stocks/{t}/summary ► JSON  │
                         │  GET  /health           ──► JSON  │
                         └──────────────┬───────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────────┐
                         │         Agent Core                │
                         │    (agents/analyst_agent.py)      │
                         │                                    │
                         │    System Prompt + ReAct Loop      │
                         │    ┌────────┐    ┌────────┐       │
                         │    │ REASON │───►│  ACT   │       │
                         │    │(Claude │    │ (Call  │       │
                         │    │ thinks)│◄───│  tool) │       │
                         │    └────────┘    └────────┘       │
                         │         │            │             │
                         │         │       ┌────▼─────┐      │
                         │         └───────│ OBSERVE  │      │
                         │                 │(Tool     │      │
                         │                 │ returns) │      │
                         │                 └──────────┘      │
                         └──────────────┬───────────────────┘
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                    ┌─────────────────┐  ┌──────────────────┐
                    │  LLM Client     │  │  Tool Dispatcher  │
                    │  (utils/        │  │  (agents/         │
                    │   llm_client.py)│  │   tool_registry.py│
                    │                 │  │                    │
                    │  Claude Sonnet  │  │  T1: load_data    │
                    │  ─── or ───     │  │  T2: indicator    │
                    │  GPT-4o         │  │  T3: patterns     │
                    │  (fallback)     │  │  T4: levels       │
                    └─────────────────┘  │  T5: index_cmp    │
                                         │  T6: sector_cmp   │
                                         │  T7: volume       │
                                         │  T8: chart        │
                                         └──────────────────┘
                                                  │
                                    ┌─────────────┴──────────────┐
                                    ▼                            ▼
                          ┌──────────────────┐     ┌──────────────────┐
                          │  PDF Generator   │     │     SQLite       │
                          │  (utils/         │     │   (database.py)  │
                          │   pdf_generator) │     │                  │
                          │                  │     │  reports table   │
                          │  Jinja2 + fpdf2  │     │  agent_runs tbl  │
                          └──────────────────┘     └──────────────────┘
```

---

## 2. Module Specifications

### 2.1 `agents/analyst_agent.py` — THE CORE

This is the heart of MarketLens. It implements the ReAct (Reason + Act) loop using Anthropic's tool_use API.

**Responsibilities:**
- Manage the conversation with Claude/GPT-4o
- Send messages with tool definitions
- Parse tool_use blocks from responses
- Dispatch tool calls to actual Python functions
- Return tool_result messages to the LLM
- Stream each step as an `AgentStep` for SSE
- Handle termination: `end_turn`, max iterations, timeout
- Handle errors: tool failures, LLM errors, malformed responses

**Key Function:**

```python
async def run_analyst_agent(
    ticker: str,
    max_iterations: int = 15,
    timeout_seconds: int = 60
) -> AsyncGenerator[AgentStep, None]:
    """
    Run the analyst agent for a given ticker.
    Yields AgentStep objects for SSE streaming.
    Final yield is type="complete" with full analysis.
    """
```

**Flow:**

1. Initialize messages with system prompt + user message ("Analyze {ticker} on PSX")
2. Enter loop (max `MAX_ITERATIONS` iterations):
   a. Call `llm_client.create_message(messages, tools)`
   b. Parse response content blocks
   c. For each `text` block: yield `AgentStep(type="reasoning")`
   d. For each `tool_use` block:
      - yield `AgentStep(type="tool_call")`
      - Execute tool via `tool_registry.dispatch(name, input)`
      - yield `AgentStep(type="observation")`
      - Append tool_result to messages
   e. If `stop_reason == "end_turn"`: parse final response, yield `AgentStep(type="complete")`, return
3. If loop exits without end_turn: force compile partial analysis

**Error Handling:**
- Tool raises exception → return error string to agent → agent adapts ("Data unavailable, proceeding with other evidence")
- LLM timeout → retry once → switch to fallback provider → if still fails, yield error step
- Malformed agent output JSON → attempt partial parse → yield what's usable

---

### 2.2 `agents/tool_registry.py`

**Responsibilities:**
- Define all 8 tools in Anthropic tool_use JSON schema format
- Map tool names to Python functions
- Validate inputs before calling tools
- Format outputs for agent consumption

**Structure:**

```python
TOOL_DEFINITIONS: list[dict]  # Anthropic tool schemas

TOOL_DISPATCH: dict[str, Callable] = {
    "load_stock_data": data_tools.load_stock_data,
    "calculate_indicator": indicator_tools.calculate_indicator,
    "detect_patterns": pattern_tools.detect_patterns,
    "find_support_resistance": level_tools.find_support_resistance,
    "compare_with_index": comparison_tools.compare_with_index,
    "compare_with_sector": comparison_tools.compare_with_sector,
    "analyze_volume": volume_tools.analyze_volume,
    "generate_chart": chart_tools.generate_chart,
}

async def dispatch(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return formatted result string."""
```

---

### 2.3 `tools/data_tools.py`

**Function: `load_stock_data(ticker: str, period: str) -> dict`**

- Reads CSV from `data/{ticker}.csv`
- Filters to requested period (1M, 3M, 6M, 1Y)
- Computes: current price, price change (absolute + %), period high/low, average volume, 52-week range (if data available)
- Returns last 5 days of OHLCV data
- Includes human-readable summary

**Output Example:**

```json
{
  "ticker": "OGDC",
  "period": "6M",
  "current_price": 118.50,
  "price_change": -23.50,
  "change_percent": -16.55,
  "period_high": 142.00,
  "period_low": 112.00,
  "avg_volume": 5200000,
  "data_points": 126,
  "last_5_days": [
    {"date": "2026-02-10", "open": 120.0, "high": 121.5, "low": 117.8, "close": 118.5, "volume": 5800000}
  ],
  "summary": "OGDC: Current PKR 118.50, down 16.6% over 6M. Range: 112-142. Avg volume: 5.2M shares/day."
}
```

---

### 2.4 `tools/indicator_tools.py`

**Function: `calculate_indicator(ticker: str, indicator: str, params: dict) -> dict`**

- Loads price data from CSV
- Uses `pandas-ta` library for calculations
- Returns computed value + human-readable interpretation

**Supported Indicators:**

| Indicator | Default Params | Interpretation Logic |
|-----------|---------------|---------------------|
| RSI | `period=14` | <30: oversold, >70: overbought, 30-70: neutral |
| SMA | `period=50` | Price above/below SMA, distance from SMA |
| EMA | `period=20` | Price above/below EMA, crossover detection |
| MACD | `fast=12, slow=26, signal=9` | Histogram positive/negative, signal crossover |
| Bollinger | `period=20, std=2` | Price near upper/lower band, bandwidth |
| ATR | `period=14` | Volatility level (high/medium/low vs historical) |
| VWAP | — | Price above/below VWAP |
| Stochastic | `k=14, d=3` | <20: oversold, >80: overbought |
| OBV | — | Trend direction, divergence with price |
| ADX | `period=14` | <20: no trend, 20-40: trend, >40: strong trend |
| Williams %R | `period=14` | <-80: oversold, >-20: overbought |
| CCI | `period=20` | <-100: oversold, >100: overbought |

**Output Example (RSI):**

```json
{
  "indicator": "RSI",
  "params": {"period": 14},
  "value": 32.1,
  "interpretation": "RSI(14) = 32.1 — Oversold territory (below 30 is deeply oversold). Current RSI suggests selling pressure may be exhausting, potential reversal zone.",
  "data": {
    "current": 32.1,
    "previous": 35.4,
    "trend": "declining"
  }
}
```

---

### 2.5 `tools/pattern_tools.py`

**Function: `detect_patterns(ticker: str, pattern_type: str) -> dict`**

- `pattern_type`: `"candlestick"`, `"chart"`, or `"both"`
- Scans recent price data for recognizable patterns
- Returns patterns with confidence scores and implications

**Candlestick Patterns Detected:**
Doji, Hammer, Inverted Hammer, Engulfing (bullish/bearish), Morning Star, Evening Star, Three White Soldiers, Three Black Crows, Harami

**Chart Patterns Detected:**
Double Top/Bottom, Head & Shoulders, Triangle (ascending/descending/symmetrical), Flag, Wedge, Channel

**Output Example:**

```json
{
  "pattern_type": "both",
  "candlestick_patterns": [
    {
      "name": "Bearish Engulfing",
      "date": "2026-02-07",
      "confidence": 0.78,
      "implication": "BEARISH",
      "description": "Large red candle engulfing previous green candle — bearish reversal signal"
    }
  ],
  "chart_patterns": [
    {
      "name": "Descending Triangle",
      "start_date": "2026-01-15",
      "end_date": "2026-02-10",
      "confidence": 0.65,
      "implication": "BEARISH",
      "description": "Lower highs with flat support at 115 — typically breaks down"
    }
  ],
  "summary": "1 bearish candlestick pattern and 1 bearish chart pattern detected. Both suggest continued downward pressure."
}
```

---

### 2.6 `tools/level_tools.py`

**Function: `find_support_resistance(ticker: str, method: str) -> dict`**

- `method`: `"pivot"`, `"fibonacci"`, or `"both"`
- Pivot: classic pivot point calculation from recent data
- Fibonacci: retracement levels from recent swing high/low

**Output Example:**

```json
{
  "method": "both",
  "pivot_levels": {
    "r2": 135.2,
    "r1": 128.3,
    "pivot": 123.5,
    "s1": 115.0,
    "s2": 108.2
  },
  "fibonacci_levels": {
    "0.0_high": 142.0,
    "0.236": 134.9,
    "0.382": 130.5,
    "0.5": 127.0,
    "0.618": 123.5,
    "1.0_low": 112.0
  },
  "key_support": [115.0, 108.2],
  "key_resistance": [128.3, 135.2],
  "current_price": 118.5,
  "summary": "Nearest support at 115.0 (pivot S1), just 3 points below current price. Nearest resistance at 128.3 (pivot R1). Fibonacci 61.8% retracement at 123.5."
}
```

---

### 2.7 `tools/comparison_tools.py`

**Function: `compare_with_index(ticker: str, period: str) -> dict`**

- Compares stock performance with KSE-100 over the specified period
- Returns relative performance, correlation, beta

**Output Example:**

```json
{
  "ticker": "OGDC",
  "index": "KSE-100",
  "period": "3M",
  "stock_return": -12.3,
  "index_return": 1.5,
  "relative_performance": -13.8,
  "correlation": 0.42,
  "summary": "OGDC underperformed KSE-100 by 13.8% over 3 months. KSE-100 gained 1.5% while OGDC declined 12.3%. Low correlation (0.42) suggests stock-specific factors driving the decline."
}
```

**Function: `compare_with_sector(ticker: str) -> dict`**

- Reads peers from `config.json`
- Compares 1-month performance across sector

**Output Example:**

```json
{
  "ticker": "OGDC",
  "sector": "Energy",
  "period": "1M",
  "rankings": [
    {"ticker": "PPL", "return": -1.2, "rank": 1},
    {"ticker": "PSO", "return": -3.5, "rank": 2},
    {"ticker": "MARI", "return": -5.1, "rank": 3},
    {"ticker": "OGDC", "return": -8.7, "rank": 4}
  ],
  "sector_avg_return": -4.6,
  "relative_to_sector": -4.1,
  "summary": "OGDC ranks last among Energy peers with -8.7% return vs sector average of -4.6%. Underperforming sector by 4.1 percentage points."
}
```

---

### 2.8 `tools/volume_tools.py`

**Function: `analyze_volume(ticker: str, period: str) -> dict`**

- Analyzes volume trends, unusual activity, price-volume divergence

**Output Example:**

```json
{
  "ticker": "OGDC",
  "period": "1M",
  "avg_volume_20d": 5200000,
  "recent_volume": 5800000,
  "volume_ratio": 1.12,
  "volume_trend": "increasing",
  "up_day_avg_volume": 4100000,
  "down_day_avg_volume": 6300000,
  "volume_price_divergence": false,
  "unusual_volume_days": [
    {"date": "2026-02-03", "volume": 8900000, "ratio": 1.71, "price_change": -3.2}
  ],
  "summary": "Volume trending 12% above 20-day average. Down days see 54% more volume than up days — selling pressure dominates. One unusual volume day on Feb 3 (1.7x average) coincided with a -3.2% drop."
}
```

---

### 2.9 `tools/chart_tools.py`

**Function: `generate_chart(ticker: str, period: str, overlays: list[str], annotations: list[str], style: str) -> dict`**

- Uses `mplfinance` to generate a candlestick chart
- Applies overlays specified by the agent (SMA, EMA, Bollinger, S/R zones)
- TradingView-inspired dark theme
- Returns Base64-encoded PNG

**Overlay Types:**
- `SMA_{period}` — Simple Moving Average line
- `EMA_{period}` — Exponential Moving Average line
- `bollinger` — Bollinger Bands (upper, lower, middle)
- `support_resistance` — Horizontal lines at key levels
- `vwap` — Volume Weighted Average Price line

**Annotation Types:**
- `current_price` — Horizontal dashed line at current price
- `rsi_oversold_zone` — RSI sub-panel with oversold zone highlighted
- `macd_crossover` — MACD sub-panel with crossover marked
- `volume_spike` — Volume bars with spikes highlighted

**Output:**

```json
{
  "chart_base64": "iVBORw0KGgo...",
  "chart_path": "output/charts/OGDC_20260210_143012.png",
  "dimensions": {"width": 1200, "height": 800},
  "dpi": 150,
  "overlays_applied": ["SMA_200", "support_resistance"],
  "annotations_applied": ["current_price"]
}
```

---

### 2.10 `utils/pdf_generator.py`

**Function: `generate_pdf(report_data: AgentResult, chart_base64: str, reasoning_trace: list[AgentStep]) -> str`**

- Uses Jinja2 to render `templates/report.html` with all analysis data
- Converts HTML to PDF using fpdf2 or Playwright
- Returns path to generated PDF file

**PDF Sections:**
1. **Header** — MarketLens logo, report date, ticker, stock name
2. **Executive Summary** — Signal badge, confidence, thesis (1 sentence), summary (2–3 sentences)
3. **Chart** — Embedded candlestick chart (Base64 decoded)
4. **Detailed Analysis** — Trend, Momentum, Key Levels, Volume Context, Market Context
5. **Key Levels Table** — Support, Resistance, Stop Loss, Target
6. **Evidence Chain** — Numbered list of findings
7. **Risk Factors** — Bulleted list
8. **Agent Reasoning Summary** — Condensed version of the reasoning trace
9. **Disclaimer** — Standard financial disclaimer

---

### 2.11 `utils/llm_client.py`

**Responsibilities:**
- Abstract away the difference between Anthropic and OpenAI APIs
- Provide a unified `create_message()` interface
- Handle provider fallback (Claude → GPT-4o)
- Convert tool definitions between formats

**Key Functions:**

```python
async def create_message(
    messages: list[dict],
    tools: list[dict],
    system: str,
    model: str = None,
    temperature: float = 0.3,
    max_tokens: int = 4096
) -> LLMResponse:
    """
    Send messages to LLM with tools.
    Tries primary provider, falls back to secondary on failure.
    """
```

**Fallback Logic:**
1. Try Claude (Anthropic API) with 10-second timeout
2. If timeout/error → log warning → retry once
3. If second failure → switch to GPT-4o (OpenAI API)
4. Convert tool definitions from Anthropic format to OpenAI function-calling format
5. Convert response back to unified format
6. If both fail → raise `LLMUnavailableError`

---

### 2.12 `models.py`

All Pydantic models as defined in [API_CONTRACT.md](../../docs/API_CONTRACT.md) Section 3.1.

---

### 2.13 `database.py`

**Tables:**

```sql
CREATE TABLE reports (
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

CREATE TABLE agent_runs (
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
```

**Key Functions:**

```python
async def init_db() -> None: ...
async def save_report(report: ReportDetail) -> None: ...
async def get_reports(limit: int = 10, ticker: str = None) -> list[ReportSummary]: ...
async def get_report(report_id: str) -> ReportDetail | None: ...
async def save_agent_step(report_id: str, step: AgentStep) -> None: ...
```

---

## 3. Configuration Files

### 3.1 `data/config.json`

```json
{
  "stocks": {
    "OGDC": {
      "name": "Oil & Gas Development Company",
      "sector": "Energy",
      "peers": ["PSO", "PPL", "MARI"],
      "seed_support": [115, 108],
      "seed_resistance": [128, 142]
    },
    "TRG": {
      "name": "TRG Pakistan",
      "sector": "Technology",
      "peers": ["SYS", "AVN"],
      "seed_support": [125, 118],
      "seed_resistance": [155, 170]
    },
    "PSO": {
      "name": "Pakistan State Oil",
      "sector": "Energy",
      "peers": ["OGDC", "PPL", "MARI"],
      "seed_support": [195, 185],
      "seed_resistance": [225, 240]
    },
    "LUCK": {
      "name": "Lucky Cement",
      "sector": "Cement",
      "peers": ["DGKC", "MLCF", "KOHC"],
      "seed_support": [750, 720],
      "seed_resistance": [810, 850]
    },
    "ENGRO": {
      "name": "Engro Corporation",
      "sector": "Conglomerate",
      "peers": ["DAWOOD", "ICI"],
      "seed_support": [300, 285],
      "seed_resistance": [340, 360]
    }
  },
  "sectors": {
    "Energy": ["OGDC", "PSO", "PPL", "MARI"],
    "Technology": ["TRG", "SYS", "AVN"],
    "Cement": ["LUCK", "DGKC", "MLCF", "KOHC"],
    "Conglomerate": ["ENGRO", "DAWOOD", "ICI"]
  },
  "index": {
    "ticker": "KSE100",
    "name": "KSE-100 Index"
  }
}
```

### 3.2 `.env` Variables

See [ENV_SETUP.md](ENV_SETUP.md) for complete documentation.

### 3.3 `chart_styles.json` (optional)

```json
{
  "dark": {
    "base_mpl_style": "dark_background",
    "marketcolors": {
      "candle": {"up": "#26a69a", "down": "#ef5350"},
      "edge": {"up": "#26a69a", "down": "#ef5350"},
      "wick": {"up": "#26a69a", "down": "#ef5350"},
      "ohlc": {"up": "#26a69a", "down": "#ef5350"},
      "volume": {"up": "#26a69a80", "down": "#ef535080"},
      "vcdopcod": false
    },
    "rc_params": {
      "figure.facecolor": "#131722",
      "axes.facecolor": "#131722",
      "axes.edgecolor": "#363A45",
      "axes.labelcolor": "#D1D4DC",
      "xtick.color": "#787B86",
      "ytick.color": "#787B86",
      "grid.color": "#1E222D"
    },
    "overlay_colors": {
      "sma_50": "#F7A21B",
      "sma_200": "#2196F3",
      "ema_20": "#E040FB",
      "bollinger_upper": "#78909C",
      "bollinger_lower": "#78909C",
      "support": "#26a69a",
      "resistance": "#ef5350",
      "vwap": "#FF9800"
    }
  }
}
```

---

## 4. Error Handling Strategy

### 4.1 LLM Errors

| Error | Action |
|-------|--------|
| Anthropic API timeout (>10s) | Retry once → fallback to GPT-4o |
| Anthropic 429 (rate limit) | Wait 2s → retry → fallback to GPT-4o |
| Anthropic 500 (server error) | Fallback to GPT-4o immediately |
| OpenAI fallback also fails | Yield error SSE event → partial analysis if possible |
| Malformed LLM response | Log → retry once → if still malformed, yield error |

### 4.2 Tool Errors

| Error | Action |
|-------|--------|
| CSV file missing | Return `"Data unavailable for {ticker}"` → agent adapts |
| pandas-ta calculation fails | Return `"Unable to calculate {indicator}"` → agent uses other indicators |
| mplfinance chart fails | Return `"Chart generation failed"` → report generated without chart |
| Division by zero / NaN | Catch → return `"Insufficient data for calculation"` |

### 4.3 Agent Loop Errors

| Error | Action |
|-------|--------|
| Max iterations (15) reached | Force-compile available evidence into partial report |
| Timeout (60s) reached | Cancel LLM call → compile partial report |
| Agent refuses to use tools | After 3 reasoning-only iterations, inject reminder |
| Agent produces invalid JSON | Regex extraction → parse subsections → compile best-effort report |

---

## 5. Implementation Order

| Priority | Module | Depends On | Day |
|----------|--------|-----------|-----|
| 1 | `data_tools.py` | CSV files | Day 1 |
| 2 | `indicator_tools.py` | `data_tools` | Day 1 |
| 3 | `pattern_tools.py` | `data_tools` | Day 1 |
| 4 | `level_tools.py` | `data_tools` | Day 1 |
| 5 | `comparison_tools.py` | `data_tools`, config.json | Day 1 |
| 6 | `volume_tools.py` | `data_tools` | Day 1 |
| 7 | `chart_tools.py` | `data_tools`, chart_styles | Day 1 |
| 8 | `tool_registry.py` | All tools | Day 1 |
| 9 | `llm_client.py` | API keys | Day 1 |
| 10 | `analyst_agent.py` | `tool_registry`, `llm_client` | Day 1 |
| 11 | `main.py` (SSE endpoint) | `analyst_agent` | Day 2 |
| 12 | `models.py` | None | Day 1 |
| 13 | `database.py` | `models` | Day 2 |
| 14 | `pdf_generator.py` | `models`, Jinja2 template | Day 2 |
| 15 | REST endpoints | `database` | Day 3 |
| 16 | Docker | Everything | Day 3 |

---

*Reference: [TECH_SPEC.md](TECH_SPEC.md) for detailed tool schemas and system prompt. [ENV_SETUP.md](ENV_SETUP.md) for setup instructions. [API_CONTRACT.md](../../docs/API_CONTRACT.md) for endpoint specifications.*
