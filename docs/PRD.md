# MarketLens — Product Requirements Document

**Version:** 1.0
**Date:** February 2026
**Author:** MarketLens Team
**Status:** Approved for Hackathon MVP

---

## 1. Problem Statement

### 1.1 The Pain

Technical analysts at Pakistani banks and brokerage houses spend **2–4 hours per stock** manually assembling technical analysis reports. The process is:

- **Repetitive:** Pull up charts in TradingView, screenshot, paste into Word/PowerPoint, write commentary, format, export PDF. Repeat for every stock.
- **Inconsistent:** Every analyst follows a different process. One checks RSI + MACD. Another uses Bollinger Bands + Fibonacci. Reports look different, read differently, and reach conclusions via incomparable methods.
- **Error-prone:** Manual indicator calculations, misread chart patterns, copy-paste mistakes in price levels. A single wrong support level can mislead an investment committee.
- **Unscalable:** A senior analyst can produce 3–4 quality reports per day. A research desk covering 20 stocks falls behind every week.
- **Opaque:** The final PDF shows conclusions but not the reasoning chain. An investment committee reading "BEARISH — RSI oversold" has no way to audit whether the analyst checked volume confirmation, sector context, or contradictory signals.

### 1.2 The Market

Pakistan's capital markets are growing:

- **PSX (Pakistan Stock Exchange)** has 500+ listed companies with a combined market cap exceeding PKR 9 trillion.
- **50+ brokerage houses** and **30+ banks** with active treasury/investment departments produce daily/weekly technical reports.
- Existing tools like TradingView and Bloomberg Terminal provide **data and charts** but do not generate **complete, reasoned analysis reports**. Analysts still manually interpret and write.
- There is no product in the Pakistani market that automates the full report generation pipeline with transparent, auditable AI reasoning.

### 1.3 Why Existing Tools Fall Short

| Tool | What It Does | What It Doesn't Do |
|------|-------------|-------------------|
| TradingView | Charts, indicators, alerts | Doesn't write analysis or generate reports |
| Bloomberg Terminal | Comprehensive data, some AI features | Expensive ($24K/yr), no auto-generated TA reports for PSX |
| ChatGPT/Claude (raw) | Can discuss stocks in general | No access to real data, no tools, no structured output, halluccinates numbers |
| Screener.pk | PSX data and basic screening | No analysis, no reports, no AI |

**MarketLens fills the gap:** real market data + AI agent that reasons like an analyst + professional PDF output.

---

## 2. Product Vision

### 2.1 One-Liner

> **"An AI analyst that thinks, not just calculates."**

MarketLens is not a template engine that runs the same indicators on every stock and fills in blanks. It is a **genuine AI agent** that loads data, decides what to investigate, follows the evidence, changes course when signals contradict, and produces a unique, reasoned analysis for every stock — just like a senior human analyst would.

### 2.2 Hackathon Scope (4 Days)

A working prototype demonstrating the core agentic loop:

- 5–6 Pakistani stocks + KSE-100 index from pre-downloaded CSV data
- One-click analysis with **live reasoning trace** streaming to the UI
- Professional PDF report output
- Report history with signal badges

### 2.3 6-Month Vision

A production SaaS platform for Pakistani financial institutions:

- Live PSX data feeds
- Multi-agent architecture (Bull vs Bear debate, Judge synthesis)
- Portfolio-level analysis
- White-label reports with custom branding
- Scheduled daily/weekly report generation
- API access for integration with existing research workflows
- User authentication, team management, audit trails

### 2.4 Differentiation

| Feature | Other "AI Stock" Tools | MarketLens |
|---------|----------------------|------------|
| Analysis approach | Fixed pipeline: always RSI + MACD + summary | Agent decides per stock: might use Fibonacci for one, ADX for another |
| Transparency | Black box — shows conclusion only | Live reasoning trace — watch the agent think |
| Adaptiveness | Same template for all stocks | Different stocks get different analysis paths |
| Output | Chat response or basic chart | Professional A4 PDF with chart, levels, evidence chain |
| Data integrity | Often hallucinated numbers | All numbers from real tool calculations on real CSV data |

---

## 3. User Personas

### 3.1 Persona 1: Saad Ahmed — Senior Technical Analyst

| Attribute | Detail |
|-----------|--------|
| **Role** | Senior Technical Analyst at AKD Securities |
| **Experience** | 8 years on PSX |
| **Goals** | Produce 6–8 quality reports per day instead of 3–4. Focus on high-conviction calls rather than routine coverage. |
| **Pain Points** | Spends 60% of time on formatting and boilerplate. Junior analysts produce inconsistent reports he must review and correct. |
| **How MarketLens Helps** | Generates first-draft reports in 15 seconds. Saad reviews the reasoning trace to validate the AI's logic, makes adjustments, and publishes. His throughput triples. He values the **reasoning trace** because it lets him audit the AI's work the same way he'd review a junior analyst. |

### 3.2 Persona 2: Dr. Amina Malik — Head of Research

