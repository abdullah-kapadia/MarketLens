# MarketLens - Automated Stock Analyst

**An AI analyst that thinks, not just calculates.**

MarketLens is an AI-powered stock analysis platform for the Pakistan Stock Exchange (PSX). It uses an autonomous agent with 8 analytical tools to produce professional technical analysis reports — with a live reasoning trace so you can watch it think in real-time.

## ⚡ Quick Start (TL;DR)

```bash
# 1. Check prerequisites
check-prereqs.bat

# 2. Install dependencies (first time only)
cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# 3. Configure API keys
# Edit backend/.env and add your OPENAI_API_KEY

# 4. Start everything
start-dev.bat        # Windows (double-click)
# OR
python start-dev.py  # All platforms
```

**Then open:** http://localhost:8080 🎉

---

## ✨ What Makes This Different

| Traditional AI Tools | MarketLens |
|---------------------|------------|
| Same template for every stock | Agent adapts analysis per stock |
| Black box — shows conclusion only | **Live process log** — watch the agent think step-by-step |
| Hallucinated numbers | Every number computed from **real data** via tools |
| Chat response | Professional A4 **PDF report** with charts |
| 2–4 hours per report (manual) | **15 seconds** per report (automated) |
| Generic analysis | Context-aware analysis with KSE-100 & sector comparison |

---

## 🚀 Key Features

### 1. **Live Process Log Window**
Watch the AI analyst work in real-time:
- 🧠 **Reasoning**: See what the agent is thinking
- 🔧 **Tool Calls**: Track which analysis tools are being used
- 📊 **Observations**: View results from each tool
- ⏱️ **Timestamps**: Monitor performance with iteration counters
- ✅ **Completion**: Get execution time and tool call statistics

### 2. **Real-Time Technical Analysis**
All indicators calculated from **actual historical data**:
- **Moving Averages** (SMA 9, 50, 200)
- **RSI** (14-period Relative Strength Index)
- **Bollinger Bands** (20-period, 2σ)
- **Support/Resistance Levels** (Pivot Points & Fibonacci)
- **Chart Patterns** (Doji, Double Bottom, Rising Channel, etc.)
- **Volume Analysis** (Unusual volume detection, divergence)

### 3. **Professional Reports**
- 📄 Interactive candlestick charts with indicators
- 📈 Support/resistance visualization
- 📋 Detailed analysis sections (Trend, Momentum, Levels, Volume)
- 🎯 Trading levels (Entry, Target, Stop Loss)
- ⚠️ Risk factors and evidence chain
- 💾 PDF export for offline viewing

### 4. **Intelligent Agent**
- 🤖 Powered by GPT-4o (primary) with Claude Sonnet fallback
- 🔄 ReAct (Reason + Act) loop for adaptive analysis
- 📊 8 specialized analysis tools
- 🎯 Stock-specific analysis paths
- 📝 Professional report generation

---

## 🏗️ Architecture

```
┌──────────────────────────┐          ┌──────────────────────────┐
│   Backend (FastAPI)      │   API    │   Frontend (React)       │
│   Python 3.12            │◄────────►│   Vite + TypeScript      │
│                          │   SSE    │                          │
│   • AI Analyst Agent     │          │   • Live Process Log     │
│   • 8 Analysis Tools     │          │   • Interactive Charts   │
│   • PDF Generator        │          │   • Report Preview       │
│   • GPT-4o + Claude      │          │   • Stock Selector       │
│   • SQLite Database      │          │   • Minimalist Dark UI   │
│                          │          │                          │
│   Port: 8000             │          │   Port: 8080             │
└──────────────────────────┘          └──────────────────────────┘
```

**Communication**: REST API + Server-Sent Events (SSE) for real-time streaming

---

## 🛠️ The 8 Analysis Tools

| Tool | Purpose | Example Output |
|------|---------|----------------|
| `load_stock_data` | Load OHLCV price data with summary statistics | Current: PKR 281.09, +23.7% (6M) |
| `calculate_indicator` | Compute RSI, MACD, Bollinger, ADX, and more | RSI = 66.0, Bullish momentum |
| `detect_patterns` | Scan for candlestick and chart patterns | Doji, Double Bottom, Rising Channel |
| `find_support_resistance` | Identify key levels via pivot points & Fibonacci | Support: 247.35, Resistance: 286.28 |
| `compare_with_index` | Compare performance against KSE-100 | Underperformed by 8.2% over 6M |
| `compare_with_sector` | Compare with sector peers | Ranks #1 in Energy with 3.7% return |
| `analyze_volume` | Volume trend analysis and divergence detection | 1.43x average, decreasing trend |
| `generate_chart` | Candlestick chart with agent-selected overlays | PNG chart with SMA, BB, RSI |

