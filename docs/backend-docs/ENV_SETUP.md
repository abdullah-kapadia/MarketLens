# Document 8 of 12 -- Environment Setup & Configuration

## MarketLens Backend -- Complete Setup Guide

This document provides every step required to install, configure, and run the
MarketLens backend locally and in Docker. All commands, paths, and configuration
values are production-tested and copy-paste ready.

---

## 8.1 Prerequisites

### Required Software

| Software   | Minimum Version | Verify Command           |
|------------|-----------------|--------------------------|
| Python     | 3.11+           | `python --version`       |
| pip        | 23.0+           | `pip --version`          |
| git        | 2.30+           | `git --version`          |
| curl       | any             | `curl --version`         |

### Required API Keys

| Key                | Required | Source                                      |
|--------------------|----------|---------------------------------------------|
| Anthropic API Key  | Yes      | https://console.anthropic.com/settings/keys |
| OpenAI API Key     | No       | https://platform.openai.com/api-keys        |

**Anthropic API Key** -- This is the primary key used by the Claude tool_use
agent loop. Without it, the analysis engine will not start. You need at least a
tier that supports the `claude-sonnet-4-20250514` model (or whichever model
you configure as `MODEL_PRIMARY`).

**OpenAI API Key** -- Optional fallback. If the Anthropic API returns a 529
(overloaded) or 500 (server error), the agent can retry the request against
OpenAI's `gpt-4o` model. If you do not provide this key, the fallback path is
disabled and errors from Anthropic will be returned directly to the client.

### System Resources

- **RAM**: 512 MB minimum, 1 GB recommended (pandas holds stock data in memory)
- **Disk**: 100 MB for application + dependencies, plus space for generated PDFs
- **Network**: Outbound HTTPS to `api.anthropic.com` and optionally
  `api.openai.com`

---

## 8.2 Installation

### Step-by-Step

```bash
# 1. Clone the repository (if you have not already)
git clone https://github.com/your-org/marketlens.git
cd marketlens

# 2. Navigate to the backend directory
cd marketlens-backend

# 3. Create a Python virtual environment
python -m venv venv

# 4. Activate the virtual environment
# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On macOS / Linux:
source venv/bin/activate

# 5. Upgrade pip to latest
pip install --upgrade pip

# 6. Install all dependencies
pip install -r requirements.txt

# 7. Copy the environment template and fill in your keys
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 8. Edit .env and add your ANTHROPIC_API_KEY at minimum
# (See section 8.4 for full variable documentation)

# 9. Verify installation
python -c "import fastapi; import anthropic; import pandas; print('All imports OK')"
```

If step 9 prints `All imports OK`, your installation is correct.

---

## 8.3 requirements.txt

Save the following as `marketlens-backend/requirements.txt`:

```text
# ============================================================================
# MarketLens Backend -- Pinned Dependencies
# Python 3.11+ required
# Last updated: 2025-01-15
# ============================================================================

# --- Web Framework -----------------------------------------------------------
fastapi==0.115.6
uvicorn[standard]==0.34.0

# --- AI / LLM Clients -------------------------------------------------------
anthropic==0.42.0
openai==1.58.1

# --- Data & Analysis ---------------------------------------------------------
pandas==2.2.3
pandas-ta==0.3.14b1
numpy==1.26.4

# --- Charting & Visualization ------------------------------------------------
mplfinance==0.12.10b0
matplotlib==3.9.4

# --- Templating & PDF --------------------------------------------------------
jinja2==3.1.5
fpdf2==2.8.2

# --- Data Validation ---------------------------------------------------------
pydantic==2.10.4
pydantic-settings==2.7.1

# --- Environment & Config ----------------------------------------------------
python-dotenv==1.0.1

# --- Database ----------------------------------------------------------------
aiosqlite==0.20.0

# --- HTTP Client (async) -----------------------------------------------------
httpx==0.28.1

# --- SSE (Server-Sent Events) ------------------------------------------------
sse-starlette==2.2.1

# --- Testing -----------------------------------------------------------------
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
```

### Installing Exact Versions

```bash
pip install -r requirements.txt
```

### Verifying Key Packages

