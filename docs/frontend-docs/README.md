# MarketLens Frontend

**Bloomberg-style dashboard with live AI reasoning trace**

MarketLens Frontend is a Next.js 14 application that provides a professional, dark-themed dashboard for viewing AI-generated stock analysis. The centerpiece is the **Reasoning Panel** — a real-time display of the AI agent's thinking process, streamed via Server-Sent Events as the agent analyzes Pakistani stocks.

---

## Key Feature: Live Reasoning Trace

The Reasoning Panel is what makes MarketLens unique. When a user clicks "Analyze," they watch the AI agent think in real-time:

```
┌──────────────────────────────────────────────────────────┐
│  Agent Reasoning                                          │
│  ─────────────                                            │
│  🧠 Loading OGDC data for 6 months...                    │
│                                                           │
│  📊 load_stock_data → OGDC: PKR 118.50, -16.6% (6M)     │
│                                                           │
│  🧠 Price has declined significantly. Checking RSI...     │
│                                                           │
│  📊 calculate_indicator → RSI(14) = 32.1 (Oversold)      │
│                                                           │
│  🧠 Oversold RSI. Need to verify support holds...        │
│                                                           │
│  📊 find_support_resistance → Support at 115, price 118  │
│                                                           │
│  👁 Only 3 points above support. Checking volume...      │
│                                                           │
│  ⏳ Analyzing...                                          │
└──────────────────────────────────────────────────────────┘
```

Each step appears live as the agent works, with smooth animations and auto-scrolling.

---

## Screenshots

> *Placeholder — replace with actual screenshots after build*

| View | Description |
|------|-------------|
| Dashboard (empty state) | Dark theme, stock list sidebar, "Select a stock" prompt |
| Analysis in progress | Reasoning panel filling with live steps, loading indicator |
| Analysis complete | Report viewer with PDF, QuickStats panel, signal badge |
| Report history | Sidebar showing past analyses with color-coded signal badges |

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend running at `http://localhost:8000` (see [backend README](../backend-docs/README.md))

### Install

```bash
cd marketlens-frontend
npm install
```

### Configure

```bash
cp .env.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL if backend is not on localhost:8000
```

### Run

```bash
npm run dev
# Open http://localhost:3000
```

---

## Project Structure

```
marketlens-frontend/
├── app/
│   ├── layout.tsx              # Root layout — dark theme, Inter font, metadata
│   ├── page.tsx                # Main dashboard page (single-page app)
│   └── globals.css             # Tailwind imports + custom dark theme styles
├── components/
│   ├── Dashboard.tsx           # Main layout: sidebar + content area
│   ├── Sidebar.tsx             # Left sidebar wrapper (logo, stock list, history)
│   ├── StockList.tsx           # Clickable stock items with price/change
│   ├── ReportHistory.tsx       # Past reports with signal badges (🟢🔴🟡)
│   ├── StockHeader.tsx         # Selected stock: ticker, name, price, sector
│   ├── AnalyzeButton.tsx       # Trigger button: idle → streaming → complete
│   ├── ReasoningPanel.tsx      # THE KEY COMPONENT — live SSE consumer
│   ├── ReasoningStep.tsx       # Individual step renderer (4 types)
│   ├── ReportViewer.tsx        # react-pdf inline PDF viewer
│   ├── QuickStats.tsx          # Signal pill, confidence, support/resistance
│   ├── EmptyState.tsx          # "Select a stock to begin analysis"
│   └── LoadingState.tsx        # Loading indicators and skeletons
├── hooks/
│   └── useAgentStream.ts       # Custom hook — SSE consumer + state management
├── lib/
│   ├── api.ts                  # API client functions (fetch wrappers)
│   └── types.ts                # TypeScript interfaces (matches backend models)
├── docs/
│   ├── README.md               # This file
│   ├── IMPLEMENTATION_PLAN.md
│   ├── TECH_SPEC.md
│   └── ENV_SETUP.md
├── public/
│   └── logo.svg                # MarketLens logo
├── package.json
├── tailwind.config.ts          # Dark theme config, custom colors
├── tsconfig.json
├── next.config.js
├── Dockerfile
├── .env.example
└── .gitignore
```

