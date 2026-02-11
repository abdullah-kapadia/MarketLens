# MarketLens Frontend — Technical Specification

**Document 11 of 12** | Frontend-specific

---

## 1. Component Specifications

### 1.1 `Dashboard.tsx`

```typescript
interface DashboardProps {}

// State
// selectedStock: Stock | null
// agentStream: from useAgentStream() hook
```

**Behavior:**
- Renders the main split layout: sidebar (fixed 280px) + main content (flex-1)
- Manages `selectedStock` state — passed down to `StockHeader`, `AnalyzeButton`
- Houses `useAgentStream()` hook — passes state/controls to child components
- On stock selection change: resets agent stream state
- Full viewport height (`h-screen`), dark background (`bg-ml-bg`)

**Styling:**
- `flex h-screen bg-ml-bg text-ml-text overflow-hidden`
- Sidebar: `w-[280px] flex-shrink-0 border-r border-ml-border`
- Main: `flex-1 flex flex-col min-w-0`

**Accessibility:**
- Sidebar has `role="navigation"` with `aria-label="Stock selection and report history"`
- Main content has `role="main"`

---

### 1.2 `Sidebar.tsx`

```typescript
interface SidebarProps {
  selectedStock: Stock | null;
  onSelectStock: (stock: Stock) => void;
  onSelectReport: (reportId: string) => void;
  refreshReportsSignal: number; // increments when a new report is generated
}
```

**Behavior:**
- Contains logo/title section at top
- `StockList` in the upper portion
- Horizontal divider
- `ReportHistory` in the lower portion (scrollable)
- Lower section takes remaining height via `flex-1 overflow-y-auto`

**Styling:**
- `flex flex-col h-full bg-ml-card`
- Logo section: `p-4 border-b border-ml-border`
- Title: "MarketLens" in `text-lg font-semibold`

---

### 1.3 `StockList.tsx`

```typescript
interface StockListProps {
  selectedStock: Stock | null;
  onSelect: (stock: Stock) => void;
}
```

**State:**
- `stocks: Stock[]` — fetched from `GET /api/v1/stocks` on mount
- `loading: boolean`
- `error: string | null`

**Behavior:**
- Fetches stocks on mount via `fetchStocks()`
- Renders each stock as a clickable item
- Active stock highlighted with left border accent
- Shows ticker (bold), name (muted), price, and change %
- Change % colored: positive → `text-ml-bullish`, negative → `text-ml-bearish`

**Styling per item:**
```
px-4 py-3 cursor-pointer hover:bg-slate-700/50 transition-colors
border-l-2 border-transparent
[active]: border-l-2 border-ml-accent bg-slate-700/30
```

**Accessibility:**
- Each stock item: `role="button"`, `tabIndex={0}`, `onKeyDown` handles Enter/Space
- `aria-selected` on active item
- Container: `role="listbox"`, `aria-label="Available stocks"`

---

### 1.4 `ReportHistory.tsx`

```typescript
interface ReportHistoryProps {
  onSelectReport: (reportId: string) => void;
  refreshSignal: number;
}
```

**State:**
- `reports: ReportSummary[]` — fetched from `GET /api/v1/reports?limit=10`
- `loading: boolean`

**Behavior:**
- Fetches on mount and whenever `refreshSignal` changes
- Each item shows: signal dot (colored), ticker, truncated thesis, relative timestamp
- Click loads full report detail in ReportViewer

**Signal dot colors:**
- BULLISH: `bg-ml-bullish` (green circle)
- BEARISH: `bg-ml-bearish` (red circle)
- NEUTRAL: `bg-ml-neutral` (amber circle)

**Relative timestamp:** "Just now", "2m ago", "1h ago", "Feb 10"

**Styling per item:**
```
px-4 py-2.5 cursor-pointer hover:bg-slate-700/50 transition-colors flex items-start gap-3
```

---

### 1.5 `StockHeader.tsx`

```typescript
interface StockHeaderProps {
  stock: Stock | null;
  streamStatus: AgentStreamStatus;
  onAnalyze: () => void;
}
```

**Behavior:**
- Displays selected stock's ticker (large, bold), full name, current price, change %, sector badge
- Contains `AnalyzeButton` at the right side
- If no stock selected, shows minimal state

**Layout:**
```
[OGDC]  Oil & Gas Development Company     Energy     PKR 118.50  -2.3%    [Analyze]
 ^^^                                      ^^^^^^                           ^^^^^^^
ticker             name                   sector      price  change        button
```

**Styling:**
- `h-16 px-6 flex items-center justify-between border-b border-ml-border bg-ml-card`
- Ticker: `text-xl font-bold`
- Sector badge: `px-2 py-0.5 rounded text-xs bg-slate-700 text-ml-muted`

---