```bash
python -c "
import fastapi; print(f'FastAPI:     {fastapi.__version__}')
import anthropic; print(f'Anthropic:   {anthropic.__version__}')
import pandas; print(f'Pandas:      {pandas.__version__}')
import pandas_ta; print(f'Pandas-TA:   {pandas_ta.version}')
import mplfinance; print(f'mplfinance:  {mplfinance.__version__}')
import uvicorn; print(f'Uvicorn:     {uvicorn.__version__}')
"
```

---

## 8.4 .env.example

Save the following as `marketlens-backend/.env.example`. Every variable is
documented with its type, whether it is required, its default value, and its
purpose.

```dotenv
# ============================================================================
# MarketLens Backend -- Environment Configuration
# Copy this file to .env and fill in your values.
# Lines starting with # are comments.
# ============================================================================

# ----------------------------------------------------------------------------
# API KEYS
# ----------------------------------------------------------------------------

# ANTHROPIC_API_KEY
# Type:     string
# Required: YES
# Default:  (none)
# Purpose:  Authentication key for the Anthropic Claude API. Used by the
#           primary agent loop (tool_use) in agents/analyst_agent.py.
#           Obtain from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPENAI_API_KEY
# Type:     string
# Required: NO
# Default:  (none -- fallback disabled if not set)
# Purpose:  Authentication key for the OpenAI API. Used as a fallback when
#           the Anthropic API returns 529 (overloaded) or 500 (server error).
#           If not set, errors from Anthropic are returned directly to the
#           client without retry.
#           Obtain from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ----------------------------------------------------------------------------
# MODEL CONFIGURATION
# ----------------------------------------------------------------------------

# MODEL_PRIMARY
# Type:     string
# Required: NO
# Default:  claude-sonnet-4-20250514
# Purpose:  The primary Claude model used for the agentic analysis loop.
#           Must support tool_use. Recommended: claude-sonnet-4-20250514 for
#           best price/performance, or claude-opus-4-20250514 for highest quality.
MODEL_PRIMARY=claude-sonnet-4-20250514

# MODEL_FALLBACK
# Type:     string
# Required: NO
# Default:  gpt-4o
# Purpose:  The OpenAI model to use when the primary Anthropic model is
#           unavailable. Only used if OPENAI_API_KEY is set.
MODEL_FALLBACK=gpt-4o

# ----------------------------------------------------------------------------
# AGENT BEHAVIOR
# ----------------------------------------------------------------------------

# MAX_AGENT_ITERATIONS
# Type:     integer
# Required: NO
# Default:  15
# Purpose:  Maximum number of tool_use iterations the agent will perform in a
#           single analysis run. Each iteration is one Claude API call that may
#           invoke one or more tools. Higher values allow deeper analysis but
#           increase latency and cost. Range: 5-30.
MAX_AGENT_ITERATIONS=15

# AGENT_TIMEOUT_SECONDS
# Type:     integer
# Required: NO
# Default:  120
# Purpose:  Maximum wall-clock time (in seconds) for a single analysis run.
#           If the agent exceeds this limit, the run is terminated and a
#           partial result is returned. Range: 30-300.
AGENT_TIMEOUT_SECONDS=120

# ----------------------------------------------------------------------------
# APPLICATION SETTINGS
# ----------------------------------------------------------------------------

# DEBUG
# Type:     boolean (true/false)
# Required: NO
# Default:  false
# Purpose:  Enables debug mode. When true:
#           - FastAPI returns detailed error tracebacks in responses
#           - Agent logs every tool call and result to stdout
#           - CORS allows all origins (not safe for production)
#           Set to false in production.
DEBUG=false

# ----------------------------------------------------------------------------
# FILE PATHS
# ----------------------------------------------------------------------------

# DATABASE_PATH
# Type:     string (file path)
# Required: NO
# Default:  data/marketlens.db
# Purpose:  Path to the SQLite database file used for storing analysis
#           history, cached results, and session metadata. Relative paths
#           are resolved from the marketlens-backend/ directory.
DATABASE_PATH=data/marketlens.db

# DATA_DIR
# Type:     string (directory path)
# Required: NO
# Default:  data
# Purpose:  Directory containing stock CSV files and config.json. Each
#           stock's historical data is stored as {SYMBOL}.csv in this
#           directory. Relative paths are resolved from the
#           marketlens-backend/ directory.
DATA_DIR=data

# PDF_OUTPUT_DIR
# Type:     string (directory path)
# Required: NO
# Default:  output/reports
# Purpose:  Directory where generated PDF analysis reports are saved.
#           The directory is created automatically if it does not exist.
#           Relative paths are resolved from the marketlens-backend/
#           directory.
PDF_OUTPUT_DIR=output/reports
```

