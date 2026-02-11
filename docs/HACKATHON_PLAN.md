# MarketLens — 4-Day Hackathon Sprint Plan

**Total Time:** 32 hours (4 days x 8 hours)
**Team:** 1–2 developers (Backend + Frontend parallel tracks)
**Goal:** Working demo with live reasoning trace, adaptive agent analysis, and PDF output

---

## Day 1: Foundation (8 Hours)

### Backend Track (8 hours)

#### Hour 1–2: Project Setup

| Item | Detail |
|------|--------|
| **Deliverable** | Runnable FastAPI skeleton with health endpoint |
| **Tasks** | Create `marketlens-backend/` repo. Set up virtualenv. Install dependencies from `requirements.txt`. Create directory structure (`agents/`, `tools/`, `utils/`, `data/`, `templates/`). Create `.env.example` and `config.json`. Add CSV data files (OGDC, TRG, PSO, LUCK, ENGRO, KSE100). Implement `GET /api/v1/health` endpoint. |
| **Definition of Done** | `curl http://localhost:8000/api/v1/health` returns `{"status": "ok"}` |
| **Risk** | Low |
| **Fallback** | N/A — this is foundational |

#### Hour 3–5: Implement All 8 Tool Functions

| Item | Detail |
|------|--------|
| **Deliverable** | All 8 tool functions working independently, tested via CLI |
| **Tasks** | Implement in order: (1) `data_tools.py` — CSV loading, summary stats. (2) `indicator_tools.py` — RSI, SMA, EMA, MACD, Bollinger, ATR, VWAP, Stochastic, OBV, ADX, Williams %R, CCI using pandas-ta. (3) `pattern_tools.py` — candlestick pattern detection. (4) `level_tools.py` — pivot points + Fibonacci retracement. (5) `comparison_tools.py` — index and sector comparison. (6) `volume_tools.py` — volume trend and divergence. (7) `chart_tools.py` — mplfinance chart generation with dark theme. Each tool returns structured data with human-readable interpretation. |
| **Definition of Done** | Each tool callable from Python REPL with real CSV data. Example: `calculate_indicator("OGDC", "RSI", {"period": 14})` returns `{"value": 32.1, "interpretation": "Oversold territory..."}` |
| **Risk** | Medium — pandas-ta edge cases, mplfinance styling |
| **Fallback** | Simplify pattern detection to top 3 patterns. Use default mplfinance style if custom styling blocks. |

#### Hour 6–7: Tool Registry + LLM Client

| Item | Detail |
|------|--------|
| **Deliverable** | `tool_registry.py` with all 8 Anthropic-format tool schemas. `llm_client.py` with Claude + GPT-4o abstraction. |
| **Tasks** | Define all 8 tools in Anthropic `tool_use` JSON schema format. Create tool name → function dispatch mapping. Implement `llm_client.py` with `create_message()` abstracting Anthropic vs OpenAI. Implement fallback logic: try Claude → catch timeout/error → switch to GPT-4o. |
| **Definition of Done** | `llm_client.create_message(messages, tools)` works with both providers. Tool schemas pass Anthropic validation. |
| **Risk** | Low — straightforward mapping |
| **Fallback** | Skip GPT-4o fallback, hardcode Claude only |

#### Hour 8: Analyst Agent (ReAct Loop)

| Item | Detail |
|------|--------|
| **Deliverable** | `analyst_agent.py` — working ReAct loop that analyzes a stock end-to-end |
| **Tasks** | Implement `run_analyst_agent(ticker)` async generator. System prompt with analyst persona. Conversation history management. Tool dispatch: parse `tool_use` blocks → call function → return `tool_result`. Termination: `end_turn` or max iterations. Yield `AgentStep` for each reasoning/tool_call/observation/complete event. |
| **Definition of Done** | `python -m agents.analyst_agent OGDC` runs in terminal, shows reasoning steps, calls 4–8 tools, produces final JSON analysis. Different output for different stocks. |
| **Risk** | High — prompt engineering may need iteration |
| **Fallback** | If agent loops or produces bad output, hardcode a simpler prompt and fix on Day 2. The loop mechanics must work. |

### Frontend Track (8 hours)

#### Hour 1–2: Project Setup