---

## 📦 Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Web framework with async support |
| **sse-starlette** | Server-Sent Events streaming |
| **OpenAI SDK** | GPT-4o integration (primary LLM) |
| **Anthropic SDK** | Claude Sonnet (fallback LLM) |
| **pandas** | Data processing and manipulation |
| **pandas-ta** | Technical indicator calculations |
| **mplfinance** | Candlestick chart generation |
| **matplotlib** | Chart visualization |
| **fpdf2** | PDF report generation |
| **Jinja2** | PDF templating |
| **aiosqlite** | Async SQLite database |
| **pydantic** | Data validation and serialization |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 18** | UI library |
| **Vite** | Build tool and dev server |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |
| **Recharts** | Interactive chart components |
| **Axios** | HTTP client |
| **React Router** | Client-side routing |
| **Lucide React** | Icon library |

---

## 🚀 Quick Start

### ⚡ One-Command Startup (Recommended)

**Windows users:** Just double-click `start-dev.bat` or run:

```bash
# Check prerequisites first (optional)
check-prereqs.bat

# Start both servers with one command
start-dev.bat
```

**All platforms:** Or use the Python launcher:

```bash
python start-dev.py
```

This will:
- ✅ Check all prerequisites
- ✅ Verify dependencies are installed
- ✅ Start backend on port 8000
- ✅ Start frontend on port 8080
- ✅ Show combined logs from both servers

**Then:** Open http://localhost:8080 in your browser! 🎉

---

### 📋 Manual Setup (First Time Only)

#### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **OpenAI API key** (primary, required)
- **Anthropic API key** (fallback, optional)

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/market-lens.git
cd Market
```

#### 2. Install Dependencies

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Back to root
cd ..
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Back to root
cd ..
```

#### 3. Configure Environment

Create `backend/.env` with your API keys:

```env
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional (fallback)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Model Configuration
MODEL_PRIMARY=gpt-4o
MODEL_FALLBACK=claude-sonnet-4-20250514

# Agent Settings
MAX_AGENT_ITERATIONS=15
AGENT_TIMEOUT_SECONDS=120
```

#### 4. Start Development Servers

**Option A: One-Command Startup (Recommended)**
```bash
# Windows
start-dev.bat

# All platforms
python start-dev.py
```

**Option B: Manual (Two Terminals)**