### 1.6 `AnalyzeButton.tsx`

```typescript
interface AnalyzeButtonProps {
  ticker: string;
  status: AgentStreamStatus;
  onClick: () => void;
}
```

**States and Rendering:**

| Status | Label | Classes |
|--------|-------|---------|
| `idle` | `Analyze {ticker}` | `bg-ml-accent hover:bg-blue-600 text-white` |
| `connecting` | `Connecting...` | `bg-ml-accent/70 text-white cursor-not-allowed` + pulse animation |
| `streaming` | `Analyzing...` | `bg-ml-accent/70 text-white cursor-not-allowed border border-ml-accent` + pulse border |
| `complete` | `Re-analyze` | `bg-emerald-600 hover:bg-emerald-700 text-white` |
| `error` | `Retry` | `bg-red-600 hover:bg-red-700 text-white` |

**Base classes:** `px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200`

**Disabled during:** `connecting`, `streaming`

---

### 1.7 `ReasoningPanel.tsx` — THE KEY COMPONENT

```typescript
interface ReasoningPanelProps {
  steps: AgentStep[];
  status: AgentStreamStatus;
}
```

**State:**
- `autoScroll: boolean` — defaults to `true`, set to `false` when user scrolls up
- `scrollContainerRef: RefObject<HTMLDivElement>`

**Behavior:**
- Renders a scrollable list of `ReasoningStep` components
- New steps animate in with `animate-slide-in`
- Auto-scrolls to bottom as new steps arrive (unless user scrolled up)
- Shows pulsing loading indicator at bottom while `status === "streaming"`
- Header shows step count: "Agent Reasoning ({n} steps)"

**Auto-scroll Logic:**

```typescript
const handleScroll = () => {
  const el = scrollContainerRef.current;
  if (!el) return;
  const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
  setAutoScroll(isNearBottom);
};

useEffect(() => {
  if (autoScroll && scrollContainerRef.current) {
    scrollContainerRef.current.scrollTo({
      top: scrollContainerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }
}, [steps.length, autoScroll]);
```

**Styling:**
- Container: `flex flex-col h-full bg-ml-bg`
- Header: `px-4 py-3 border-b border-ml-border text-sm font-medium text-ml-muted`
- Scroll area: `flex-1 overflow-y-auto px-4 py-2 space-y-2`
- Loading dots: three `w-2 h-2 rounded-full bg-ml-accent animate-pulse-dot` with staggered delays

---

### 1.8 `ReasoningStep.tsx`

```typescript
interface ReasoningStepProps {
  step: AgentStep;
  isLatest: boolean;
}
```

**Behavior:**
- Renders differently based on `step.type`
- Latest step has `animate-slide-in` class
- Tool calls are collapsible — click to show/hide `tool_input` JSON
- Observations highlight key numeric values

**Rendering by type:**

#### `reasoning`
```
┌────────────────────────────────────┐
│ 🧠  Loading OGDC data for 6M...   │
│                           14:30:01 │
└────────────────────────────────────┘
```
- Background: `bg-slate-800/50 rounded-lg p-3`
- Icon: `🧠` in `text-lg`
- Text: `text-sm text-slate-200`
- Timestamp: `text-xs text-ml-muted` right-aligned

#### `tool_call`
```
┌────────────────────────────────────┐
│ 📊  calculate_indicator            │
│     RSI • period: 14      14:30:03 │
│     [▼ Show details]               │
│     ┌──────────────────────────┐   │
│     │ {"ticker": "OGDC",      │   │
│     │  "indicator": "RSI",    │   │
│     │  "params": {"period":14}│   │
│     └──────────────────────────┘   │
└────────────────────────────────────┘
```
- Background: `bg-blue-900/20 rounded-lg p-3 border border-blue-800/30`
- Tool name: `font-mono text-sm text-blue-300`
- Input summary: one-line extraction of key params
- Collapsible detail: `font-mono text-xs bg-slate-900 rounded p-2`

#### `observation`
```
┌────────────────────────────────────┐
│ 👁  RSI(14) = 32.1 — Oversold     │
│     territory...           14:30:04│
└────────────────────────────────────┘
```
- Background: `bg-slate-800/30 rounded-lg p-3`
- Key values (numbers, percentages) rendered in `font-mono text-ml-bullish` or `text-ml-bearish` based on context

#### `complete`
```
┌────────────────────────────────────┐
│ ✅  Analysis Complete              │
│                                    │
│     BEARISH  HIGH                  │
│                                    │
│     OGDC faces sustained bearish   │
│     pressure with RSI in oversold  │
│     territory near key support...  │
│                           14:30:12 │
└────────────────────────────────────┘
```
- Background: `bg-emerald-900/20 rounded-lg p-3 border border-emerald-800/30`
- Signal badge: styled pill with signal-appropriate color
- Thesis text: `text-sm font-medium`