### Minimal .env for Development

If you just want to get started quickly, the only required variable is:

```dotenv
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
DEBUG=true
```

Everything else will use sensible defaults.

---

## 8.5 Data Setup

### Directory Structure

```
marketlens-backend/
  data/
    config.json          # Stock metadata, sectors, peer mappings
    OGDC.csv             # Oil & Gas Development Company
    TRG.csv              # TRG Pakistan (Systems Limited)
    PSO.csv              # Pakistan State Oil
    LUCK.csv             # Lucky Cement
    ENGRO.csv            # Engro Corporation
    KSE100.csv           # KSE-100 Index (benchmark)
    marketlens.db        # SQLite database (auto-created)
```

### CSV Format Specification

Every stock CSV file must follow this exact format:

**Filename**: `{SYMBOL}.csv` (uppercase symbol, e.g., `OGDC.csv`)

**Columns** (in order):

| Column | Type    | Format      | Description                    |
|--------|---------|-------------|--------------------------------|
| Date   | string  | YYYY-MM-DD  | Trading date                   |
| Open   | float   | 2 decimals  | Opening price (PKR)            |
| High   | float   | 2 decimals  | Highest price of the day (PKR) |
| Low    | float   | 2 decimals  | Lowest price of the day (PKR)  |
| Close  | float   | 2 decimals  | Closing price (PKR)            |
| Volume | integer | no decimals | Number of shares traded        |

**Example** (`OGDC.csv`):

```csv
Date,Open,High,Low,Close,Volume
2024-01-02,98.50,101.20,97.80,100.75,3245000
2024-01-03,100.80,102.50,99.90,101.30,2876000
2024-01-04,101.50,103.00,100.20,102.80,4102000
2024-01-05,102.90,104.75,102.10,104.50,3567000
```

**Rules**:
- The CSV must have a header row with exactly these column names.
- Dates must be sorted in ascending order (oldest first).
- No missing values. If a trading day has no data, omit the row entirely.
- Decimal separator is a period (`.`), not a comma.
- No thousands separator in the Volume column.
- Encoding: UTF-8 without BOM.
- Line endings: LF (`\n`) or CRLF (`\r\n`) are both accepted.
- Minimum 60 trading days of data recommended for technical indicators to
  produce meaningful results (some indicators like 200-day SMA require 200+
  data points).

### config.json Structure

Save the following as `marketlens-backend/data/config.json`:

```json
{
  "stocks": {
    "OGDC": {
      "name": "Oil & Gas Development Company",
      "sector": "Energy - Exploration & Production",
      "exchange": "PSX",
      "currency": "PKR",
      "csv_file": "OGDC.csv",
      "description": "Pakistan's largest exploration and production company by market capitalization."
    },
    "TRG": {
      "name": "TRG Pakistan Limited",
      "sector": "Technology & Communication",
      "exchange": "PSX",
      "currency": "PKR",
      "csv_file": "TRG.csv",
      "description": "Technology holding company with investments in Ibex Global and Afiniti."
    },
    "PSO": {
      "name": "Pakistan State Oil",
      "sector": "Energy - Oil Marketing",
      "exchange": "PSX",
      "currency": "PKR",
      "csv_file": "PSO.csv",
      "description": "Largest oil marketing company in Pakistan by market share."
    },
    "LUCK": {
      "name": "Lucky Cement Limited",
      "sector": "Materials - Cement",
      "exchange": "PSX",
      "currency": "PKR",
      "csv_file": "LUCK.csv",
      "description": "Largest cement manufacturer in Pakistan by production capacity."
    },
    "ENGRO": {
      "name": "Engro Corporation Limited",
      "sector": "Conglomerate",
      "exchange": "PSX",
      "currency": "PKR",
      "csv_file": "ENGRO.csv",
      "description": "Diversified conglomerate with interests in fertilizers, foods, energy, and petrochemicals."
    }
  },
  "indices": {
    "KSE100": {
      "name": "KSE-100 Index",
      "description": "Benchmark index of the Pakistan Stock Exchange comprising the top 100 companies by market capitalization.",
      "csv_file": "KSE100.csv"
    }
  },
  "sectors": {
    "Energy - Exploration & Production": {
      "stocks": ["OGDC"],
      "benchmark": "KSE100"
    },
    "Energy - Oil Marketing": {
      "stocks": ["PSO"],
      "benchmark": "KSE100"
    },
    "Technology & Communication": {
      "stocks": ["TRG"],
      "benchmark": "KSE100"
    },
    "Materials - Cement": {
      "stocks": ["LUCK"],
      "benchmark": "KSE100"
    },
    "Conglomerate": {
      "stocks": ["ENGRO"],
      "benchmark": "KSE100"
    }
  },
  "peers": {
    "OGDC": ["PSO", "ENGRO"],
    "TRG": [],
    "PSO": ["OGDC", "ENGRO"],
    "LUCK": ["ENGRO"],
    "ENGRO": ["OGDC", "PSO", "LUCK"]
  },
  "defaults": {
    "analysis_period_days": 365,
    "chart_style": "charles",
    "indicators": ["SMA_20", "SMA_50", "SMA_200", "RSI_14", "MACD", "BB_20"]
  }
}
```