| Item | Detail |
|------|--------|
| **Deliverable** | Running Next.js 14 app with Tailwind, dark theme, TypeScript |
| **Tasks** | `npx create-next-app@latest marketlens-frontend` with App Router + TypeScript + Tailwind. Configure dark theme in `tailwind.config.ts`. Set up directory structure (`components/`, `hooks/`, `lib/`). Create `globals.css` with dark mode styles. Add Inter font. |
| **Definition of Done** | `npm run dev` shows dark-themed page at `localhost:3000` |
| **Risk** | Low |
| **Fallback** | N/A |

#### Hour 3–5: Dashboard Layout + Stock List

| Item | Detail |
|------|--------|
| **Deliverable** | Complete UI shell: sidebar with stock list, main content area, header |
| **Tasks** | Build `Dashboard.tsx` — split layout (sidebar + main). Build `Sidebar.tsx` — wrapper with logo, stock list, report history placeholder. Build `StockList.tsx` — hardcoded 6 stocks with ticker, name, price, change %. Active/selected state styling. Build `StockHeader.tsx` — selected stock details bar. Build `EmptyState.tsx` — illustration + "Select a stock to begin analysis". |
| **Definition of Done** | Dashboard looks polished with dark theme. Clicking a stock updates the header. Bloomberg-terminal aesthetic. |
| **Risk** | Low — pure UI |
| **Fallback** | Simplify to basic list if styling takes too long |

#### Hour 6–8: Mock Data + Component Polish

| Item | Detail |
|------|--------|
| **Deliverable** | All components rendering with mock/hardcoded data. UI ready for API integration. |
| **Tasks** | Create `lib/types.ts` with all TypeScript interfaces (Stock, AgentStep, AgentResult, etc.). Create mock data: fake stocks array, fake reasoning steps, fake report data. Build `AnalyzeButton.tsx` — idle/loading/complete states with mock toggle. Build `ReasoningPanel.tsx` skeleton — renders mock steps with icons. Build `ReportHistory.tsx` skeleton — renders mock reports with signal badges. Ensure auto-scroll works on reasoning panel with mock data. |
| **Definition of Done** | Full UI walkthrough possible with mock data. All component states visible. Screenshot-ready. |
| **Risk** | Low |
| **Fallback** | Skip animations, focus on data display |

---

## Day 2: Core Integration (8 Hours)

### Backend Track (8 hours)

#### Hour 1–2: SSE Endpoint

| Item | Detail |
|------|--------|
| **Deliverable** | `POST /api/v1/analyze/{ticker}` streams SSE events as agent runs |
| **Tasks** | Implement SSE endpoint in `main.py`. Wire `run_analyst_agent()` to `StreamingResponse`. Format each `AgentStep` as SSE `data:` line. Add CORS middleware allowing `localhost:3000`. Test with `curl -N -X POST http://localhost:8000/api/v1/analyze/OGDC`. |
| **Definition of Done** | curl shows streaming SSE events in real-time as agent runs. Events arrive progressively (not all at once). |
| **Risk** | Medium — SSE with POST is non-standard (EventSource uses GET) |
| **Fallback** | Switch to GET endpoint with ticker in query params, or use fetch + ReadableStream on frontend |

#### Hour 3–4: Prompt Engineering

| Item | Detail |
|------|--------|
| **Deliverable** | Agent produces high-quality, diverse analyses for all 5 stocks |
| **Tasks** | Run agent on all 5 stocks. Review reasoning traces. Refine system prompt: ensure agent uses 4–8 tools, produces different paths per stock, includes specific numbers, forms clear thesis. Tune temperature. Test edge cases (flat stock, volatile stock). Ensure output JSON is valid and complete. |
| **Definition of Done** | All 5 stocks produce valid analyses. At least 3 use visibly different tool sequences. No JSON parsing errors. |
| **Risk** | High — this is the hardest part. Agent may fixate on same tools. |
| **Fallback** | Add explicit instructions: "For the first stock, start with RSI..." No — that defeats the purpose. Instead: improve tool descriptions so agent understands when each is useful. |

#### Hour 5–6: PDF Generator