---

### 1.9 `ReportViewer.tsx`

```typescript
interface ReportViewerProps {
  reportId: string | null;
  pdfUrl: string | null;
}
```

**State:**
- `numPages: number | null`
- `pageNumber: number` (default 1)
- `loading: boolean`
- `error: boolean`

**Behavior:**
- Uses `react-pdf` (`Document` + `Page` components)
- Constructs PDF URL from `getReportPdfUrl(reportId)`
- Shows loading skeleton while PDF renders
- Error fallback: "Unable to load PDF" + download link
- Page navigation controls if multi-page (Previous/Next buttons)

**Integration:**

```typescript
import { Document, Page, pdfjs } from "react-pdf";

// Set worker source
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
```

**Styling:**
- Container: `flex flex-col items-center bg-slate-900/50 rounded-lg overflow-auto`
- PDF page: centered with subtle shadow
- Controls: `flex items-center gap-4 py-2`

**Accessibility:**
- `aria-label="Report PDF viewer"`
- Page navigation buttons have proper labels

---

### 1.10 `QuickStats.tsx`

```typescript
interface QuickStatsProps {
  analysis: AgentResult;
}
```

**Behavior:**
- Horizontal row of stat cards
- Only shown when analysis is complete
- Fades in with `animate-fade-in`

**Cards Layout:**

```
┌──────────┬────────────┬─────────────┬──────────────┬───────────┬──────────┐
│  BEARISH │ HIGH conf. │ S: 115, 108 │ R: 128, 135  │ SL: 112   │ T: 108   │
│  signal  │ confidence │ support     │ resistance   │ stop loss │ target   │
└──────────┴────────────┴─────────────┴──────────────┴───────────┴──────────┘
```

**Each card:**
- Label: `text-xs text-ml-muted uppercase tracking-wider`
- Value: `text-sm font-mono font-medium`
- Background: `bg-ml-card rounded-lg px-3 py-2`
- Signal card: colored background matching signal

---

### 1.11 `EmptyState.tsx`

```typescript
interface EmptyStateProps {
  hasStock: boolean; // Is a stock selected?
}
```

**Behavior:**
- If no stock: "Select a stock from the sidebar to get started"
- If stock selected but no analysis: "Click Analyze to start AI analysis of {ticker}"
- Centered in main content area
- Muted text with optional illustration/icon

---

## 2. SSE Event Handling

### 2.1 Event Parsing

```typescript
function parseSSELine(line: string): AgentStep | null {
  if (!line.startsWith("data: ")) return null;

  const jsonStr = line.slice(6).trim();
  if (!jsonStr) return null;

  try {
    return JSON.parse(jsonStr) as AgentStep;
  } catch {
    console.warn("Failed to parse SSE event:", jsonStr);
    return null;
  }
}
```

### 2.2 Chunk Buffering

SSE events may arrive split across multiple `read()` chunks. The parser must buffer incomplete lines:

```typescript
let buffer = "";

function processChunk(chunk: string): AgentStep[] {
  buffer += chunk;
  const lines = buffer.split("\n");
  buffer = lines.pop() || ""; // Last element may be incomplete

  const steps: AgentStep[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === "") continue; // Empty line (SSE delimiter)
    const step = parseSSELine(trimmed);
    if (step) steps.push(step);
  }
  return steps;
}
```

### 2.3 Error Handling

| Error | Detection | Action |
|-------|-----------|--------|
| Network error | `fetch` throws | Set error state, show "Connection failed" |
| HTTP error (404, 503) | `!response.ok` | Parse error JSON, show message |
| SSE parse error | JSON.parse throws | Log warning, skip event, continue stream |
| Stream interrupted | `reader.read()` returns `done: true` prematurely | Check if "complete" event received; if not, poll REST |
| Abort (user navigated) | AbortError caught | Clean up silently, no error shown |

### 2.4 Connection Recovery

If the stream drops before a `complete` event:

```typescript
// After stream error/close without completion
const lastStep = steps[steps.length - 1];
if (lastStep?.type !== "complete") {
  // Try to recover: check if the report was generated
  try {
    const reports = await fetchReports(1);
    const latestReport = reports.find(r => r.ticker === ticker);
    if (latestReport && wasGeneratedRecently(latestReport.generated_at)) {
      const detail = await fetchReportDetail(latestReport.id);
      dispatch({ type: "STREAM_COMPLETE", report: detail });
      return;
    }
  } catch {
    // Recovery failed
  }
  dispatch({ type: "STREAM_ERROR", error: "Connection lost during analysis" });
}
```

---

## 3. TypeScript Interfaces

All type definitions are in `lib/types.ts`. See [API_CONTRACT.md](../../docs/API_CONTRACT.md) Section 3.1 for the complete list of interfaces. The frontend types mirror the backend Pydantic models exactly.