### Validating Your Data Setup

```bash
# Verify all required files exist
python -c "
import os, json

data_dir = 'data'
required_files = ['config.json', 'OGDC.csv', 'TRG.csv', 'PSO.csv', 'LUCK.csv', 'ENGRO.csv', 'KSE100.csv']

print('Checking data directory...')
for f in required_files:
    path = os.path.join(data_dir, f)
    exists = os.path.isfile(path)
    size = os.path.getsize(path) if exists else 0
    status = f'OK ({size:,} bytes)' if exists else 'MISSING'
    print(f'  {f:15s} {status}')

# Validate config.json
with open(os.path.join(data_dir, 'config.json')) as fh:
    config = json.load(fh)
    print(f'\nStocks configured: {len(config[\"stocks\"])}')
    for symbol in config['stocks']:
        print(f'  {symbol}: {config[\"stocks\"][symbol][\"name\"]}')
print('\nData setup validation complete.')
"
```

---

## 8.6 Database Initialization

MarketLens uses SQLite (via `aiosqlite`) to store analysis history, cached
results, and session metadata. The database must be initialized before first
use.

### Initialize the Database

```bash
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

This creates the SQLite database file at the path specified by `DATABASE_PATH`
(default: `data/marketlens.db`) with the following tables:

| Table              | Purpose                                              |
|--------------------|------------------------------------------------------|
| `analysis_runs`    | Stores metadata for each analysis run (symbol, timestamp, status, duration) |
| `tool_calls`       | Logs every tool invocation made by the agent during a run |
| `analysis_results` | Stores the final analysis output (text, charts, indicators) |
| `sessions`         | Tracks SSE client sessions and connection state      |

### Verify Database Creation

```bash
python -c "
import sqlite3, os
db_path = 'data/marketlens.db'
if os.path.isfile(db_path):
    conn = sqlite3.connect(db_path)
    tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
    print(f'Database: {db_path}')
    print(f'Tables:   {[t[0] for t in tables]}')
    conn.close()
else:
    print(f'ERROR: Database not found at {db_path}')
    print('Run: python -c \"from database import init_db; import asyncio; asyncio.run(init_db())\"')
"
```

### Reset the Database

To drop all data and recreate tables from scratch:

```bash
# Delete the existing database
del data\marketlens.db                  # Windows
# rm data/marketlens.db                 # macOS / Linux

# Recreate it
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## 8.7 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload --port 8000
```

This starts the server at `http://localhost:8000` with:
- **Auto-reload**: The server restarts automatically when you save a `.py` file.
- **Single worker**: One process, suitable for development.

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --no-access-log
```

Flags:
- `--host 0.0.0.0` -- Listen on all interfaces (required for Docker).
- `--workers 4` -- Spawn 4 worker processes. Adjust based on CPU cores.
- `--no-access-log` -- Suppress per-request access logs for performance.

### Verify the Server Is Running

```bash
# Health check endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","model":"claude-sonnet-4-20250514"}

