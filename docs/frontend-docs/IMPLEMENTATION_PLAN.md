# MarketLens Frontend — Implementation Plan

**Document 10 of 12** | Frontend-specific

---

## 1. Component Hierarchy

```
App (layout.tsx — dark theme, Inter font)
│
├── page.tsx (Dashboard entry point)
│
└── Dashboard.tsx (main layout container)
    │
    ├── Sidebar (280px fixed width)
    │   ├── Logo + App Title
    │   ├── StockList
    │   │   └── StockItem (repeated)
    │   │       ├── Ticker badge
    │   │       ├── Stock name
    │   │       ├── Price
    │   │       └── Change % (green/red)
    │   │
    │   ├── Divider
    │   │
    │   └── ReportHistory
    │       └── ReportItem (repeated)
    │           ├── Signal badge (🟢🔴🟡)
    │           ├── Ticker
    │           ├── Thesis preview (truncated)
    │           └── Timestamp
    │
    └── MainContent (flex-1)
        │
        ├── StockHeader
        │   ├── Ticker (large)
        │   ├── Stock name
        │   ├── Current price
        │   ├── Change % (colored)
        │   ├── Sector badge
        │   └── AnalyzeButton
        │
        ├── [BEFORE ANALYSIS] EmptyState
        │   └── Illustration + "Click Analyze to begin"
        │
        ├── [DURING/AFTER ANALYSIS] SplitView (resizable)
        │   │
        │   ├── LeftPanel: ReasoningPanel
        │   │   ├── Header ("Agent Reasoning" + step count)
        │   │   ├── StepList (scrollable)
        │   │   │   ├── ReasoningStep (type="reasoning")
        │   │   │   │   └── 🧠 icon + thought text + timestamp
        │   │   │   ├── ReasoningStep (type="tool_call")
        │   │   │   │   └── 📊 icon + tool name + params (collapsible)
        │   │   │   ├── ReasoningStep (type="observation")
        │   │   │   │   └── 👁 icon + result summary + key values highlighted
        │   │   │   └── ReasoningStep (type="complete")
        │   │   │       └── ✅ icon + thesis + signal badge
        │   │   └── LoadingIndicator (while streaming)
        │   │
        │   └── RightPanel: ReportPanel
        │       ├── QuickStats
        │       │   ├── Signal pill (BULLISH/BEARISH/NEUTRAL)
        │       │   ├── Confidence badge
        │       │   ├── Support levels
        │       │   ├── Resistance levels
        │       │   ├── Stop loss
        │       │   └── Target price
        │       ├── ReportViewer (react-pdf)
        │       │   ├── PDF pages
        │       │   └── Page navigation
        │       └── DownloadButton
        │
        └── [ON ERROR] ErrorState
            └── Error message + retry button
```

---

## 2. State Management

### 2.1 Agent Stream State (`useReducer`)

```typescript
// State shape
interface AgentStreamState {
  status: "idle" | "connecting" | "streaming" | "complete" | "error";
  steps: AgentStep[];
  currentReport: ReportDetail | null;
  error: string | null;
}

// Initial state
const initialState: AgentStreamState = {
  status: "idle",
  steps: [],
  currentReport: null,
  error: null,
};
```

### 2.2 Reducer Actions

```typescript
type AgentStreamAction =
  | { type: "START_STREAM" }                          // → connecting
  | { type: "CONNECTED" }                              // → streaming
  | { type: "ADD_STEP"; step: AgentStep }             // append to steps[]
  | { type: "STREAM_COMPLETE"; report: ReportDetail }  // → complete
  | { type: "STREAM_ERROR"; error: string }           // → error
  | { type: "RESET" };                                 // → idle (clear all)
```

### 2.3 Status Flow

```
idle ──[click Analyze]──► connecting ──[first event]──► streaming
                                                            │
                                                   ┌───────┴───────┐
                                                   ▼               ▼
                                              complete          error
                                                   │               │
                                                   └──[click Analyze again]──► connecting
```

### 2.4 Application-Level State

No global state management library needed for MVP. State is organized as:

| State | Location | Scope |
|-------|----------|-------|
| Selected stock | `Dashboard` component (`useState`) | Passed to StockHeader, AnalyzeButton |
| Agent stream | `useAgentStream` hook (`useReducer`) | Passed to ReasoningPanel, ReportPanel |
| Stock list | `StockList` component (`useState` + fetch) | Local |
| Report history | `ReportHistory` component (`useState` + fetch) | Local, refreshed after analysis |

---

## 3. SSE Hook: `useAgentStream.ts`

### 3.1 Interface

```typescript
interface UseAgentStreamReturn {
  state: AgentStreamState;
  startAnalysis: (ticker: string) => void;
  reset: () => void;
}

function useAgentStream(): UseAgentStreamReturn;
```

### 3.2 Implementation Outline