| Item | Detail |
|------|--------|
| **Deliverable** | Professional PDF generated from agent output |
| **Tasks** | Create Jinja2 HTML template (`templates/report.html`) with all sections: header (logo, date, ticker), executive summary (thesis + signal badge), chart (embedded Base64), detailed analysis (trend, momentum, levels, volume, context), key levels table, evidence chain (numbered list), risk factors, reasoning trace summary, disclaimer. Style with inline CSS. Convert to PDF using fpdf2 or Playwright. |
| **Definition of Done** | PDF opens in any viewer. Looks professional. All sections populated from real agent output. Chart embedded and crisp. |
| **Risk** | Medium — PDF styling is fiddly |
| **Fallback** | Use fpdf2 for simple layout if HTML→PDF is problematic. Skip fancy formatting. |

#### Hour 7–8: Report Storage + History API

| Item | Detail |
|------|--------|
| **Deliverable** | Reports stored in SQLite. History endpoints working. |
| **Tasks** | Implement `database.py` — SQLite tables for `reports` and `agent_runs`. Store report on agent completion: analysis JSON, reasoning trace, PDF path, metadata. Implement `GET /api/v1/reports` — list recent reports. Implement `GET /api/v1/reports/{id}` — full report detail. Implement `GET /api/v1/reports/{id}/pdf` — serve PDF file. |
| **Definition of Done** | Analyze a stock → report appears in GET /reports. PDF downloadable via GET /reports/{id}/pdf. |
| **Risk** | Low — straightforward CRUD |
| **Fallback** | In-memory dict if SQLite setup blocks |

### Frontend Track (8 hours)

#### Hour 1–2: SSE Hook