# API documentation (auto-generated by FastAPI)
# Open in browser: http://localhost:8000/docs
```

### Available Endpoints

| Method | Path                         | Description                          |
|--------|------------------------------|--------------------------------------|
| GET    | `/health`                    | Health check                         |
| GET    | `/docs`                      | Swagger UI (interactive API docs)    |
| GET    | `/redoc`                     | ReDoc (alternative API docs)         |
| GET    | `/api/v1/stocks`             | List all configured stocks           |
| GET    | `/api/v1/stocks/{symbol}`    | Get stock metadata                   |
| POST   | `/api/v1/analyze/{symbol}`   | Start analysis (returns SSE stream)  |
| GET    | `/api/v1/reports/{run_id}`   | Download PDF report                  |
| GET    | `/api/v1/history`            | List past analysis runs              |

---

## 8.8 Docker

### Dockerfile

Save as `marketlens-backend/Dockerfile`:

```dockerfile
# ============================================================================
# MarketLens Backend -- Production Dockerfile
# Base: Python 3.11 slim (Debian Bookworm)
# ============================================================================

FROM python:3.11-slim AS base

# -- Metadata ----------------------------------------------------------------
LABEL maintainer="MarketLens Team"
LABEL description="MarketLens AI-agentic stock analysis backend"
LABEL version="1.0.0"

# -- System dependencies -----------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# -- Application user (non-root) ---------------------------------------------
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# -- Working directory --------------------------------------------------------
WORKDIR /app

# -- Install Python dependencies first (layer caching) -----------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -- Copy application code ----------------------------------------------------
COPY . .

# -- Create output directories ------------------------------------------------
RUN mkdir -p /app/output/reports /app/data && \
    chown -R appuser:appuser /app

# -- Switch to non-root user --------------------------------------------------
USER appuser

# -- Expose port --------------------------------------------------------------
EXPOSE 8000

# -- Health check -------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# -- Entrypoint ---------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### .dockerignore

Save as `marketlens-backend/.dockerignore`:

```
venv/
__pycache__/
*.pyc
.env
.git/
.gitignore
*.md
output/reports/*.pdf
data/marketlens.db
.pytest_cache/
.mypy_cache/
```

### Build and Run

```bash
# Build the image
docker build -t marketlens-backend:latest .

# Run the container
docker run -d \
    --name marketlens-api \
    -p 8000:8000 \
    -e ANTHROPIC_API_KEY=sk-ant-api03-your-key-here \
    -e DEBUG=false \
    -v marketlens-data:/app/data \
    -v marketlens-reports:/app/output/reports \
    marketlens-backend:latest

# Verify it started
docker logs marketlens-api

# Check health
curl http://localhost:8000/health

# Stop and remove
docker stop marketlens-api && docker rm marketlens-api
```

### Docker Compose

Save as `marketlens-backend/docker-compose.yml`:

```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: marketlens-api
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - MODEL_PRIMARY=${MODEL_PRIMARY:-claude-sonnet-4-20250514}
      - MODEL_FALLBACK=${MODEL_FALLBACK:-gpt-4o}
      - MAX_AGENT_ITERATIONS=${MAX_AGENT_ITERATIONS:-15}
      - AGENT_TIMEOUT_SECONDS=${AGENT_TIMEOUT_SECONDS:-120}
      - DEBUG=${DEBUG:-false}
      - DATABASE_PATH=data/marketlens.db
      - DATA_DIR=data
      - PDF_OUTPUT_DIR=output/reports
    volumes:
      - ./data:/app/data
      - marketlens-reports:/app/output/reports
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

volumes:
  marketlens-reports:
    driver: local
```

### Docker Compose Commands

```bash
# Start the stack (build if needed)
docker compose up -d --build

# View logs (follow mode)
docker compose logs -f api

# Stop the stack
docker compose down

# Stop and remove volumes (DELETES DATA)
docker compose down -v

# Rebuild without cache
docker compose build --no-cache
```

---

## 8.9 Testing Tools

### Test Individual Tools

Each tool module in `tools/` can be run standalone to verify it works in
isolation. These scripts load sample data from the `data/` directory and
print results to stdout.

```bash
# Test indicator calculation tools (SMA, RSI, MACD, Bollinger Bands)
python -m tools.indicator_tools
# Expected: Prints calculated indicators for sample data

# Test charting tools (generates a chart image)
python -m tools.chart_tools
# Expected: Saves a test chart to output/test_chart.png

# Test data loading tools
python -m tools.data_tools
# Expected: Prints loaded DataFrame info and sample rows

# Test report generation tools
python -m tools.report_tools
# Expected: Generates a test PDF in output/reports/
```