| Attribute | Detail |
|-----------|--------|
| **Role** | Head of Research at Habib Bank Limited (HBL) |
| **Experience** | 15 years, manages a team of 6 analysts |
| **Goals** | Standardized report format across her team. Consistent methodology. Defensible recommendations for the Investment Committee. |
| **Pain Points** | Every analyst on her team produces reports that look and read differently. IC members complain about inconsistency. Onboarding new analysts takes months. |
| **How MarketLens Helps** | Every report follows the same professional structure: thesis, evidence chain, key levels, risk factors. The agent's methodology is consistent and auditable. She values **consistency and professional output**. |

### 3.3 Persona 3: Faisal Raza — Treasury Department Manager

| Attribute | Detail |
|-----------|--------|
| **Role** | Treasury Manager at MCB Bank |
| **Experience** | 12 years in banking, 5 in treasury |
| **Goals** | Quick daily assessment of 10–15 stocks the bank holds positions in. Needs to brief the CFO by 10 AM. |
| **Pain Points** | Relies on overnight research reports that are stale by market open. Can't wait for analysts to produce intraday updates. Needs speed. |
| **How MarketLens Helps** | Generates a full analysis in 15 seconds. Faisal can scan all positions before the morning meeting. He values **speed and reliability**. |

---

## 4. Feature Requirements

### 4.1 P0 — Hackathon MVP (4 Days)

These features are required for the hackathon demo:

| # | Feature | Description | Priority |
|---|---------|-------------|----------|
| F1 | Stock Selection Dashboard | Bloomberg-style dark UI. Sidebar with 5–6 Pakistani stocks (OGDC, TRG, PSO, LUCK, ENGRO) + KSE-100 index. Click to select. | P0 |
| F2 | One-Click Analysis | "Analyze" button triggers the AI agent. Single click, no configuration needed. | P0 |
| F3 | Live Reasoning Trace Panel | **THE killer feature.** Real-time SSE stream showing agent's thinking process: what it's loading, which indicators it chose, what it found, how it's reasoning. Updates live as agent works. | P0 |
| F4 | AI Analyst Agent (8 Tools) | Claude-powered ReAct agent with 8 tools: load_stock_data, calculate_indicator, detect_patterns, find_support_resistance, compare_with_index, compare_with_sector, analyze_volume, generate_chart. | P0 |
| F5 | Adaptive Analysis | Different stocks produce different analysis paths. OGDC (bearish near support) gets different tools/sequence than TRG (bullish momentum). Agent decides, not a pipeline. | P0 |
| F6 | Professional Chart | mplfinance candlestick chart with agent-selected overlays (SMA, EMA, Bollinger, S/R zones). TradingView dark theme styling. | P0 |
| F7 | LLM-Generated Analysis | Structured output: thesis, signal (BULLISH/BEARISH/NEUTRAL), confidence (HIGH/MEDIUM/LOW), evidence chain, key levels, risk factors. | P0 |
| F8 | PDF Report | Branded A4 PDF with: header, executive summary, chart, detailed analysis, key levels table, evidence chain, risk factors, reasoning summary, disclaimer. | P0 |
| F9 | Report History | Sidebar showing past reports with signal badges (green/red/amber). Click to view. | P0 |
| F10 | PDF Preview | In-app PDF viewer using react-pdf. Download button. | P0 |
| F11 | Dark Mode UI | Bloomberg Terminal-inspired dark theme. Information-dense but clean. | P0 |
| F12 | LLM Fallback | Claude primary, GPT-4o fallback. Automatic switch within 2 seconds if Claude is down. | P0 |

### 4.2 P1 — Post-Hackathon

| # | Feature | Description |
|---|---------|-------------|
| F13 | Live Data Feed | PSX API or Alpha Vantage integration replacing CSV files |
| F14 | Multi-Agent Debate | Bull agent vs Bear agent. Judge agent synthesizes into balanced report. |
| F15 | Analysis Depth Control | Quick Scan (3 tools, 5 seconds) vs Deep Dive (8+ tools, 20 seconds) |
| F16 | Mid-Analysis Redirect | User can inject guidance while agent is running ("focus on volume") |
| F17 | Authentication | User login, team accounts, API key management |
| F18 | Email Delivery | Scheduled report delivery via email |
| F19 | Custom Date Range | Analyze specific historical periods |

### 4.3 P2 — Future

| # | Feature | Description |
|---|---------|-------------|
| F20 | Portfolio Agent | Multi-stock analysis: correlations, sector allocation, risk assessment |
| F21 | Sector Rotation Agent | Identifies which sectors are gaining/losing momentum |
| F22 | Morning Brief Agent | Daily market summary covering top movers, key levels, overnight developments |
| F23 | Scheduled Reports | Cron-based automatic report generation |
| F24 | White-Label | Custom branding per client (bank logo, colors, disclaimer) |
| F25 | API Access | REST API for external systems to trigger analysis |
| F26 | Agent Memory | Agent remembers past analyses, tracks thesis evolution over time |

---

## 5. Non-Functional Requirements

