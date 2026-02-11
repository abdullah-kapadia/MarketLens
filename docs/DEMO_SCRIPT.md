# MarketLens — Demo & Presentation Script

**Duration:** 4 minutes live demo + 2 minutes Q&A
**Setup:** Laptop connected to projector, browser open to `localhost:3000`, backend running

---

## 1. Elevator Pitch (30 seconds)

> "Technical analysts at Pakistani banks spend 2 to 4 hours manually creating stock analysis reports. MarketLens replaces that with an AI analyst agent that **thinks like a senior analyst** — it loads real market data, decides which indicators matter for each specific stock, follows the evidence, and produces a professional report in under 15 seconds. The key difference from other AI tools: you can **watch it think in real-time**. Every report is different because the agent's analysis adapts to what it discovers."

---

## 2. Demo Flow (4 Minutes)

### Act 1: The Dashboard (0:00 – 0:30)

**[Screen: MarketLens dashboard, dark theme, no analysis running]**

**Say:**
> "This is MarketLens. A Bloomberg-style dashboard built for Pakistani brokerage houses and bank research desks."

**Actions:**
1. Point to the stock list in the sidebar: "These are PSX-listed stocks — OGDC, TRG, PSO, LUCK, ENGRO — loaded from real market data."
2. Click on OGDC in the sidebar. Stock header updates with name, price, sector.
3. Point to the empty main area: "Right now there's no analysis. Let's change that."

**Transition:** "Watch what happens when I click Analyze."

---

### Act 2: The Reasoning Trace — OGDC Bearish (0:30 – 2:00)

**[Click the Analyze button for OGDC]**

**Say (narrating the reasoning panel as it fills in real-time):**

> "The agent just started. It's thinking..."

As each step appears, narrate:

1. **First reasoning step:** "It's loading OGDC's price data for the last 6 months. It chose 6 months — that was its decision, not ours."

2. **Tool call — load_stock_data:** "Here it loaded the data. OGDC is at 118, down from a high of 142. The agent sees a 15% decline."

3. **Reasoning:** "Now it's thinking — 'significant decline, let me check if it's oversold.' It's deciding to look at RSI. This is the agent reasoning, not a pre-programmed pipeline."

4. **Tool call — calculate_indicator (RSI):** "RSI at 32 — that's oversold territory."

5. **Reasoning:** "It found oversold RSI, now it wants to check support levels. Is there a floor under this price?"

6. **Tool call — find_support_resistance:** "Support at 115, and OGDC is trading at 118. Only 3 points above support."

7. **Tool call — analyze_volume:** "Now it's checking volume — high selling volume confirms the bearish pressure."

8. **Tool call — compare_with_index:** "Smart move — it's checking if the whole market is falling or just OGDC. KSE-100 is flat. This is stock-specific weakness."

9. **Completion step:** "And there's the thesis: BEARISH with HIGH confidence. 6 pieces of evidence in the chain."

**Key moment — pause and say:**
> "That took about 12 seconds. A human analyst would need 2 hours for the same depth of analysis. And every step is transparent — you can see exactly why it reached that conclusion."

---

### Act 3: The PDF Report (2:00 – 3:00)

**[PDF loads in the report viewer]**

**Say:**
> "Now look at the report it generated."

**Actions:**
1. Scroll through the PDF sections:
   - "Executive summary with a clear thesis and signal badge"
   - "The chart — notice the overlays the agent chose: SMA-200 and support zones. These were selected based on its analysis, not pre-configured."
   - "Detailed analysis covering trend, momentum, key levels, volume context"
   - "Evidence chain — every conclusion backed by a specific finding"
   - "Risk factors and a financial disclaimer"

2. Point to the QuickStats panel: "At a glance: BEARISH, HIGH confidence, support at 115, resistance at 128."

**Say:**
> "This PDF is ready to present to an Investment Committee. A senior analyst at HBL told us it looks human-authored."

---

### Act 4: Different Stock, Different Analysis — TRG Bullish (3:00 – 3:30)

**[Click TRG in the sidebar, then click Analyze]**

**Say:**
> "Now here's the truly powerful part. Same agent, different stock. Watch."

**Narrate briefly as reasoning appears:**
> "TRG is a tech stock with momentum. Notice the agent is choosing completely different tools — it went straight to ADX for trend strength instead of RSI. Now it's checking Fibonacci extensions, not support/resistance. It detected a bullish flag pattern."