### Test the Agent in Terminal Mode

Run a full analysis cycle from the command line without starting the web
server. This invokes the same agent loop used by the API endpoint.

```bash
# Analyze OGDC
python -m agents.analyst_agent OGDC

# Analyze with verbose output (shows every tool call)
python -m agents.analyst_agent OGDC --verbose

# Analyze a different stock
python -m agents.analyst_agent LUCK

# Analyze with a custom iteration limit
python -m agents.analyst_agent ENGRO --max-iterations 10
```

Expected output:
```
[Agent] Starting analysis for OGDC...
[Agent] Iteration 1: Calling tool 'load_stock_data' with args {'symbol': 'OGDC'}
[Agent] Iteration 2: Calling tool 'calculate_indicators' with args {'symbol': 'OGDC', 'indicators': ['SMA_20', 'SMA_50', 'RSI_14', 'MACD']}
[Agent] Iteration 3: Calling tool 'generate_chart' with args {'symbol': 'OGDC', 'chart_type': 'candlestick'}
...
[Agent] Analysis complete. 7 iterations, 12.3 seconds.
[Agent] Result: OGDC shows bullish momentum with RSI at 62.4...
```

### Test the SSE Endpoint

Use `curl` to test the Server-Sent Events streaming endpoint directly:

```bash
# Basic SSE test (streams analysis events in real-time)
curl -N -X POST http://localhost:8000/api/v1/analyze/OGDC

# With headers for proper SSE handling
curl -N -X POST \
    -H "Accept: text/event-stream" \
    -H "Content-Type: application/json" \
    http://localhost:8000/api/v1/analyze/OGDC

# With request body options
curl -N -X POST \
    -H "Accept: text/event-stream" \
    -H "Content-Type: application/json" \
    -d '{"indicators": ["SMA_20", "RSI_14", "MACD"], "period_days": 180}' \
    http://localhost:8000/api/v1/analyze/TRG
```

Expected SSE output:
```
event: status
data: {"type": "status", "message": "Starting analysis for OGDC..."}

event: tool_call
data: {"type": "tool_call", "tool": "load_stock_data", "args": {"symbol": "OGDC"}}

event: tool_result
data: {"type": "tool_result", "tool": "load_stock_data", "result": {"rows": 248, "date_range": "2024-01-02 to 2024-12-31"}}

event: tool_call
data: {"type": "tool_call", "tool": "calculate_indicators", "args": {"symbol": "OGDC"}}

...

event: complete
data: {"type": "complete", "run_id": "abc-123", "analysis": "OGDC shows bullish momentum..."}
```

### Running the Full Test Suite with pytest

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_indicator_tools.py

# Run a specific test function
pytest tests/test_indicator_tools.py::test_rsi_calculation

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing

# Run only fast tests (skip integration tests that hit the API)
pytest -m "not integration"

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Test File Structure

```
marketlens-backend/
  tests/
    __init__.py
    conftest.py                  # Shared fixtures (sample DataFrames, mock API)
    test_data_tools.py           # Tests for data loading and validation
    test_indicator_tools.py      # Tests for technical indicator calculations
    test_chart_tools.py          # Tests for chart generation
    test_report_tools.py         # Tests for PDF report generation
    test_analyst_agent.py        # Tests for the agent loop (mocked API)
    test_api_endpoints.py        # Integration tests for FastAPI endpoints
    test_sse_streaming.py        # Tests for SSE event streaming
```

---

## 8.10 Troubleshooting

### Problem: `anthropic.AuthenticationError: Invalid API Key`

**Symptom**: The server starts but analysis requests fail with a 401 error.

**Cause**: The `ANTHROPIC_API_KEY` in your `.env` file is missing, empty,
or invalid.

**Solution**:

```bash
# 1. Verify the key is set in your environment
python -c "import os; key = os.getenv('ANTHROPIC_API_KEY', ''); print(f'Key length: {len(key)}, Prefix: {key[:12]}...' if key else 'KEY NOT SET')"

# 2. Verify the key works
python -c "
from anthropic import Anthropic
client = Anthropic()
msg = client.messages.create(model='claude-sonnet-4-20250514', max_tokens=10, messages=[{'role':'user','content':'hi'}])
print(f'API OK: {msg.content[0].text}')
"

# 3. If the key is not loaded, check your .env file
#    - Make sure .env is in the marketlens-backend/ directory (not a subdirectory)
#    - Make sure there are no quotes around the value: ANTHROPIC_API_KEY=sk-ant-...
#      (NOT ANTHROPIC_API_KEY="sk-ant-...")
#    - Make sure there are no trailing spaces or invisible characters
#    - Make sure python-dotenv is installed: pip install python-dotenv
```

