# MarketLens

**An AI analyst that thinks, not just calculates.**

MarketLens is an AI-powered stock analysis platform for the Pakistan Stock Exchange (PSX). It uses an autonomous agent with 8 analytical tools to produce professional technical analysis reports — with a live reasoning trace so you can watch it think.

---

## What Makes This Different

| Traditional AI Tools | MarketLens |
|---------------------|------------|
| Same template for every stock | Agent adapts analysis per stock |
| Black box — shows conclusion only | Live reasoning trace — watch the agent think |
| Hallucinated numbers | Every number computed from real data via tools |
| Chat response | Professional A4 PDF report |
| 2–4 hours per report (manual) | 15 seconds per report (automated) |

---

## Architecture

```
┌──────────────────────────┐          ┌──────────────────────────┐
│   marketlens-backend     │   API    │   marketlens-frontend    │
│   Python / FastAPI       │◄────────►│   Next.js / TypeScript   │
│                          │   SSE    │                          │
│   • AI Analyst Agent     │          │   • Live Reasoning Panel │
│   • 8 Analysis Tools     │          │   • PDF Report Viewer    │
│   • PDF Generator        │          │   • Report History       │
│   • Claude + GPT-4o      │          │   • Bloomberg Dark Theme │
│                          │          │                          │
│   Port: 8000             │          │   Port: 3000             │
└──────────────────────────┘          └──────────────────────────┘
```

Two independent sub-projects connected by a [REST + SSE API contract](docs/API_CONTRACT.md).

---

## Quick Start

### Prerequisites

- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- Anthropic API key (required)
- OpenAI API key (optional, for fallback)

### 1. Clone

```bash
git clone https://github.com/your-org/market-lens.git
cd market-lens
```

### 2. Backend

```bash
cd marketlens-backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY

uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd marketlens-frontend
npm install

cp .env.example .env.local
# Edit .env.local if backend is not on localhost:8000

npm run dev
```

### 4. Open

Navigate to [http://localhost:3000](http://localhost:3000)

### Docker Compose (Alternative)

```bash
cp .env.example .env
# Edit .env with API keys

docker compose up
```

---

## The Agent

The MarketLens analyst agent is not a pipeline — it's a genuine ReAct (Reason + Act) loop powered by Claude Sonnet. For each stock, the agent:

1. **Loads data** and assesses the big picture
2. **Decides** which indicators are most relevant for this specific stock
3. **Investigates** — running 4–8 tools, following the evidence
4. **Adapts** — if signals contradict, it digs deeper
5. **Concludes** — forms a thesis with a confidence level and evidence chain
6. **Generates** — professional chart and branded PDF report

Different stocks get different analysis paths because the agent reasons about what matters.

### The 8 Tools

| Tool | Purpose |
|------|---------|
| `load_stock_data` | Load OHLCV price data with summary statistics |
| `calculate_indicator` | Compute RSI, MACD, Bollinger, ADX, and 8 more indicators |
| `detect_patterns` | Scan for candlestick and chart patterns |
| `find_support_resistance` | Identify key levels via pivot points and Fibonacci |
| `compare_with_index` | Compare performance against KSE-100 |
| `compare_with_sector` | Compare with sector peers |
| `analyze_volume` | Volume trend analysis and divergence detection |
| `generate_chart` | Candlestick chart with agent-selected overlays |

---

## Stocks (MVP)

| Ticker | Company | Sector |
|--------|---------|--------|
| OGDC | Oil & Gas Development Company | Energy |
| TRG | TRG Pakistan | Technology |
| PSO | Pakistan State Oil | Energy |
| LUCK | Lucky Cement | Cement |
| ENGRO | Engro Corporation | Conglomerate |
| KSE100 | KSE-100 Index | Benchmark |

---

## Documentation

All documentation lives in the [`docs/`](docs/) directory. See the [Documentation Index](docs/INDEX.md) for a complete map.

### Project-Level

| Document | Description |
|----------|-------------|
| [PRD](docs/PRD.md) | Product requirements, personas, features, success metrics |
| [Hackathon Plan](docs/HACKATHON_PLAN.md) | 4-day sprint plan, hour-by-hour |
| [Demo Script](docs/DEMO_SCRIPT.md) | Demo flow, Q&A, backup plans |
| [API Contract](docs/API_CONTRACT.md) | Endpoint specs, SSE events, data models |
| [Index](docs/INDEX.md) | Complete documentation map with reading order |

### Backend

| Document | Description |
|----------|-------------|
| [README](docs/backend-docs/README.md) | Architecture, toolkit, quick start |
| [Implementation Plan](docs/backend-docs/IMPLEMENTATION_PLAN.md) | Module specs, function signatures |
| [Tech Spec](docs/backend-docs/TECH_SPEC.md) | System prompt, tool schemas, chart/PDF specs |
| [Env Setup](docs/backend-docs/ENV_SETUP.md) | Installation, config, Docker, troubleshooting |

### Frontend

| Document | Description |
|----------|-------------|
| [README](docs/frontend-docs/README.md) | Reasoning panel, component guide, styling |
| [Implementation Plan](docs/frontend-docs/IMPLEMENTATION_PLAN.md) | Component hierarchy, state management, SSE hook |
| [Tech Spec](docs/frontend-docs/TECH_SPEC.md) | Component interfaces, TypeScript types, responsive design |
| [Env Setup](docs/frontend-docs/ENV_SETUP.md) | Dependencies, Tailwind config, mock mode, Docker |

---

## Tech Stack

### Backend

| Technology | Purpose |
|-----------|---------|
| FastAPI | Web framework, SSE streaming |
| Anthropic SDK | Claude Sonnet tool_use API |
| OpenAI SDK | GPT-4o fallback |
| pandas / pandas-ta | Data processing, technical indicators |
| mplfinance | Candlestick chart generation |
| fpdf2 / Jinja2 | PDF report generation |
| SQLite / aiosqlite | Report storage |

### Frontend

| Technology | Purpose |
|-----------|---------|
| Next.js 14 | React framework (App Router) |
| TypeScript | Type safety |
| Tailwind CSS | Styling (dark theme) |
| react-pdf | Inline PDF viewing |

---

## License

*To be determined*

---

*Built for the [Hackathon Name] 2026. See [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for the pitch.*