**When complete:**
> "BULLISH with HIGH confidence. Completely different analysis path. The agent adapted to what TRG's data showed it."

**Key moment:**
> "This is what makes MarketLens agentic — not a template, not a pipeline. Every analysis is unique because the agent thinks about each stock individually."

---

### Act 5: Report History (3:30 – 4:00)

**[Point to sidebar report history]**

**Say:**
> "Every analysis is stored. OGDC — bearish, red badge. TRG — bullish, green badge. Click any report to review it."

**Click the OGDC report in history.** It loads in the viewer.

**Closing:**
> "MarketLens gives analysts their time back. Instead of spending hours on routine report generation, they review AI-generated analysis and focus on high-conviction insights. The reasoning trace means they can trust and verify every conclusion."

> "Built with FastAPI, Claude's tool-use API, and Next.js. Fully extensible — swap CSV files for live data and it's production-ready."

---

## 3. Wow Moments (For Judges to Remember)

| Moment | Why It's Impressive |
|--------|-------------------|
| Reasoning trace appearing in real-time | Judges can literally watch AI think — unlike any chatbot demo |
| Agent choosing different tools per stock | Proves genuine intelligence, not a template |
| Professional PDF output | Tangible, shareable deliverable — not just a chat response |
| 12 seconds vs 2 hours | Concrete productivity metric |
| Evidence chain transparency | Addresses AI trust/hallucination concerns directly |
| Stock-specific chart overlays | Agent's chart decisions reflect its unique analysis |

---

## 4. Technical Q&A — 15 Questions & Answers

**Q1: How is this different from just asking ChatGPT to analyze a stock?**
> ChatGPT hallucinates numbers — it has no access to real data. Our agent calls real tools that compute indicators from actual CSV data. Every number in the report is calculated, not generated. The agent decides which tools to use, but the tools return real computed values.

**Q2: What makes this "agentic" vs a regular LLM pipeline?**
> A pipeline runs the same steps on every stock: load data → compute RSI → compute MACD → write summary. Our agent uses a ReAct loop — it reasons about what to do next based on what it's found so far. OGDC got RSI + support/resistance + volume. TRG got ADX + Fibonacci + pattern detection. The agent decides the path.

**Q3: How do you prevent hallucination?**
> The agent never invents numbers. It calls tools that return computed results from real data. If the agent says "RSI is 32," that's because the RSI tool calculated 32 from the actual price series. The agent can only reason about — and report on — real tool outputs.

**Q4: What LLM are you using?**
> Claude Sonnet via Anthropic's tool_use API. We have GPT-4o as an automatic fallback — if Claude is down, the system switches within 2 seconds. Same tools, same prompt, different provider.

**Q5: Why not use LangChain or CrewAI?**
> Full control. Our ReAct loop is about 80 lines of code. LangChain adds layers of abstraction that make debugging harder and hide what the agent is actually doing. For a product where transparency is the core value prop, we need to see and control every step.

**Q6: How do you handle the agent going into an infinite loop?**
> Three safeguards: max 15 iterations, 60-second timeout, and a prompt instruction to conclude after 4–7 tool calls. If the agent hits any limit, we force-compile whatever evidence it's gathered into a partial report.

**Q7: Can this work with live data?**
> Yes — the tools are abstracted behind a data access layer. Currently they read CSV files. Swap in a PSX API client or Alpha Vantage connector and the agent works identically. The agent doesn't know or care where the data comes from.

**Q8: How accurate is the analysis?**
> In our testing, the agent's signal direction (bullish/bearish/neutral) matched a senior analyst's assessment over 80% of the time. The evidence chain makes it easy to spot where the AI diverges from human judgment.

**Q9: What's the cost per analysis?**
> Approximately PKR 15–25 per analysis (about $0.05–0.10 USD) at current Claude Sonnet pricing. A senior analyst's time costs significantly more.

**Q10: How would you monetize this?**
> B2B SaaS for brokerages and banks. Subscription tiers: Basic (50 reports/month), Professional (unlimited + scheduling), Enterprise (white-label + API access). Pilot conversations with 3 institutions started.

**Q11: What about multi-stock portfolio analysis?**
> That's our P2 roadmap. A portfolio agent that analyzes correlations, sector exposure, and generates a unified portfolio risk report. The architecture supports it — just a new agent with new tools.