```typescript
function useAgentStream(): UseAgentStreamReturn {
  const [state, dispatch] = useReducer(agentStreamReducer, initialState);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startAnalysis = useCallback(async (ticker: string) => {
    // Cancel any existing stream
    abortControllerRef.current?.abort();
    dispatch({ type: "START_STREAM" });

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze/${ticker}`,
        {
          method: "POST",
          headers: { Accept: "text/event-stream" },
          signal: controller.signal,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        dispatch({ type: "STREAM_ERROR", error: errorData.error.message });
        return;
      }

      dispatch({ type: "CONNECTED" });

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr) continue;

            const step: AgentStep = JSON.parse(jsonStr);
            dispatch({ type: "ADD_STEP", step });

            if (step.type === "complete") {
              // Fetch full report detail
              const report = await fetchReportDetail(step.report_id!);
              dispatch({ type: "STREAM_COMPLETE", report });
            }

            if (step.type === "error") {
              dispatch({ type: "STREAM_ERROR", error: step.content || "Unknown error" });
            }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        dispatch({ type: "STREAM_ERROR", error: (err as Error).message });
      }
    }
  }, []);

  const reset = useCallback(() => {
    abortControllerRef.current?.abort();
    dispatch({ type: "RESET" });
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => abortControllerRef.current?.abort();
  }, []);

  return { state, startAnalysis, reset };
}
```

### 3.3 SSE Parsing Notes

- `EventSource` API does not support POST — use `fetch` + `ReadableStream`
- Buffer incomplete lines across chunks (SSE events can span multiple read() calls)
- Handle `data:` prefix stripping
- Parse JSON per event
- Handle malformed JSON gracefully (log warning, skip event)

---

## 4. Key Pages / Routes

MVP is a single-page application. No routing needed.

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `page.tsx` → `Dashboard` | Main and only page |

Post-hackathon routes (future):

| Route | Purpose |
|-------|---------|
| `/report/{id}` | Shareable report link |
| `/settings` | API key management, preferences |
| `/history` | Full report history with search/filter |

---

## 5. API Client: `lib/api.ts`

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchStocks(): Promise<Stock[]> {
  const res = await fetch(`${API_URL}/api/v1/stocks`);
  const data: StockListResponse = await res.json();
  return data.stocks;
}

export async function fetchReports(limit: number = 10): Promise<ReportSummary[]> {
  const res = await fetch(`${API_URL}/api/v1/reports?limit=${limit}`);
  const data: ReportListResponse = await res.json();
  return data.reports;
}

export async function fetchReportDetail(reportId: string): Promise<ReportDetail> {
  const res = await fetch(`${API_URL}/api/v1/reports/${reportId}`);
  return res.json();
}

export function getReportPdfUrl(reportId: string): string {
  return `${API_URL}/api/v1/reports/${reportId}/pdf`;
}

export async function fetchStockSummary(ticker: string): Promise<StockSummary> {
  const res = await fetch(`${API_URL}/api/v1/stocks/${ticker}/summary`);
  return res.json();
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/api/v1/health`);
  return res.json();
}
```

---

## 6. Styling Specification

### 6.1 Tailwind Config

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Custom semantic colors
        "ml-bg": "#0f172a",         // slate-900
        "ml-card": "#1e293b",       // slate-800
        "ml-border": "#334155",     // slate-700
        "ml-text": "#f1f5f9",       // slate-100
        "ml-muted": "#94a3b8",      // slate-400
        "ml-bullish": "#10b981",    // emerald-500
        "ml-bearish": "#ef4444",    // red-500
        "ml-neutral": "#f59e0b",    // amber-500
        "ml-accent": "#3b82f6",     // blue-500
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      animation: {
        "slide-in": "slideIn 150ms ease-out",
        "fade-in": "fadeIn 200ms ease-out",
        "pulse-dot": "pulseDot 1.5s ease-in-out infinite",
      },
      keyframes: {
        slideIn: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

### 6.2 Layout Specifications

| Element | Spec |
|---------|------|
| Sidebar width | 280px fixed |
| Main content | flex-1, min-width 0 |
| ReasoningPanel | 40% of main content (resizable) |
| ReportPanel | 60% of main content (resizable) |
| Stock header height | 64px |
| Reasoning step padding | 12px 16px |
| Card border radius | 8px |
| Card padding | 16px |

### 6.3 Reasoning Step Styles

| Step Type | Icon | Background | Text Color |
|-----------|------|-----------|-----------|
| `reasoning` | 🧠 | `slate-800/50` | `slate-200` |
| `tool_call` | 📊 | `blue-900/30` | `blue-200` |
| `observation` | 👁 | `slate-800/30` | `slate-300` |
| `complete` | ✅ | `emerald-900/30` | `emerald-200` |
| `error` | ❌ | `red-900/30` | `red-200` |

### 6.4 Signal Badge Styles

| Signal | Background | Text | Border |
|--------|-----------|------|--------|
| BULLISH | `emerald-900/50` | `emerald-400` | `emerald-700` |
| BEARISH | `red-900/50` | `red-400` | `red-700` |
| NEUTRAL | `amber-900/50` | `amber-400` | `amber-700` |

---

## 7. Component Behavior Details

### 7.1 StockList

- **Data source:** `GET /api/v1/stocks` on mount
- **Selection:** Click sets `selectedStock` in parent Dashboard
- **Active state:** Selected stock has `ml-accent` left border + `slate-700` background
- **Price coloring:** Positive change → `emerald-400`, negative → `red-400`
- **Refresh:** Static for MVP (fetched once on mount)

### 7.2 AnalyzeButton

| State | Label | Style | Behavior |
|-------|-------|-------|----------|
| `idle` | "Analyze {ticker}" | Blue button, full opacity | Clickable |
| `connecting` | "Connecting..." | Blue button, pulsing opacity | Disabled |
| `streaming` | "Analyzing... ({n} steps)" | Pulsing blue border | Disabled, shows step count |
| `complete` | "Analysis Complete ✓" | Green button | Clickable (re-analyze) |
| `error` | "Retry Analysis" | Red button | Clickable |

### 7.3 ReasoningPanel

- **Auto-scroll:** Automatically scrolls to bottom as new steps arrive, unless user has manually scrolled up
- **Auto-scroll detection:** Track `scrollTop + clientHeight >= scrollHeight - 50px` — if true, auto-scroll enabled
- **Step animation:** Each new step enters with `animate-slide-in` (150ms)
- **Tool call collapsible:** Click tool_call step to expand/collapse `tool_input` JSON
- **Observation highlighting:** Key numeric values (prices, percentages, indicator values) rendered in `font-mono` with `emerald-400` or `red-400` coloring
- **Loading indicator:** Pulsing dots at bottom while `status === "streaming"`

### 7.4 ReportViewer

- **Library:** `react-pdf` (or `@react-pdf-viewer/core`)
- **PDF URL:** `getReportPdfUrl(reportId)` → `http://localhost:8000/api/v1/reports/{id}/pdf`
- **Loading state:** Skeleton placeholder while PDF loads
- **Error state:** "PDF could not be loaded" with download link fallback
- **Controls:** Page navigation (if multi-page), zoom not needed for MVP
- **Download:** Direct `<a href={pdfUrl} download>` link