| Item | Detail |
|------|--------|
| **Deliverable** | `useAgentStream.ts` — custom hook consuming SSE from backend |
| **Tasks** | Implement `useAgentStream(ticker)` hook using `fetch` + `ReadableStream` (since EventSource doesn't support POST). Parse SSE `data:` lines into typed `AgentStep` objects. Use `useReducer` for state management: `{ status, steps[], currentReport, error }`. Status flow: `idle → connecting → streaming → complete → error`. Handle connection errors and cleanup on unmount. |
| **Definition of Done** | Hook connects to real backend SSE, state updates correctly as events arrive. Console.log shows parsed events. |
| **Risk** | Medium — SSE parsing edge cases, POST vs GET |
| **Fallback** | Use polling (GET /reports/{id} every 2 seconds) if SSE integration fails |

#### Hour 3–5: Reasoning Panel (Killer Feature)

| Item | Detail |
|------|--------|
| **Deliverable** | `ReasoningPanel.tsx` consuming live SSE and rendering beautiful step-by-step trace |
| **Tasks** | Implement `ReasoningStep.tsx` — renders based on step type: reasoning (thought bubble with brain icon), tool_call (tool name + params, collapsible detail), observation (result with highlighted key values), complete (thesis + signal badge). Add slide-in animation for new steps. Implement auto-scroll to latest step. Add timestamp display. Style: dark cards, subtle borders, color-coded by type. |
| **Definition of Done** | Start analysis → reasoning panel fills in real-time with styled steps. Smooth animations. Auto-scrolls. Looks impressive. |
| **Risk** | Medium — animations + auto-scroll interaction |
| **Fallback** | Skip animations, use simple list with icons. Focus on correct data display. |

#### Hour 6–8: Full Integration

| Item | Detail |
|------|--------|
| **Deliverable** | Frontend connected to real backend. Full flow working. |
| **Tasks** | Implement `lib/api.ts` with all API client functions. Wire `StockList` click → `StockHeader` update → `AnalyzeButton` trigger → `useAgentStream` → `ReasoningPanel` display. Replace all mock data with real API calls. Test complete flow: select stock → click analyze → watch reasoning → see completion. Handle error states. |
| **Definition of Done** | End-to-end flow works for all 5 stocks. No console errors. Reasoning panel populates from real agent data. |
| **Risk** | Medium — integration bugs |
| **Fallback** | If SSE breaks, fall back to mock data for demo. Fix integration as time allows. |

---

## Day 3: Full Integration + Polish (8 Hours)

### Backend Track (8 hours)

#### Hour 1–2: Remaining REST Endpoints

| Item | Detail |
|------|--------|
| **Deliverable** | All API endpoints from API_CONTRACT.md implemented |
| **Tasks** | Implement `GET /api/v1/stocks` — list available stocks with current price from CSV. Implement `GET /api/v1/stocks/{ticker}/summary` — quick stats without running agent. Verify all error responses match contract format. Add input validation on all endpoints. |
| **Definition of Done** | All endpoints from API_CONTRACT.md return correct data. Postman/curl testing passes. |
| **Risk** | Low |
| **Fallback** | N/A |

#### Hour 3–4: Edge Cases + Error Handling

| Item | Detail |
|------|--------|
| **Deliverable** | Robust error handling across all paths |
| **Tasks** | Handle: unknown ticker → 404. LLM timeout → retry + fallback. Tool function error → return error to agent → agent adapts. Agent max iterations → force compile partial analysis. Malformed agent output → extract what's usable. SSE connection drop → no server crash. CORS headers on all responses including errors. |
| **Definition of Done** | Send invalid requests → get proper error responses. Kill LLM mid-request → graceful degradation. |
| **Risk** | Medium |
| **Fallback** | Handle top 3 error cases, skip edge cases |

#### Hour 5–6: Docker Setup

| Item | Detail |
|------|--------|
| **Deliverable** | Backend runs in Docker container |
| **Tasks** | Write `Dockerfile` (Python 3.11-slim, copy requirements, install, copy app, expose 8000). Add to `docker-compose.yml` at root level. Test container build and run. Ensure CSV data is copied into container. Environment variables via docker-compose. |
| **Definition of Done** | `docker compose up backend` → backend accessible at localhost:8000 |
| **Risk** | Low |
| **Fallback** | Skip Docker, run locally for demo |

#### Hour 7–8: Load Testing All Stocks

| Item | Detail |
|------|--------|
| **Deliverable** | All 5 stocks produce reliable, diverse analyses |
| **Tasks** | Run each stock 3 times. Verify: consistent signal direction, different tool sequences across stocks, no JSON errors, charts generate correctly, PDFs complete. Fix any agent prompt issues discovered. Log average execution times. |
| **Definition of Done** | 15/15 runs succeed. At least 3 stocks show different analysis paths. Average time < 20 seconds. |
| **Risk** | Medium — agent inconsistency |
| **Fallback** | Tune prompt aggressively. If one stock consistently fails, remove from demo set. |

### Frontend Track (8 hours)

#### Hour 1–2: Report Viewer

| Item | Detail |
|------|--------|
| **Deliverable** | In-app PDF viewer + download button |
| **Tasks** | Integrate react-pdf to display PDF inline. Construct PDF URL from report ID: `${API_URL}/api/v1/reports/${id}/pdf`. Add loading state while PDF loads. Add download button (direct link to PDF endpoint). Handle PDF load errors gracefully. |
| **Definition of Done** | After analysis completes, PDF renders inline. Download button works. |
| **Risk** | Medium — react-pdf configuration, CORS for PDF binary |
| **Fallback** | Skip inline viewer, provide download link only |

#### Hour 3–4: Report History Sidebar

| Item | Detail |
|------|--------|
| **Deliverable** | Sidebar shows past reports, clickable to view |
| **Tasks** | Fetch reports from `GET /api/v1/reports`. Display: ticker, signal badge (green/red/amber circle), thesis preview, timestamp. Click → fetch full report → display in ReportViewer. Auto-refresh after new analysis completes. |
| **Definition of Done** | Run 3 analyses → all 3 appear in history → click any → report loads |
| **Risk** | Low |
| **Fallback** | Static list, no click-to-view |

#### Hour 5–6: QuickStats Panel

| Item | Detail |
|------|--------|
| **Deliverable** | Signal/confidence display with key levels after analysis |
| **Tasks** | Build `QuickStats.tsx` — shows after analysis: signal pill (BULLISH green / BEARISH red / NEUTRAL amber), confidence badge, support/resistance levels, stop loss, target price. Extract from agent result JSON. Positioned above or beside report viewer. |
| **Definition of Done** | After analysis, QuickStats shows accurate data from agent output. Color-coded correctly. |
| **Risk** | Low |
| **Fallback** | Skip, show data in ReasoningPanel completion step only |

#### Hour 7–8: Full Integration Testing

| Item | Detail |
|------|--------|
| **Deliverable** | All states tested, all flows working |
| **Tasks** | Test: initial load (empty state), stock selection, analysis trigger, streaming (reasoning panel populating), completion (report + QuickStats + history update), error states (backend down, analysis timeout), multiple sequential analyses. Fix visual bugs. Ensure responsive at 1280px+. |
| **Definition of Done** | 5 consecutive end-to-end analyses work without errors. All states render correctly. |
| **Risk** | Medium |
| **Fallback** | Fix critical path only (happy path). Mark non-critical bugs for later. |

---

## Day 4: Polish + Demo (8 Hours)

### Both Tracks

#### Hour 1–2: UI Polish

| Item | Detail |
|------|--------|
| **Deliverable** | Polished, demo-ready UI |
| **Tasks** | Smooth animations on reasoning steps (slide-in, fade). Transition between states (idle → streaming → complete). Loading indicators (pulsing dots, skeleton screens). Stock list hover effects. Active stock highlight. Report history signal badges. Typography consistency check. Spacing/alignment audit. |
| **Definition of Done** | UI looks polished and professional in screen recording |
| **Risk** | Low — cosmetic only |
| **Fallback** | Ship without animations |

#### Hour 3–4: PDF Template Refinement

| Item | Detail |
|------|--------|
| **Deliverable** | Print-quality PDF output |
| **Tasks** | Refine PDF template: typography (section headers, body text, data tables), color scheme (green/red/amber for signals), chart placement and sizing, evidence chain formatting, key levels table, disclaimer styling, header/footer with branding. Test with all 5 stocks. |
| **Definition of Done** | PDF passes the "would a human analyst be embarrassed to present this?" test — answer: no |
| **Risk** | Low |
| **Fallback** | Use current PDF as-is |

#### Hour 5–6: End-to-End Testing

| Item | Detail |
|------|--------|
| **Deliverable** | All stocks tested, screenshots captured |
| **Tasks** | Run all 5 stocks through complete flow. Verify different analysis paths (screenshot reasoning panels side by side). Verify PDFs for each. Test Docker Compose deployment (both containers). Capture screenshots for documentation. Note any remaining bugs. |
| **Definition of Done** | 5/5 stocks work. Visual evidence of different analysis paths. Docker Compose works. |
| **Risk** | Medium — may discover bugs |
| **Fallback** | Fix showstoppers only. Document known issues. |

#### Hour 7: Demo Rehearsal

| Item | Detail |
|------|--------|
| **Deliverable** | Practiced demo, timed at 4 minutes |
| **Tasks** | Follow DEMO_SCRIPT.md exactly. Practice narrating reasoning trace. Time each section. Identify best stocks for demo (one bearish, one bullish, one neutral). Test backup plans (pre-cached responses). Prepare for Q&A. |
| **Definition of Done** | Clean 4-minute demo run completed twice |
| **Risk** | Low |
| **Fallback** | N/A |

#### Hour 8: Buffer

| Item | Detail |
|------|--------|
| **Deliverable** | Bug fixes, final touches |
| **Tasks** | Fix any issues found during rehearsal. Last-minute polish. Verify API keys are set. Ensure demo environment is stable. Final git commit and tag. |
| **Definition of Done** | Demo-ready build tagged in git |
| **Risk** | N/A — buffer time |
| **Fallback** | N/A |

---

## Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|------|------------|--------|-----------|-------|
| Agent produces same analysis for all stocks | Medium | Critical | Better tool descriptions, diverse system prompt, test early on Day 1 | Backend |
| SSE not working with POST method | Medium | High | Use GET with query params, or fetch + ReadableStream on frontend | Both |
| mplfinance chart quality poor | Low | Medium | Fallback to matplotlib direct. Or screenshot TradingView approach. | Backend |
| PDF generation fails or looks bad | Medium | Medium | Pre-generate demo PDFs. Use simple fpdf2 layout as fallback. | Backend |
| react-pdf integration issues | Medium | Medium | Download link only. Skip inline preview. | Frontend |
| Anthropic API rate limits | Low | High | Implement request queuing. Pre-cache demo stocks. | Backend |
| 4-day timeline overrun | Medium | High | Strict P0 scope. Cut: report history, QuickStats, Docker. Must-have: agent + reasoning trace + PDF. | Both |

---

## Minimum Viable Demo

If everything goes wrong and only the absolute essentials work, the demo must include:

1. **Agent runs in terminal** — shows reasoning trace in console
2. **PDF generates** — from agent output
3. **Different stocks → different analysis** — provable via console output

Everything else (UI, SSE streaming, report history) is a bonus on top of this core.

---

*Reference: [PRD.md](PRD.md) for requirements, [API_CONTRACT.md](API_CONTRACT.md) for interface spec, [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for presentation plan.*
