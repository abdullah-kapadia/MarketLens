# MarketLens Backend Design

## Overview
MarketLens is a FastAPI backend that produces AI-driven technical analysis for PSX tickers. It runs a ReAct-style agent loop using Claude (primary) with GPT-4o fallback, executes eight deterministic analysis tools over local CSV data, persists results to SQLite, and streams progress to clients via Server-Sent Events (SSE). A PDF report generator renders the final analysis with charts and a dark-theme layout.

## Architecture
The system is organized into modules under `backend/`: `main.py` hosts the API and SSE streaming, `agents/` implements the ReAct loop, `tools/` contains analysis functions, `utils/` provides the LLM client and PDF generator, `database.py` manages SQLite persistence, and `models.py` defines Pydantic schemas. Data is file-based (CSV) under `data/` and configuration is read from `data/config.json`. The agent uses tool schemas from `agents/tool_registry.py` and emits event payloads that the SSE endpoint forwards to clients.

## Components
- **FastAPI app**: REST endpoints + `/api/v1/analyze/{ticker}` SSE stream.
- **LLM client**: Anthropic first, retry once on timeout/errors, then fallback to OpenAI; unified response format.
- **Agent loop**: Iterative reasoning with tool calls (min 3, max 15, 60s timeout).
- **Tools**: Data loading, indicators, patterns, support/resistance, comparisons, volume, chart generation.
- **Storage**: SQLite tables `reports` and `agent_runs` for persistence and auditability.
- **PDF**: Jinja2 template + fpdf2 renderer; charts generated with mplfinance.

## Data Flow
1. Client POSTs to `/api/v1/analyze/{ticker}` (optionally with indicator/period params).
2. API validates ticker, seeds an agent run, and begins SSE streaming.
3. Agent selects tools, receives observations, and composes final analysis.
4. Result is persisted to SQLite; optional PDF is generated and stored.
5. SSE emits `reasoning`, `tool_call`, `observation`, `complete` (or `error`) events.

## Error Handling & Observability
Errors return structured `ErrorResponse` payloads and SSE `error` events. LLM failures trigger retry and fallback; hard failure raises `LLMUnavailableError`. Tool errors are captured and emitted as observations so the agent can adapt. Key logs include run_id, ticker, tool usage, and latency metrics.

## Testing & Verification
Module-level tool tests validate indicator math, chart outputs, and data loading. Agent tests mock the LLM client to confirm tool sequencing and SSE event formats. API integration tests exercise SSE streaming and report retrieval. Manual verification focuses on PDF appearance and client-side SSE consumption.
