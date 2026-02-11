# MarketLens Backend

**An AI Analyst Agent powered by FastAPI and Claude's tool_use API**

MarketLens Backend is the engine behind MarketLens — it runs an autonomous AI agent that analyzes Pakistani stocks like a senior technical analyst. The agent uses a ReAct (Reason + Act) loop with 8 analytical tools to produce professional technical analysis reports with transparent reasoning.

---

## Architecture

```
HTTP Request ──► FastAPI Router ──► Agent Core (ReAct Loop)
                                        ↕ (tool_use API)
                                  Claude Sonnet / GPT-4o
                                        ↕
                                  Tool Dispatcher
                               ┌──┬──┬──┬──┬──┬──┬──┬──┐
                               T1 T2 T3 T4 T5 T6 T7 T8
                               └──┴──┴──┴──┴──┴──┴──┴──┘
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                        SSE Stream           PDF Generator
                       (to Frontend)              │
                                                  ▼
                                              SQLite DB
```

The agent is **not a pipeline**. It doesn't run the same indicators on every stock. It reasons about the data, decides what to investigate next, and adapts its analysis path based on what it discovers.

---

## Agent's Toolkit

The AI analyst has 8 tools at its disposal. It decides which to use, in what order, and with what parameters.

| # | Tool | Description | Example Use |
|---|------|-------------|-------------|
| 1 | `load_stock_data` | Load OHLCV price data with summary stats | Always called first — assesses the big picture |
| 2 | `calculate_indicator` | Calculate any of 12+ technical indicators | RSI, MACD, Bollinger, ADX — agent picks what's relevant |
| 3 | `detect_patterns` | Scan for candlestick and chart patterns | Doji, Hammer, Head & Shoulders, Flags |
| 4 | `find_support_resistance` | Identify key price levels | Pivot points, Fibonacci retracement |
| 5 | `compare_with_index` | Compare performance vs KSE-100 | Is this stock-specific or market-wide movement? |
| 6 | `compare_with_sector` | Compare with sector peers | How is this stock vs its peers? |
| 7 | `analyze_volume` | Volume trend, unusual activity, divergence | Confirms or contradicts price signals |
| 8 | `generate_chart` | Candlestick chart with agent-selected overlays | Chart reflects the specific analysis performed |

**Supported Indicators:** RSI, SMA, EMA, MACD, Bollinger Bands, ATR, VWAP, Stochastic, OBV, ADX, Williams %R, CCI

---

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key (required)
- OpenAI API key (optional, for fallback)

### Install

```bash
cd marketlens-backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Initialize Database

```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

### Run

```bash
uvicorn main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/api/v1/health`

---

## Project Structure

```
marketlens-backend/
├── main.py                     # FastAPI app, SSE endpoint, REST routes
├── models.py                   # Pydantic models (see API_CONTRACT.md)
├── database.py                 # SQLite setup, queries, report storage
├── agents/
│   ├── __init__.py
│   ├── analyst_agent.py        # THE CORE — ReAct loop, agent execution
│   └── tool_registry.py        # Tool definitions (Anthropic schema) + dispatch
├── tools/
│   ├── __init__.py
│   ├── data_tools.py           # load_stock_data — CSV reader, summary stats
│   ├── indicator_tools.py      # calculate_indicator — 12+ indicators via pandas-ta
│   ├── pattern_tools.py        # detect_patterns — candlestick/chart patterns
│   ├── level_tools.py          # find_support_resistance — pivots + Fibonacci
│   ├── comparison_tools.py     # compare_with_index, compare_with_sector
│   ├── volume_tools.py         # analyze_volume — trend, divergence
│   └── chart_tools.py          # generate_chart — mplfinance, Base64 PNG
├── utils/
│   ├── __init__.py
│   ├── pdf_generator.py        # Jinja2 + fpdf2/Playwright → branded PDF
│   └── llm_client.py           # Provider abstraction: Claude ↔ GPT-4o
├── templates/
│   └── report.html             # Jinja2 template for PDF generation
├── data/
│   ├── OGDC.csv                # OHLCV data
│   ├── TRG.csv
│   ├── PSO.csv
│   ├── LUCK.csv
│   ├── ENGRO.csv
│   ├── KSE100.csv              # KSE-100 index data
│   └── config.json             # Stock metadata, sectors, peers
├── docs/                       # Backend-specific documentation
│   ├── README.md               # This file
│   ├── IMPLEMENTATION_PLAN.md
│   ├── TECH_SPEC.md
│   └── ENV_SETUP.md
├── tests/
│   ├── test_tools.py           # Unit tests for each tool
│   └── test_agent.py           # Integration test for agent loop
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze/{ticker}` | Stream agent analysis via SSE |
| `GET` | `/api/v1/reports` | List past reports |
| `GET` | `/api/v1/reports/{id}` | Get full report detail |
| `GET` | `/api/v1/reports/{id}/pdf` | Download report PDF |
| `GET` | `/api/v1/stocks` | List available stocks |
| `GET` | `/api/v1/stocks/{ticker}/summary` | Quick stock summary (no agent) |
| `GET` | `/api/v1/health` | Health check |