*Terminal 1 - Backend:*
```bash
cd backend
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

*Terminal 2 - Frontend:*
```bash
cd frontend
npm run dev
```

#### 5. Usage

1. Open **http://localhost:8080** in your browser
2. Select a stock ticker (OGDC, TRG, PSO, etc.)
3. Click **"INITIALIZE REPORT SEQUENCE"**
4. Watch the **Process Log** as the AI analyst works:
   - `[#1] REASONING: Analyzing current price trends...`
   - `[#2] TOOL CALL: calculate_rsi(period=14)`
   - `[#2] OBSERVATION: {"rsi": 66.0, "signal": "overbought"}`
   - `ANALYSIS COMPLETE in 15.23s (12 tool calls)`
5. View the generated report with interactive charts
6. Download PDF for offline viewing

---

### 🛠️ Startup Scripts

Four convenient scripts to launch the development environment:

| Script | Platform | Description |
|--------|----------|-------------|
| **`start-dev.bat`** | Windows | Double-click to start both servers in separate windows |
| **`start-dev.ps1`** | Windows | PowerShell version with colored output |
| **`start-dev.py`** | All | Cross-platform launcher with combined logs |
| **`check-prereqs.bat`** | Windows | Verify all prerequisites are installed |

**Features:**
- ✅ Automatic prerequisite checking (Python, Node.js, npm)
- ✅ Dependency verification (venv, node_modules)
- ✅ Environment validation (.env file)
- ✅ Concurrent server startup
- ✅ Clear error messages with fix suggestions
- ✅ Graceful shutdown (Ctrl+C stops both servers)

**Recommended Workflow:**
```bash
# First time setup
check-prereqs.bat        # Verify everything is installed

# Every day
start-dev.bat            # One command to start everything
```

---

## 📊 Available Stocks (PSX)

| Ticker | Company | Sector |
|--------|---------|--------|
| **OGDC** | Oil & Gas Development Company | Energy |
| **TRG** | TRG Pakistan | Technology |
| **PSO** | Pakistan State Oil | Energy |
| **LUCK** | Lucky Cement | Cement |
| **ENGRO** | Engro Corporation | Conglomerate |

Data source: Historical CSV files in `data/` directory

---

## 🎯 How It Works

### The AI Agent Loop

1. **Initialize** → Load stock data and market context
2. **Reason** → Agent decides which analysis is most relevant
3. **Act** → Calls appropriate tools (RSI, patterns, volume, etc.)
4. **Observe** → Processes tool results
5. **Adapt** → If signals conflict, investigates further
6. **Conclude** → Forms thesis with confidence level
7. **Generate** → Creates chart and PDF report
8. **Stream** → Sends all steps to frontend via SSE

### Real-Time Streaming

All agent steps are streamed to the frontend via **Server-Sent Events (SSE)**:

```typescript
// Backend sends:
event: tool_call
data: {"type": "tool_call", "tool_name": "calculate_rsi", "tool_input": {...}}

event: observation
data: {"type": "observation", "result": {"rsi": 66.0, ...}}

event: complete
data: {"type": "complete", "report_id": "rpt_abc123", "execution_time_ms": 15230}
```

The **Process Log** window displays these events in real-time with:
- ✅ Completion indicators
- ⏱️ Timestamps
- 🔢 Iteration numbers
- 📊 Tool arguments and results

---

## 🔧 Configuration

### Backend Environment Variables

```env
# API Keys
OPENAI_API_KEY=sk-proj-...                    # Required
ANTHROPIC_API_KEY=sk-ant-...                  # Optional fallback

# Model Configuration
MODEL_PRIMARY=gpt-4o                          # Primary LLM
MODEL_FALLBACK=claude-sonnet-4-20250514       # Fallback LLM

# Agent Settings
MAX_AGENT_ITERATIONS=15                       # Max reasoning loops
AGENT_TIMEOUT_SECONDS=120                     # Timeout per analysis

# Paths
DATABASE_PATH=data/marketlens.db              # SQLite database
DATA_DIR=data                                 # CSV data directory
PDF_OUTPUT_DIR=output/reports                 # PDF output directory

# Debug
DEBUG=false                                   # Enable debug logging
```

### Frontend Environment Variables

```env
# Backend API URL (optional, defaults to http://localhost:8000)
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
Market/
├── backend/
│   ├── agents/
│   │   ├── analyst_agent.py         # Main AI agent with ReAct loop
│   │   └── tool_registry.py         # Tool definitions and dispatcher
│   ├── tools/
│   │   ├── data_tools.py            # Data loading and chart generation
│   │   ├── chart_tools.py           # Candlestick chart creation
│   │   └── indicator_tools.py       # Technical indicators
│   ├── utils/
│   │   ├── llm_client.py            # Unified LLM client (OpenAI + Anthropic)
│   │   └── pdf_generator.py         # PDF report generation
│   ├── main.py                      # FastAPI app and SSE endpoints
│   ├── models.py                    # Pydantic data models
│   ├── database.py                  # SQLite database operations
│   ├── requirements.txt             # Python dependencies
│   └── .env                         # Environment configuration (create this)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StockSelector.tsx   # Stock picker dropdown
│   │   │   ├── TerminalLog.tsx     # Live process log window
│   │   │   ├── DocumentPreview.tsx # Report display
│   │   │   └── TechnicalChart.tsx  # Interactive candlestick chart
│   │   ├── lib/
│   │   │   ├── api.ts              # API client with SSE support
│   │   │   └── api-types.ts        # TypeScript type definitions
│   │   └── pages/
│   │       └── Index.tsx           # Main application page
│   ├── package.json                # Node dependencies
│   └── vite.config.ts              # Vite configuration
├── data/
│   ├── OGDC.csv                    # Stock price data
│   ├── TRG.csv                     # Stock price data
│   ├── PSO.csv                     # Stock price data
│   └── config.json                 # Stock metadata
├── start-dev.bat                   # 🚀 One-click startup (Windows)
├── start-dev.ps1                   # 🚀 PowerShell startup script
├── start-dev.py                    # 🚀 Cross-platform startup script
├── check-prereqs.bat               # ✅ Prerequisites checker
└── README.md                       # This file
```

**Key Files:**
- **`start-dev.bat`** - Double-click to start both servers (Windows)
- **`start-dev.py`** - Cross-platform Python launcher
- **`check-prereqs.bat`** - Verify Python, Node.js, dependencies installed
- **`backend/.env`** - API keys and configuration (you need to create this)
- **`data/*.csv`** - Historical stock price data (OHLCV format)

---

## 🐛 Troubleshooting

### Issue: "Both LLM providers unavailable"

**Solution**:
1. Check that API keys are set in `backend/.env`
2. Uncomment the `ANTHROPIC_API_KEY` line if using Claude fallback
3. Verify keys are valid (not expired)
4. Restart backend server after updating `.env`

### Issue: "No module named 'sse_starlette'"

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Process log not showing events

**Solution**:
1. Hard refresh browser (Ctrl+F5)
2. Check browser console for errors
3. Verify backend is running on port 8000
4. Check Network tab for SSE EventStream

### Issue: Chart shows "0 chart data points"

**Solution**:
This was a Bollinger Bands column name mismatch. Already fixed in latest version. Make sure you're running the updated `tools/data_tools.py`.

### Issue: Report not displaying after analysis completes

**Solution**:
Field name mismatch between backend and frontend. Already fixed in latest version. The backend now sends:
- `tool_name` (not `tool`)
- `tool_input` (not `args`)
- `report_id` (not `run_id`)

---

## 🎨 UI Features

### Process Log Window
- **Real-time streaming** of agent reasoning
- **Iteration tracking** with `[#N]` prefixes
- **Color-coded indicators**:
  - ✅ Green checkmark for completed steps
  - ⏩ Amber arrow for active step
- **Formatted output**:
  - Tool calls: `calculate_rsi(period=14)`
  - Observations: Truncated to 200 chars for readability
  - Completion summary: Execution time and tool count

### Interactive Charts
- **Candlestick visualization** with real OHLCV data
- **Technical indicators overlay** (SMA, Bollinger Bands)
- **Support/Resistance levels** marked on chart
- **Responsive design** with Recharts library

### Report Preview
- **Professional layout** inspired by financial reports
- **Thesis statement** with signal (BULLISH/BEARISH/NEUTRAL)
- **Confidence level** (HIGH/MEDIUM/LOW)
- **Evidence chain** with checkmarks
- **Risk factors** with warning symbols
- **Key price levels** in tabular format

---

## 📝 API Endpoints

### `POST /api/v1/analyze/{ticker}`
Stream analysis steps via Server-Sent Events

**Response**: SSE stream with events:
- `reasoning` → Agent's thinking
- `tool_call` → Tool invocation
- `observation` → Tool result
- `complete` → Analysis finished
- `error` → Analysis failed

### `GET /api/v1/stocks`
List available stocks

### `GET /api/v1/stocks/{ticker}/summary`
Get stock summary data

### `GET /api/v1/reports`
List past reports

### `GET /api/v1/reports/{report_id}`
Get report details

### `GET /api/v1/reports/{report_id}/pdf`
Download PDF report

### `GET /api/v1/health`
Health check with system info

---

## 🔬 Development

### Running Tests
```bash
cd backend
pytest
```

### Code Style
```bash
# Backend
black . --check
mypy .

# Frontend
npm run lint
npm run type-check
```

### Building for Production
```bash
# Frontend
npm run build
npm run preview
```

---

## Acknowledgments

- **LLM Providers**: OpenAI (GPT-4o) and Anthropic (Claude Sonnet)
- **Technical Indicators**: pandas-ta library
- **Chart Visualization**: mplfinance and Recharts
- **UI Inspiration**: Bloomberg Terminal aesthetic

---

## License

*To be determined*

---

## Future Enhancements

- [ ] Add more PSX stocks (expand beyond MVP 5)
- [ ] Historical report comparison
- [ ] Custom date range selection
- [ ] Export to Excel/CSV
- [ ] Email report delivery
- [ ] Real-time price updates
- [ ] Alert system for price targets
- [ ] Portfolio analysis (multi-stock)
- [ ] Backtesting simulation
- [ ] Mobile app

---

**Built with ❤️ for the Pakistan Stock Exchange community**

*Watch the AI analyst think in real-time at [http://localhost:8080](http://localhost:8080)*