---

## Component Guide

| Component | Role | Key Behavior |
|-----------|------|-------------|
| `Dashboard` | Main layout container | Splits into sidebar (280px) + main content (flex) |
| `Sidebar` | Left panel | Contains StockList at top, ReportHistory below |
| `StockList` | Stock selector | Fetches from GET /stocks, click selects, shows price/change |
| `ReportHistory` | Past reports list | Fetches from GET /reports, signal badges, click loads report |
| `StockHeader` | Stock info bar | Shows selected stock details, sector tag |
| `AnalyzeButton` | Analysis trigger | States: idle (blue), streaming (pulsing), complete (green) |
| `ReasoningPanel` | Live reasoning display | Consumes SSE stream, renders steps, auto-scrolls |
| `ReasoningStep` | Step renderer | 4 variants: reasoning (🧠), tool_call (📊), observation (👁), complete (✅) |
| `ReportViewer` | PDF display | react-pdf renderer + download button |
| `QuickStats` | Analysis summary | Signal pill, confidence, key levels — shows after completion |
| `EmptyState` | Initial prompt | Shown before any analysis — "Select a stock" |
| `LoadingState` | Loading indicators | Skeleton screens and pulsing dots |

---

## API Integration

The frontend connects to the backend via REST API + Server-Sent Events.

| Frontend Action | Backend Endpoint | Method |
|----------------|-----------------|--------|
| Load stock list | `/api/v1/stocks` | GET |
| Start analysis | `/api/v1/analyze/{ticker}` | POST (SSE) |
| Get report list | `/api/v1/reports` | GET |
| Get report detail | `/api/v1/reports/{id}` | GET |
| Get PDF | `/api/v1/reports/{id}/pdf` | GET |
| Health check | `/api/v1/health` | GET |

Full API spec: [API_CONTRACT.md](../../docs/API_CONTRACT.md)

---

## SSE Integration

The `useAgentStream` hook handles the SSE connection:

1. User clicks "Analyze" → hook sends `POST /api/v1/analyze/{ticker}`
2. Response is a `ReadableStream` (not `EventSource`, since we use POST)
3. Hook parses `data:` lines into typed `AgentStep` objects
4. Each step dispatched to `useReducer` → state updates → UI re-renders
5. On `type: "complete"` → report data extracted → PDF URL constructed
6. On `type: "error"` → error state set → error message shown
7. On unmount → reader cancelled → connection closed

State flow: `idle → connecting → streaming → complete | error`

---

## Styling

### Theme

- **Background:** `slate-900` (#0f172a)
- **Cards/Panels:** `slate-800` (#1e293b)
- **Borders:** `slate-700` (#334155)
- **Text primary:** `slate-100` (#f1f5f9)
- **Text secondary:** `slate-400` (#94a3b8)

### Signal Colors

- **Bullish:** `emerald-500` (#10b981) — green
- **Bearish:** `red-500` (#ef4444) — red
- **Neutral:** `amber-500` (#f59e0b) — amber

### Typography

- **Font:** Inter (Google Fonts) or system font stack
- **Monospace:** JetBrains Mono for data values

### Design Principles

- Bloomberg Terminal inspiration: information-dense but clean
- Dark-first — no light mode in MVP
- Reasoning steps: subtle slide-in animation (150ms), auto-scroll to latest
- Minimal chrome — data takes center stage

---

## Docker

### Build

```bash
docker build -t marketlens-frontend .
```

### Run

```bash
docker run -p 3000:3000 marketlens-frontend
```

### Docker Compose (from project root)

```bash
docker compose up frontend
```

---

## Development Without Backend

The frontend can be developed independently using mock data. See [ENV_SETUP.md](ENV_SETUP.md) Section 7 for mock data setup instructions.

---

*Reference: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for component specs, [TECH_SPEC.md](TECH_SPEC.md) for technical details, [API_CONTRACT.md](../../docs/API_CONTRACT.md) for the backend interface.*