---

### Problem: `FileNotFoundError: data/OGDC.csv not found`

**Symptom**: The agent fails on the first tool call (`load_stock_data`)
because it cannot find the CSV file.

**Cause**: CSV files are not in the expected directory, or `DATA_DIR` is
misconfigured.

**Solution**:

```bash
# 1. Check your current working directory
python -c "import os; print(os.getcwd())"
# Must be: .../marketlens-backend/

# 2. Check DATA_DIR configuration
python -c "import os; print(f'DATA_DIR = {os.getenv(\"DATA_DIR\", \"data\")}')"

# 3. List files in the data directory
python -c "
import os
data_dir = os.getenv('DATA_DIR', 'data')
if os.path.isdir(data_dir):
    files = os.listdir(data_dir)
    print(f'Files in {data_dir}/: {files}')
else:
    print(f'ERROR: Directory {data_dir}/ does not exist')
    print(f'Create it: mkdir {data_dir}')
"

# 4. Make sure you are running uvicorn from the marketlens-backend/ directory
cd marketlens-backend
uvicorn main:app --reload --port 8000
```

---

### Problem: `OSError: [Errno 48] Address already in use` (port 8000)

**Symptom**: Uvicorn fails to start because port 8000 is occupied.

**Solution**:

```bash
# Option 1: Use a different port
uvicorn main:app --reload --port 8001

# Option 2: Find and kill the process using port 8000

# On Windows:
netstat -ano | findstr :8000
# Note the PID in the last column, then:
taskkill /PID <pid> /F

# On macOS / Linux:
lsof -i :8000
kill -9 <pid>
```

---

### Problem: `ImportError: cannot import name 'ta' from 'pandas_ta'`

**Symptom**: The `calculate_indicators` tool fails with an import error
related to `pandas_ta`.

**Cause**: Version mismatch between `pandas` and `pandas_ta`, or
`pandas_ta` was not installed correctly.

**Solution**:

```bash
# 1. Check installed versions
pip show pandas pandas-ta

# 2. pandas-ta 0.3.14b1 requires pandas < 2.1 in some configurations.
#    If you see errors, try reinstalling:
pip uninstall pandas-ta -y
pip install pandas-ta==0.3.14b1

# 3. Verify the import works
python -c "import pandas_ta; print(f'pandas_ta version: {pandas_ta.version}')"

# 4. If the error persists, check for conflicting numpy versions:
pip show numpy
# pandas-ta requires numpy < 2.0. If you have numpy 2.x:
pip install numpy==1.26.4

# 5. Nuclear option: recreate the virtual environment
deactivate
rmdir /s /q venv          # Windows
# rm -rf venv              # macOS / Linux
python -m venv venv
venv\Scripts\activate.bat  # Windows
# source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

---

### Problem: `ModuleNotFoundError: No module named 'dotenv'`

**Symptom**: The application fails to start because `python-dotenv` is
not installed.

**Solution**:

```bash
# The package name on PyPI is python-dotenv, not dotenv
pip install python-dotenv

# If you accidentally installed the wrong package:
pip uninstall dotenv -y
pip install python-dotenv
```

---

### Problem: Charts are blank or have rendering errors

**Symptom**: Generated chart images are empty, show only axes, or fail
to save.

**Cause**: matplotlib backend issues, typically on headless servers or
Docker containers.

**Solution**:

```bash
# 1. Force the non-interactive backend (add to the top of chart_tools.py)
#    import matplotlib
#    matplotlib.use('Agg')

# 2. Verify matplotlib can render:
python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1,2,3], [1,4,9])
fig.savefig('test_plot.png')
print('Chart saved to test_plot.png')
"