### 7.5 ReportHistory

- **Data source:** `GET /api/v1/reports?limit=10` on mount + after each analysis completes
- **Refresh trigger:** When `useAgentStream` state transitions to `complete`, refetch reports
- **Display:** Signal badge (colored dot) + ticker + truncated thesis (50 chars) + relative timestamp ("2 min ago")
- **Click:** Sets `currentReport` from fetched report detail → displays in ReportViewer
- **Empty state:** "No reports yet. Analyze a stock to get started."

### 7.6 QuickStats

- **Visibility:** Only shown when `status === "complete"`
- **Layout:** Horizontal row of stat cards above the report viewer
- **Cards:** Signal pill | Confidence badge | Support levels | Resistance levels | Stop Loss | Target
- **Signal pill:** Colored background (green/red/amber) with uppercase text
- **Level values:** `font-mono`, formatted as "PKR {value}"

---

## 8. Error Handling

| Error Scenario | User Experience |
|----------------|----------------|
| Backend unreachable | "Unable to connect to analysis server. Is the backend running?" + retry button |
| Unknown ticker (404) | "Stock {ticker} not found." (shouldn't happen with curated stock list) |
| LLM unavailable (503) | "AI analysis service temporarily unavailable. Please try again." |
| SSE connection dropped | "Connection lost during analysis." + check if report completed via REST |
| PDF load failed | "Report PDF could not be loaded." + direct download link |
| Fetch stocks failed | Show hardcoded stock list as fallback |

---

## 9. Implementation Order

| Priority | Component/Feature | Day |
|----------|------------------|-----|
| 1 | Project setup (Next.js, Tailwind, TypeScript, dark theme) | Day 1 |
| 2 | `lib/types.ts` — all TypeScript interfaces | Day 1 |
| 3 | `Dashboard.tsx` + `Sidebar.tsx` — layout shell | Day 1 |
| 4 | `StockList.tsx` — with hardcoded data first | Day 1 |
| 5 | `StockHeader.tsx` + `EmptyState.tsx` | Day 1 |
| 6 | `AnalyzeButton.tsx` — with mock state toggle | Day 1 |
| 7 | `ReasoningStep.tsx` — renders a single step | Day 1 |
| 8 | `ReasoningPanel.tsx` — renders mock steps | Day 1 |
| 9 | `useAgentStream.ts` — SSE consumer hook | Day 2 |
| 10 | Wire ReasoningPanel to real SSE | Day 2 |
| 11 | `lib/api.ts` — API client | Day 2 |
| 12 | Full integration (StockList from API, analysis flow) | Day 2 |
| 13 | `ReportViewer.tsx` — react-pdf integration | Day 3 |
| 14 | `ReportHistory.tsx` — from API | Day 3 |
| 15 | `QuickStats.tsx` | Day 3 |
| 16 | Error states and loading states | Day 3 |
| 17 | Animations, polish, responsive | Day 4 |

---

*Reference: [TECH_SPEC.md](TECH_SPEC.md) for component specs, [ENV_SETUP.md](ENV_SETUP.md) for setup, [API_CONTRACT.md](../../docs/API_CONTRACT.md) for backend interface.*