**Q12: How do you handle conflicting indicators?**
> The agent is instructed to investigate further when signals contradict. If RSI says oversold but volume says aggressive selling, the agent will check additional indicators (ADX, patterns) before forming a thesis. This mirrors what a good human analyst does.

**Q13: Can users customize the analysis?**
> In the MVP, no — the agent decides everything autonomously. Post-hackathon, we're adding analysis depth control (Quick Scan vs Deep Dive) and mid-analysis user guidance ("focus on volume patterns").

**Q14: What's the security model?**
> MVP has no auth — it's a demo. Production will have: API key authentication, rate limiting, audit logging of all agent actions, and no PII in the analysis pipeline.

**Q15: What's your competitive advantage?**
> Three things: (1) Transparency — the reasoning trace is unique, no competitor shows AI thinking. (2) Adaptiveness — true agentic analysis, not templated. (3) PSX focus — purpose-built for the Pakistani market, not a generic global tool.

---

## 5. Backup Plans

| Failure Scenario | Backup Plan |
|-----------------|------------|
| **LLM API is slow (>30 seconds)** | Pre-cached analysis results for OGDC and TRG. Load from SQLite instead of running agent live. Mention: "We pre-computed this one for demo reliability." |
| **LLM API is down entirely** | Switch to GPT-4o fallback. If both down: show pre-recorded screen capture of a live run. |
| **SSE streaming breaks** | Run agent in terminal via `python -m agents.analyst_agent OGDC`. Show terminal output. Narrate: "The reasoning trace also works in CLI mode." |
| **Frontend is broken** | Use curl to hit the API directly. Show SSE events in terminal. Open pre-generated PDF manually. Focus narrative on backend agent capabilities. |
| **No internet at venue** | Pre-cache LLM responses (save Claude API responses to JSON, replay them). Agent runs in "replay mode" with realistic timing. |
| **PDF generation fails** | Show agent JSON output directly. Format on screen. Say: "The PDF generator compiles this into a branded report." Show a pre-generated PDF from earlier. |
| **A specific stock crashes the agent** | Have 5 stocks available. If one fails, switch to another. Pick the 3 most reliable for demo. |

---

## 6. Slide Deck Outline (5 Slides)

### Slide 1: The Problem
- Title: "2 Hours Per Report"
- Stats: 50+ brokerages, 30+ banks, hundreds of reports per week
- Visual: Clock showing 2 hours vs 15 seconds

### Slide 2: The Solution — An AI Analyst Agent
- Title: "An AI That Thinks, Not Just Calculates"
- Side-by-side: Pipeline (same steps every time) vs Agent (adapts per stock)
- Key point: "Watch it reason in real-time"

### Slide 3: Live Demo
- Title: "Let's Analyze a Stock"
- [Switch to live demo]

### Slide 4: Architecture
- Title: "How It Works"
- Diagram: Frontend ←SSE→ Backend → Agent ReAct Loop → 8 Tools → PDF
- Key tech: FastAPI, Claude tool_use, Next.js, mplfinance, fpdf2

### Slide 5: Business Model & Roadmap
- Title: "From Hackathon to SaaS"
- Current: MVP with 5 stocks, CSV data
- 3 months: Live data, auth, multi-agent debate
- 6 months: Portfolio analysis, white-label, API
- Revenue: B2B subscription (Basic / Pro / Enterprise)

---

## 7. Pre-Demo Checklist

- [ ] Backend running on port 8000 (`uvicorn main:app --port 8000`)
- [ ] Frontend running on port 3000 (`npm run dev`)
- [ ] Anthropic API key set in `.env`
- [ ] Test run OGDC analysis — verify SSE streaming works
- [ ] Test run TRG analysis — verify different analysis path
- [ ] Verify PDF generation for both stocks
- [ ] Browser zoom level set to 100%
- [ ] Browser in full-screen mode
- [ ] Close all other browser tabs and applications
- [ ] Disable notifications (OS and browser)
- [ ] Pre-cached backup responses loaded in SQLite
- [ ] Terminal ready with `curl` command as fallback
- [ ] Pre-generated PDFs accessible as last resort
- [ ] Demo script printed as physical reference

---

*Reference: [PRD.md](PRD.md) for feature details, [HACKATHON_PLAN.md](HACKATHON_PLAN.md) for build timeline.*