Full specification: [API_CONTRACT.md](../../docs/API_CONTRACT.md)

---

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Claude API key |
| `OPENAI_API_KEY` | No | — | GPT-4o fallback API key |
| `MODEL_PRIMARY` | No | `claude-sonnet-4-20250514` | Primary LLM model |
| `MODEL_FALLBACK` | No | `gpt-4o` | Fallback LLM model |
| `MAX_AGENT_ITERATIONS` | No | `15` | Max ReAct loop iterations |
| `AGENT_TIMEOUT_SECONDS` | No | `60` | Agent execution timeout |
| `DEBUG` | No | `false` | Enable debug logging |
| `DATABASE_PATH` | No | `./data/marketlens.db` | SQLite database path |
| `DATA_DIR` | No | `./data` | CSV data directory |
| `PDF_OUTPUT_DIR` | No | `./output/pdfs` | PDF output directory |

### Stock Configuration (`data/config.json`)

```json
{
  "stocks": {
    "OGDC": {
      "name": "Oil & Gas Development Company",
      "sector": "Energy",
      "peers": ["PSO", "PPL", "MARI"],
      "seed_support": [115, 108],
      "seed_resistance": [128, 142]
    }
  },
  "sectors": {
    "Energy": ["OGDC", "PSO", "PPL", "MARI"],
    "Technology": ["TRG", "SYS", "AVN"],
    "Cement": ["LUCK", "DGKC", "MLCF"],
    "Conglomerate": ["ENGRO", "DAWOOD"]
  }
}
```

---

## Adding New Stocks

1. Download OHLCV CSV data and place in `data/` as `{TICKER}.csv`
2. CSV format: `Date,Open,High,Low,Close,Volume` (date format: `YYYY-MM-DD`)
3. Add entry to `data/config.json` with name, sector, peers, seed S/R levels
4. Restart the server

---

## Adding New Tools

1. Create the tool function in the appropriate `tools/*.py` file
2. Return a dict with structured data + human-readable interpretation
3. Add the Anthropic tool schema to `agents/tool_registry.py`
4. Add the tool name → function mapping to the dispatch table
5. The agent will automatically discover and use the new tool

---

## Testing

### Test Individual Tools

```bash
python -m tools.data_tools          # Test CSV loading
python -m tools.indicator_tools     # Test indicator calculations
python -m tools.chart_tools         # Test chart generation
```

### Test Agent (Terminal Mode)

```bash
python -m agents.analyst_agent OGDC
python -m agents.analyst_agent TRG
```

### Test SSE Endpoint

```bash
curl -N -X POST http://localhost:8000/api/v1/analyze/OGDC
```

### Run Unit Tests

```bash
pytest tests/ -v
```

---

## Docker

### Build

```bash
docker build -t marketlens-backend .
```

### Run

```bash
docker run -p 8000:8000 --env-file .env marketlens-backend
```

### Docker Compose (from project root)

```bash
docker compose up backend
```

---

*Reference: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for module specs, [TECH_SPEC.md](TECH_SPEC.md) for detailed technical spec, [ENV_SETUP.md](ENV_SETUP.md) for setup guide.*