Key additions beyond the API contract types:

```typescript
// Component-specific types

export interface StockItemProps {
  stock: Stock;
  isSelected: boolean;
  onClick: () => void;
}

export interface ReportItemProps {
  report: ReportSummary;
  onClick: () => void;
}

// Utility types

export function getSignalColor(signal: Signal): string {
  switch (signal) {
    case "BULLISH": return "ml-bullish";
    case "BEARISH": return "ml-bearish";
    case "NEUTRAL": return "ml-neutral";
  }
}

export function getStepIcon(type: StepType): string {
  switch (type) {
    case "reasoning": return "🧠";
    case "tool_call": return "📊";
    case "observation": return "👁";
    case "complete": return "✅";
    case "error": return "❌";
  }
}

export function formatRelativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return new Date(isoString).toLocaleDateString("en-PK", { month: "short", day: "numeric" });
}
```

---

## 4. Performance Considerations

### 4.1 SSE Event Batching

SSE events can arrive rapidly (multiple per second during tool execution). To prevent excessive re-renders:

```typescript
// In useAgentStream, batch rapid events
const pendingSteps = useRef<AgentStep[]>([]);
const flushTimeout = useRef<NodeJS.Timeout>();

function addStep(step: AgentStep) {
  pendingSteps.current.push(step);

  if (!flushTimeout.current) {
    flushTimeout.current = setTimeout(() => {
      const batch = pendingSteps.current;
      pendingSteps.current = [];
      flushTimeout.current = undefined;

      for (const s of batch) {
        dispatch({ type: "ADD_STEP", step: s });
      }
    }, 50); // Batch events within 50ms windows
  }
}
```

### 4.2 React-PDF Lazy Loading

```typescript
import dynamic from "next/dynamic";

const ReportViewer = dynamic(() => import("./ReportViewer"), {
  ssr: false,
  loading: () => <ReportViewerSkeleton />,
});
```

### 4.3 Render Optimization

- `ReasoningStep` uses `React.memo()` — steps never change after creation
- `StockList` uses `React.memo()` — only re-renders on stock data change
- `QuickStats` uses `React.memo()` — only re-renders on analysis change

### 4.4 Memory Management

- On new analysis start: clear previous steps array
- On component unmount: abort SSE connection, clear timeouts
- Report history limited to 10 items (no infinite scroll)

---

## 5. Responsive Design

### 5.1 Breakpoints

| Breakpoint | Layout |
|-----------|--------|
| **Desktop** (1280px+) | Sidebar + Split view (reasoning left, report right) |
| **Tablet** (768px–1279px) | Sidebar (narrower, 220px) + Stacked view (reasoning above, report below) |
| **Mobile** (< 768px) | No sidebar (hamburger menu), Report only (reasoning panel collapsed/hidden) |

### 5.2 Desktop (Primary Target)

```
┌─────────┬────────────────────┬─────────────────────────┐
│ Sidebar │  Reasoning Panel   │    Report Panel          │
│ 280px   │      40%           │       60%                │
│         │                    │                          │
│ Stocks  │  🧠 Step 1         │  ┌─────────────────┐    │
│ ──────  │  📊 Step 2         │  │   QuickStats    │    │
│ History │  👁 Step 3         │  └─────────────────┘    │
│         │  🧠 Step 4         │  ┌─────────────────┐    │
│         │  ...               │  │                  │    │
│         │                    │  │   PDF Viewer     │    │
│         │                    │  │                  │    │
│         │                    │  └─────────────────┘    │
└─────────┴────────────────────┴─────────────────────────┘
```

### 5.3 Tablet (768px)

```
┌──────────┬──────────────────────────────────────┐
│ Sidebar  │  Stock Header + Analyze Button       │
│ 220px    ├──────────────────────────────────────┤
│          │  Reasoning Panel (full width, 40vh)  │
│ Stocks   ├──────────────────────────────────────┤
│ ──────   │  QuickStats + Report (full width)    │
│ History  │                                      │
└──────────┴──────────────────────────────────────┘
```

### 5.4 Mobile (< 768px)

```
┌──────────────────────────────────────┐
│  ☰  MarketLens    OGDC    [Analyze] │
├──────────────────────────────────────┤
│  QuickStats (horizontal scroll)      │
├──────────────────────────────────────┤
│                                      │
│  PDF Viewer (full width)             │
│                                      │
│                                      │
├──────────────────────────────────────┤
│  [Show Reasoning Trace] (expandable) │
└──────────────────────────────────────┘
```

---

*Reference: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for build order, [ENV_SETUP.md](ENV_SETUP.md) for project setup, [API_CONTRACT.md](../../docs/API_CONTRACT.md) for backend interface.*