| Requirement | Target | Notes |
|-------------|--------|-------|
| Agent analysis time | 5–15 seconds | 4–8 tool calls, each taking 1–3 seconds via LLM |
| LLM latency per step | 1–3 seconds | Acceptable — user watches the live reasoning trace |
| PDF generation | < 3 seconds | After agent completes |
| Total end-to-end | < 20 seconds | From click to PDF ready |
| Chart quality | 1200x800px, 150dpi PNG | Print-ready for A4 PDF |
| PDF quality | A4, print-ready, 300dpi charts | Professional output suitable for Investment Committee |
| LLM fallback | Claude to GPT-4o within 2 seconds | Transparent to user |
| Agent safety | Max 15 iterations, 60-second timeout | Prevents runaway loops |
| Concurrent users | 5 (hackathon) | Single-threaded agent per request |
| Data freshness | CSV-based (static in MVP) | Updated manually for hackathon |
| Browser support | Chrome 90+, Firefox 90+, Safari 15+ | Desktop-first |

---

## 6. Success Metrics

### 6.1 Hackathon Success

| Metric | Target |
|--------|--------|
| Live reasoning trace works end-to-end | Yes/No |
| Different stocks produce visibly different analysis paths | Demonstrate with 3 stocks |
| PDF output looks professional (would pass for human-authored) | Judge feedback |
| Demo completes without errors | 3 consecutive clean runs |
| Audience reaction to live reasoning trace | "Wow" factor |

### 6.2 Post-Hackathon Success

| Metric | Target |
|--------|--------|
| Time per report | 2 hours manual → 15 seconds automated |
| Report quality | Matches senior analyst conclusion >80% of the time |
| User satisfaction | NPS > 50 from pilot users |
| Adoption | 3 pilot institutions within 3 months |
| Agent consistency | Same stock analyzed 5 times produces consistent signal direction |

---

## 7. Constraints

| Constraint | Detail |
|-----------|--------|
| Data source | CSV files only in hackathon (no live API) |
| Authentication | None in hackathon MVP |
| API keys | Anthropic API key required; OpenAI optional for fallback |
| Market | PSX (Pakistan Stock Exchange) stocks only |
| Agent minimum | At least 3 tool calls per analysis (no shortcutting) |
| No LangChain/CrewAI | Custom ReAct loop using raw Anthropic SDK |
| No WeasyPrint | Use fpdf2 or Playwright for PDF generation |
| Two-project architecture | Backend (Python/FastAPI) and Frontend (Next.js) are independent repos |
| Hackathon timeline | 4 days, 1–2 developers |

---

## 8. Technical Architecture Overview

See [API_CONTRACT.md](API_CONTRACT.md) for the full interface specification between backend and frontend.

```
                    MarketLens Architecture

  ┌──────────────────────┐     ┌──────────────────────────┐
  │   marketlens-backend  │     │   marketlens-frontend    │
  │   (Python/FastAPI)    │◄───►│   (Next.js/TypeScript)   │
  │                       │ API │                          │
  │   Port: 8000          │ SSE │   Port: 3000             │
  └──────────────────────┘     └──────────────────────────┘
         │                                │
     Own repo                         Own repo
     Own docs                         Own docs
     Own Docker                       Own Docker
```

The **only contract** between them is the REST + SSE API specification. A backend dev and a frontend dev can work in parallel without conflicts.

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Claude API downtime during demo | Critical | Low | GPT-4o fallback + pre-cached demo responses |
| Agent produces inconsistent/wrong analysis | High | Medium | Minimum 3 tool calls, self-review prompt, real data only (no hallucination) |
| SSE streaming breaks in production | High | Medium | Fallback: poll for report completion via REST |
| PDF generation slow or broken | Medium | Low | Pre-generate demo PDFs as backup |
| 4-day timeline too aggressive | High | Medium | Strict P0 scope, mock data fallbacks, parallel dev tracks |
| Anthropic API costs | Low | Low | ~$0.05–0.10 per analysis at current Sonnet pricing |

---

## 10. Glossary

| Term | Definition |
|------|-----------|
| **PSX** | Pakistan Stock Exchange |
| **KSE-100** | Karachi Stock Exchange 100 Index — benchmark index for PSX |
| **ReAct** | Reason + Act — an AI agent pattern where the model alternates between reasoning and taking actions |
| **Tool Use** | Claude/GPT-4o API feature allowing the model to call defined functions during generation |
| **SSE** | Server-Sent Events — HTTP-based protocol for real-time server-to-client streaming |
| **OHLCV** | Open, High, Low, Close, Volume — standard price data format |
| **RSI** | Relative Strength Index — momentum oscillator (0–100) |
| **MACD** | Moving Average Convergence Divergence — trend-following momentum indicator |
| **Bollinger Bands** | Volatility bands placed above/below a moving average |
| **ATR** | Average True Range — volatility indicator |
| **ADX** | Average Directional Index — trend strength indicator (0–100) |
| **Fibonacci Retracement** | Support/resistance levels based on Fibonacci ratios (23.6%, 38.2%, 50%, 61.8%) |

---

*This PRD is the source of truth for MarketLens scope and requirements. All implementation documents reference this document.*