# 3. In Docker, ensure no X11 dependencies are expected.
#    The Agg backend does not require a display server.
```

---

### Problem: SSE connection drops or times out

**Symptom**: The `curl -N` command or the frontend loses the SSE
connection partway through an analysis.

**Cause**: A proxy, load balancer, or network configuration is closing
idle connections.

**Solution**:

```bash
# 1. Increase AGENT_TIMEOUT_SECONDS in .env
AGENT_TIMEOUT_SECONDS=180

# 2. If behind nginx, add these directives:
#    proxy_buffering off;
#    proxy_read_timeout 300s;
#    proxy_send_timeout 300s;

# 3. If behind a cloud load balancer, increase the idle timeout
#    to at least 300 seconds.

# 4. Test with a longer timeout in curl:
curl -N --max-time 300 -X POST http://localhost:8000/api/v1/analyze/OGDC
```

---

### Problem: `sqlite3.OperationalError: database is locked`

**Symptom**: Concurrent analysis requests cause database lock errors.

**Cause**: SQLite does not handle high write concurrency well. Multiple
workers writing to the same database can trigger this.

**Solution**:

```bash
# 1. In development, use a single worker (the default with --reload):
uvicorn main:app --reload --port 8000

# 2. In production with multiple workers, configure WAL mode.
#    Add this to your database.py init_db() function:
#    await db.execute("PRAGMA journal_mode=WAL")
#    await db.execute("PRAGMA busy_timeout=5000")

# 3. Verify WAL mode is active:
python -c "
import sqlite3
conn = sqlite3.connect('data/marketlens.db')
mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
print(f'Journal mode: {mode}')  # Should print: wal
conn.close()
"
```

---

### Quick Diagnostic Script

Run this script to check your entire setup at once:

```bash
python -c "
import sys, os

print('=' * 60)
print('MarketLens Backend -- Environment Diagnostic')
print('=' * 60)

# Python version
v = sys.version_info
py_ok = v.major == 3 and v.minor >= 11
print(f'\n[{\"OK\" if py_ok else \"FAIL\"}] Python version: {sys.version.split()[0]} (need 3.11+)')

# Key packages
packages = ['fastapi', 'anthropic', 'openai', 'pandas', 'pandas_ta', 'mplfinance', 'uvicorn', 'httpx', 'aiosqlite', 'fpdf2', 'jinja2', 'pydantic', 'dotenv', 'sse_starlette']
print(f'\nPackage check:')
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  [OK]   {pkg}')
    except ImportError:
        print(f'  [FAIL] {pkg} -- not installed')

# Environment variables
print(f'\nEnvironment variables:')
api_key = os.getenv('ANTHROPIC_API_KEY', '')
print(f'  ANTHROPIC_API_KEY: {\"SET (\" + str(len(api_key)) + \" chars)\" if api_key else \"NOT SET\"}')
oai_key = os.getenv('OPENAI_API_KEY', '')
print(f'  OPENAI_API_KEY:    {\"SET (\" + str(len(oai_key)) + \" chars)\" if oai_key else \"NOT SET (fallback disabled)\"}')
print(f'  MODEL_PRIMARY:     {os.getenv(\"MODEL_PRIMARY\", \"claude-sonnet-4-20250514 (default)\")}')
print(f'  DEBUG:             {os.getenv(\"DEBUG\", \"false (default)\")}')

# Data files
data_dir = os.getenv('DATA_DIR', 'data')
print(f'\nData files ({data_dir}/):')
required = ['config.json', 'OGDC.csv', 'TRG.csv', 'PSO.csv', 'LUCK.csv', 'ENGRO.csv', 'KSE100.csv']
for f in required:
    path = os.path.join(data_dir, f)
    if os.path.isfile(path):
        size = os.path.getsize(path)
        print(f'  [OK]   {f} ({size:,} bytes)')
    else:
        print(f'  [FAIL] {f} -- not found')

# Database
db_path = os.getenv('DATABASE_PATH', os.path.join(data_dir, 'marketlens.db'))
if os.path.isfile(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    tables = [t[0] for t in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
    print(f'\n[OK]   Database: {db_path} (tables: {tables})')
    conn.close()
else:
    print(f'\n[WARN] Database not found at {db_path}')
    print(f'       Run: python -c \"from database import init_db; import asyncio; asyncio.run(init_db())\"')

print('\n' + '=' * 60)
print('Diagnostic complete.')
print('=' * 60)
"
```

---

*Document 8 of 12 -- MarketLens Project Documentation*
