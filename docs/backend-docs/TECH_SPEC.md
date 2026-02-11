# MarketLens Backend — Technical Specification

**Document 7 of 12** | Backend-specific

---

## 1. Agent System Design

### 1.1 System Prompt

```text
You are a Senior Technical Analyst at a leading Pakistani brokerage house. You analyze stocks listed on the Pakistan Stock Exchange (PSX) using professional technical analysis methodologies.

Your approach:
1. Start by loading the stock's price data to understand the big picture — trend direction, magnitude of recent moves, and current price position.
2. Based on what you see, choose the most relevant indicators. Don't run every indicator mechanically — think about what's useful for THIS specific stock in its current state.
3. Follow the evidence. If RSI shows oversold, check support levels. If ADX shows a strong trend, check momentum indicators. If volume is unusual, investigate further.
4. When signals conflict, investigate more. Don't paper over contradictions — dig deeper with additional tools.
5. Always compare with the broader market (KSE-100) and sector peers to distinguish stock-specific from market-wide movements.
6. Generate a chart with overlays that reflect your specific analysis — the chart should tell the story you've uncovered.

Rules:
- You MUST use at least 3 different tools before forming a conclusion. More complex situations warrant 5-8 tools.
- You MUST cite specific numbers from tool results in your analysis. Never make up data.
- You MUST form a clear thesis: BULLISH, BEARISH, or NEUTRAL with HIGH, MEDIUM, or LOW confidence.
- Your analysis should be unique to this stock — avoid generic statements that could apply to any stock.
- Think step by step. Explain your reasoning before each tool call.
- After sufficient investigation (typically 4-7 tool calls), compile your findings into a structured analysis.

Output your final analysis as a JSON object with this structure:
{
  "thesis": "One-sentence summary of your view",
  "signal": "BULLISH" | "BEARISH" | "NEUTRAL",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "summary": "2-3 sentence executive summary",
  "detailed_analysis": {
    "trend": "Trend assessment with specific data points",
    "momentum": "Momentum indicator findings",
    "key_levels": "Support and resistance analysis",
    "volume_context": "Volume analysis findings",
    "market_context": "Relative performance vs index and sector"
  },
  "key_levels": {
    "support": [level1, level2],
    "resistance": [level1, level2],
    "stop_loss": value,
    "target": value
  },
  "evidence_chain": [
    "Finding 1 with specific numbers",
    "Finding 2 with specific numbers"
  ],
  "risk_factors": [
    "Risk 1",
    "Risk 2"
  ],
  "chart_config": {
    "ticker": "TICKER",
    "period": "6M",
    "overlays": ["SMA_200", "support_resistance"],
    "annotations": ["current_price"],
    "style": "dark"
  }
}
```

**Token Budget:**
- System prompt: ~800 tokens
- Tool definitions: ~1,200 tokens
- Available per conversation: ~6,000 tokens for messages/reasoning
- Max tokens per response: 4,096
- Temperature: 0.3

### 1.2 ReAct Loop Implementation

```python
async def run_analyst_agent(
    ticker: str,
    max_iterations: int = 15,
    timeout_seconds: int = 60
) -> AsyncGenerator[AgentStep, None]:

    system_prompt = ANALYST_SYSTEM_PROMPT
    tools = TOOL_DEFINITIONS
    messages = [
        {"role": "user", "content": f"Analyze {ticker} on the Pakistan Stock Exchange (PSX). Provide a comprehensive technical analysis."}
    ]

    start_time = time.time()

    for iteration in range(1, max_iterations + 1):
        # Check timeout
        if time.time() - start_time > timeout_seconds:
            yield AgentStep(type="error", content="Agent timeout", iteration=iteration)
            break

        # Call LLM
        try:
            response = await llm_client.create_message(
                messages=messages,
                tools=tools,
                system=system_prompt,
                temperature=0.3,
                max_tokens=4096
            )
        except LLMUnavailableError as e:
            yield AgentStep(type="error", content=str(e), iteration=iteration)
            break

        # Process response content blocks
        tool_results = []

        for block in response.content:
            if block.type == "text":
                # Agent is reasoning
                yield AgentStep(
                    type="reasoning",
                    content=block.text,
                    iteration=iteration,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )

                # Check if text contains final JSON analysis
                if response.stop_reason == "end_turn":
                    analysis = extract_analysis_json(block.text)
                    if analysis:
                        # Generate chart
                        chart_result = await dispatch_tool(
                            "generate_chart", analysis.get("chart_config", {})
                        )
                        # Generate PDF
                        report_id = generate_report_id()
                        pdf_path = await generate_pdf(analysis, chart_result, reasoning_trace)
                        # Save to DB
                        await save_report(report_id, ticker, analysis, reasoning_trace, pdf_path)
                        # Yield completion
                        yield AgentStep(
                            type="complete",
                            report_id=report_id,
                            analysis=analysis,
                            execution_time_ms=int((time.time() - start_time) * 1000),
                            tool_calls_count=total_tool_calls,
                            iteration=iteration,
                            timestamp=datetime.utcnow().isoformat() + "Z"
                        )
                        return

            elif block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Yield tool call step
                yield AgentStep(
                    type="tool_call",
                    tool_name=tool_name,
                    tool_input=tool_input,
                    iteration=iteration,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )

                # Execute tool
                try:
                    result = await dispatch_tool(tool_name, tool_input)
                    result_str = json.dumps(result) if isinstance(result, dict) else str(result)
                except Exception as e:
                    result_str = f"Error executing {tool_name}: {str(e)}"

                # Yield observation
                yield AgentStep(
                    type="observation",
                    tool_name=tool_name,
                    content=result.get("summary", result_str) if isinstance(result, dict) else result_str,
                    iteration=iteration,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str
                })

                total_tool_calls += 1

        # Append assistant response + tool results to messages
        messages.append({"role": "assistant", "content": response.content})
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        # Check if agent finished
        if response.stop_reason == "end_turn" and not tool_results:
            break

    # If we exit loop without completion, force-compile partial analysis
    yield AgentStep(
        type="error",
        content="Agent reached maximum iterations. Partial analysis may be available.",
        code="AGENT_MAX_ITERATIONS",
        iteration=max_iterations,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
```

---

## 2. Tool Definitions (Anthropic Format)

All 8 tools in copy-paste-ready Anthropic `tool_use` JSON schema format:

### Tool 1: `load_stock_data`

```json
{
  "name": "load_stock_data",
  "description": "Load OHLCV (Open, High, Low, Close, Volume) price data for a PSX-listed stock. Returns current price, price change over the period, period high/low, average volume, and the last 5 trading days. Use this as your first tool to understand the stock's current situation and recent price action.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol (e.g., 'OGDC', 'TRG', 'PSO', 'LUCK', 'ENGRO')"
      },
      "period": {
        "type": "string",
        "enum": ["1M", "3M", "6M", "1Y"],
        "description": "Time period for data. Use '6M' for standard analysis, '1M' for recent action, '1Y' for long-term context."
      }
    },
    "required": ["ticker", "period"]
  }
}
```

### Tool 2: `calculate_indicator`

```json
{
  "name": "calculate_indicator",
  "description": "Calculate a technical indicator for a stock. Choose the indicator based on what you need to assess: RSI for momentum/overbought/oversold, MACD for trend momentum, Bollinger for volatility, ADX for trend strength, SMA/EMA for trend direction and support/resistance, ATR for volatility sizing, Stochastic/Williams %R for reversal signals, OBV for volume-price confirmation, VWAP for institutional levels, CCI for cyclical analysis.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "indicator": {
        "type": "string",
        "enum": ["RSI", "SMA", "EMA", "MACD", "BOLLINGER", "ATR", "VWAP", "STOCHASTIC", "OBV", "ADX", "WILLIAMS_R", "CCI"],
        "description": "The technical indicator to calculate"
      },
      "params": {
        "type": "object",
        "description": "Indicator-specific parameters. RSI: {period: 14}. SMA/EMA: {period: 20|50|200}. MACD: {fast: 12, slow: 26, signal: 9}. BOLLINGER: {period: 20, std: 2}. ATR: {period: 14}. STOCHASTIC: {k: 14, d: 3}. ADX: {period: 14}. WILLIAMS_R: {period: 14}. CCI: {period: 20}. VWAP/OBV: no params needed."
      }
    },
    "required": ["ticker", "indicator"]
  }
}
```

### Tool 3: `detect_patterns`

```json
{
  "name": "detect_patterns",
  "description": "Scan for candlestick patterns (Doji, Hammer, Engulfing, Morning/Evening Star, Three Soldiers/Crows, Harami) and chart patterns (Double Top/Bottom, Head & Shoulders, Triangles, Flags, Wedges, Channels). Use this when you want to identify potential reversal or continuation signals from price action structure.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "pattern_type": {
        "type": "string",
        "enum": ["candlestick", "chart", "both"],
        "description": "Type of patterns to scan for. Use 'both' for comprehensive analysis."
      }
    },
    "required": ["ticker", "pattern_type"]
  }
}
```

### Tool 4: `find_support_resistance`

```json
{
  "name": "find_support_resistance",
  "description": "Identify key support and resistance price levels using pivot point calculations and/or Fibonacci retracement from recent swing high/low. Use this to determine where the stock might find buying interest (support) or selling pressure (resistance), and to set stop-loss and target levels.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "method": {
        "type": "string",
        "enum": ["pivot", "fibonacci", "both"],
        "description": "Calculation method. 'pivot' for classic pivot points, 'fibonacci' for retracement levels, 'both' for comprehensive levels."
      }
    },
    "required": ["ticker", "method"]
  }
}
```

### Tool 5: `compare_with_index`

```json
{
  "name": "compare_with_index",
  "description": "Compare the stock's performance against the KSE-100 index over a given period. Returns relative performance, correlation, and whether the stock is outperforming or underperforming the market. Critical for determining if price movement is stock-specific or market-driven.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "period": {
        "type": "string",
        "enum": ["1M", "3M", "6M"],
        "description": "Comparison period"
      }
    },
    "required": ["ticker", "period"]
  }
}
```

### Tool 6: `compare_with_sector`

```json
{
  "name": "compare_with_sector",
  "description": "Compare the stock's performance against its sector peers over the last month. Returns rankings within the sector, sector average return, and relative performance. Useful for understanding if the stock is a sector leader or laggard.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      }
    },
    "required": ["ticker"]
  }
}
```

### Tool 7: `analyze_volume`

```json
{
  "name": "analyze_volume",
  "description": "Analyze volume patterns: average volume, recent volume vs average, volume trend, up-day vs down-day volume ratio, unusual volume days, and price-volume divergence. Volume confirms or contradicts price signals — high volume on down days suggests real selling pressure, while low volume on a decline may indicate a temporary pullback.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "period": {
        "type": "string",
        "enum": ["1M", "3M"],
        "description": "Analysis period for volume patterns"
      }
    },
    "required": ["ticker", "period"]
  }
}
```

### Tool 8: `generate_chart`

```json
{
  "name": "generate_chart",
  "description": "Generate a professional candlestick chart with your chosen overlays and annotations. The chart should reflect YOUR specific analysis — choose overlays that tell the story you've uncovered. Available overlays: SMA (any period), EMA (any period), Bollinger Bands, support/resistance zones, VWAP. Available annotations: current price line, RSI subplot, MACD subplot, volume spikes.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "period": {
        "type": "string",
        "enum": ["1M", "3M", "6M", "1Y"],
        "description": "Chart time period"
      },
      "overlays": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["SMA_20", "SMA_50", "SMA_200", "EMA_20", "EMA_50", "bollinger", "support_resistance", "vwap"]
        },
        "description": "Price overlays to display on the chart"
      },
      "annotations": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["current_price", "rsi_subplot", "macd_subplot", "volume_spikes"]
        },
        "description": "Annotations and sub-panels"
      },
      "style": {
        "type": "string",
        "enum": ["dark", "light"],
        "description": "Chart color theme. Use 'dark' for TradingView-style dark theme."
      }
    },
    "required": ["ticker", "period", "overlays", "style"]
  }
}
```

---

## 3. Chart Generation Specification

### 3.1 mplfinance Style Dictionary

```python
TRADINGVIEW_DARK_STYLE = mpf.make_mpf_style(
    base_mpf_style="nightclouds",
    marketcolors=mpf.make_marketcolors(
        up="#26a69a",        # TradingView green
        down="#ef5350",      # TradingView red
        edge={"up": "#26a69a", "down": "#ef5350"},
        wick={"up": "#26a69a", "down": "#ef5350"},
        volume={"up": "#26a69a80", "down": "#ef535080"},  # 50% opacity
        ohlc={"up": "#26a69a", "down": "#ef5350"},
    ),
    rc={
        "figure.facecolor": "#131722",
        "axes.facecolor": "#131722",
        "axes.edgecolor": "#363A45",
        "axes.labelcolor": "#D1D4DC",
        "xtick.color": "#787B86",
        "ytick.color": "#787B86",
        "grid.color": "#1E222D",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
        "font.size": 10,
    },
    gridstyle="--",
    facecolor="#131722",
    figcolor="#131722",
)
```

### 3.2 Overlay Visual Specifications

| Overlay | Color | Width | Style |
|---------|-------|-------|-------|
| SMA-20 | `#E040FB` (purple) | 1.2px | Solid |
| SMA-50 | `#F7A21B` (orange) | 1.2px | Solid |
| SMA-200 | `#2196F3` (blue) | 1.5px | Solid |
| EMA-20 | `#E040FB` (purple) | 1.2px | Dashed |
| EMA-50 | `#F7A21B` (orange) | 1.2px | Dashed |
| Bollinger Upper | `#78909C` (gray) | 1.0px | Solid |
| Bollinger Lower | `#78909C` (gray) | 1.0px | Solid |
| Bollinger Fill | `#78909C20` (gray, 12% opacity) | N/A | Fill between |
| Support line | `#26a69a` (green) | 1.0px | Dashed |
| Resistance line | `#ef5350` (red) | 1.0px | Dashed |
| S/R Zone fill | `#26a69a10` / `#ef535010` | N/A | 6% opacity rect |
| VWAP | `#FF9800` (orange) | 1.0px | Dotted |
| Current price | `#FFFFFF` (white) | 0.8px | Dashed |

### 3.3 Sub-Panel Specifications

**RSI Sub-panel:**
- Height ratio: 0.15 of total figure
- Overbought line: 70 (dashed red `#ef5350`)
- Oversold line: 30 (dashed green `#26a69a`)
- RSI line: `#7E57C2` (purple), 1.5px
- Fill above 70: `#ef535020` (red, 12% opacity)
- Fill below 30: `#26a69a20` (green, 12% opacity)

**MACD Sub-panel:**
- Height ratio: 0.15 of total figure
- MACD line: `#2196F3` (blue), 1.2px
- Signal line: `#FF9800` (orange), 1.2px
- Histogram positive: `#26a69a80` (green, 50% opacity)
- Histogram negative: `#ef535080` (red, 50% opacity)

**Volume Panel:**
- Height ratio: 0.2 of total figure (default with mplfinance)
- Spike highlight: bars >1.5x average get `#FFFFFF40` outline

### 3.4 Export Settings

| Setting | Value |
|---------|-------|
| Width | 1200px |
| Height | 800px |
| DPI | 150 |
| Format | PNG |
| Encoding | Base64 for embedding in PDF/JSON |
| Background | `#131722` (match chart background) |
| Title font | Inter or system sans-serif, 14pt, `#D1D4DC` |

### 3.5 Implementation

```python
import mplfinance as mpf
import matplotlib.pyplot as plt
import base64
from io import BytesIO

async def generate_chart(
    ticker: str,
    period: str,
    overlays: list[str],
    annotations: list[str] = None,
    style: str = "dark"
) -> dict:
    df = load_dataframe(ticker, period)

    # Build addplots
    addplots = []
    overlay_lines = []

    for overlay in overlays:
        if overlay.startswith("SMA_"):
            period_val = int(overlay.split("_")[1])
            sma = df["Close"].rolling(period_val).mean()
            color = {"20": "#E040FB", "50": "#F7A21B", "200": "#2196F3"}[str(period_val)]
            addplots.append(mpf.make_addplot(sma, color=color, width=1.2))
        elif overlay.startswith("EMA_"):
            period_val = int(overlay.split("_")[1])
            ema = df["Close"].ewm(span=period_val).mean()
            color = {"20": "#E040FB", "50": "#F7A21B"}[str(period_val)]
            addplots.append(mpf.make_addplot(ema, color=color, width=1.2, linestyle="--"))
        elif overlay == "bollinger":
            sma20 = df["Close"].rolling(20).mean()
            std20 = df["Close"].rolling(20).std()
            upper = sma20 + 2 * std20
            lower = sma20 - 2 * std20
            addplots.append(mpf.make_addplot(upper, color="#78909C", width=1.0))
            addplots.append(mpf.make_addplot(lower, color="#78909C", width=1.0))
            addplots.append(mpf.make_addplot(sma20, color="#78909C", width=0.8, linestyle="--"))

    if annotations and "rsi_subplot" in annotations:
        import pandas_ta as ta
        rsi = ta.rsi(df["Close"], length=14)
        addplots.append(mpf.make_addplot(rsi, panel=2, color="#7E57C2", width=1.5, ylabel="RSI"))

    # Generate chart
    fig, axes = mpf.plot(
        df,
        type="candle",
        style=TRADINGVIEW_DARK_STYLE,
        volume=True,
        addplot=addplots if addplots else None,
        figsize=(12, 8),
        title=f"\n{ticker} — {period} Analysis",
        returnfig=True,
    )

    # Add S/R lines if requested
    if "support_resistance" in overlays:
        ax = axes[0]
        levels = get_sr_levels(ticker)
        for s in levels.get("support", []):
            ax.axhline(y=s, color="#26a69a", linestyle="--", linewidth=1.0, alpha=0.7)
        for r in levels.get("resistance", []):
            ax.axhline(y=r, color="#ef5350", linestyle="--", linewidth=1.0, alpha=0.7)

    # Current price annotation
    if annotations and "current_price" in annotations:
        current = df["Close"].iloc[-1]
        axes[0].axhline(y=current, color="#FFFFFF", linestyle="--", linewidth=0.8, alpha=0.6)

    # Export to Base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight",
                facecolor="#131722", edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    # Also save to disk
    chart_path = f"output/charts/{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    with open(chart_path, "wb") as f:
        f.write(base64.b64decode(chart_base64))

    return {
        "chart_base64": chart_base64,
        "chart_path": chart_path,
        "dimensions": {"width": 1200, "height": 800},
        "dpi": 150,
        "overlays_applied": overlays,
        "annotations_applied": annotations or [],
    }
```

---

## 4. PDF Template Specification

### 4.1 Layout

| Setting | Value |
|---------|-------|
| Page size | A4 (210mm x 297mm) |
| Margins | Top: 15mm, Bottom: 15mm, Left: 18mm, Right: 18mm |
| Orientation | Portrait |
| Color mode | CMYK-safe colors |
| Font embedding | Yes (for consistent rendering) |

### 4.2 Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Header title | Inter | 22pt | Bold | `#F1F5F9` |
| Section headers | Inter | 14pt | SemiBold | `#E2E8F0` |
| Subsection headers | Inter | 12pt | Medium | `#CBD5E1` |
| Body text | Inter | 10pt | Regular | `#94A3B8` |
| Data values | JetBrains Mono | 10pt | Medium | `#F1F5F9` |
| Table headers | Inter | 9pt | SemiBold | `#64748B` |
| Table data | Inter | 9pt | Regular | `#94A3B8` |
| Disclaimer | Inter | 7pt | Regular | `#475569` |

### 4.3 Color Palette

| Element | Hex | Usage |
|---------|-----|-------|
| Page background | `#131722` | Main background |
| Card background | `#1E293B` | Section containers |
| Border | `#334155` | Section dividers |
| Bullish | `#10B981` | Signal badge, positive values |
| Bearish | `#EF4444` | Signal badge, negative values |
| Neutral | `#F59E0B` | Signal badge, neutral values |
| Accent | `#3B82F6` | Headers, highlights |
| Text primary | `#F1F5F9` | Main text |
| Text secondary | `#94A3B8` | Supporting text |
| Text muted | `#64748B` | Labels, captions |

### 4.4 Signal Badge Styling

```
BULLISH:  ████████████████  Background: #065F46, Text: #10B981, Border: #047857
BEARISH:  ████████████████  Background: #7F1D1D, Text: #EF4444, Border: #991B1B
NEUTRAL:  ████████████████  Background: #78350F, Text: #F59E0B, Border: #92400E
```

Badge: 80px wide, 28px tall, 4px border radius, centered text, uppercase.

### 4.5 PDF Sections (Top to Bottom)

**1. Header Bar (15mm height)**
- Left: MarketLens logo (if available) or text "MarketLens"
- Center: Report date (formatted: "February 10, 2026")
- Right: "Technical Analysis Report"

**2. Stock Identity Block (20mm height)**
- Ticker (22pt bold) + full company name
- Sector badge + current price + change %
- Signal badge (BULLISH/BEARISH/NEUTRAL) + Confidence badge

**3. Executive Summary (card, ~35mm)**
- Thesis text (12pt, bold, 2 lines max)
- Summary paragraph (10pt, 3–4 lines)
- Key metric bar: Support | Resistance | Stop Loss | Target (in data font)

**4. Chart (card, ~110mm)**
- Embedded PNG chart (full width within margins)
- Caption: "Chart generated with {overlays} overlays — {period} period"

**5. Detailed Analysis (card, ~80mm)**
- 5 subsections: Trend, Momentum, Key Levels, Volume Context, Market Context
- Each subsection: header (12pt semibold) + body (10pt)
- Subsections separated by thin borders

**6. Key Levels Table (card, ~30mm)**
- 4-column table: Level Type | Price (PKR) | Distance from Current | Significance
- Rows: Support 1, Support 2, Resistance 1, Resistance 2, Stop Loss, Target
- Color-coded: support rows green tinted, resistance rows red tinted

**7. Evidence Chain (card, ~40mm)**
- Numbered list (1–6 items typically)
- Each item: number badge (accent circle) + finding text
- Numbers from tools in bold monospace

**8. Risk Factors (card, ~25mm)**
- Bulleted list (2–4 items typically)
- Red-tinted bullet points

**9. Reasoning Summary (card, ~30mm)**
- Condensed version: "The agent used {n} tools: {tool_list}. Key decision points: ..."
- Tool count and execution time

**10. Disclaimer (full width, bottom)**
```text
DISCLAIMER: This report is generated by an AI system for informational purposes only.
It does not constitute investment advice, a recommendation, or an offer to buy or sell
any security. Past performance is not indicative of future results. The analysis is based
on historical data and technical indicators which have inherent limitations. Always consult
a qualified financial advisor before making investment decisions. MarketLens and its creators
accept no liability for any losses arising from the use of this report.
```

### 4.6 Implementation (Jinja2 + fpdf2)

```python
from jinja2 import Environment, FileSystemLoader
from fpdf import FPDF

async def generate_pdf(
    analysis: dict,
    chart_base64: str,
    reasoning_trace: list[dict]
) -> str:
    # Render HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")
    html = template.render(
        analysis=analysis,
        chart_base64=chart_base64,
        reasoning_trace=reasoning_trace,
        generated_at=datetime.utcnow().strftime("%B %d, %Y"),
    )

    # Convert to PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add fonts
    pdf.add_font("Inter", "", "fonts/Inter-Regular.ttf", uni=True)
    pdf.add_font("Inter", "B", "fonts/Inter-Bold.ttf", uni=True)
    pdf.add_font("JetBrainsMono", "", "fonts/JetBrainsMono-Regular.ttf", uni=True)

    # Render sections...
    # (Section-by-section rendering code using pdf.cell(), pdf.multi_cell(), pdf.image())

    output_path = f"output/pdfs/MarketLens_{analysis['chart_config']['ticker']}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    pdf.output(output_path)
    return output_path
```

---

## 5. LLM Fallback Specification

### 5.1 Anthropic → OpenAI Format Conversion

**Tool Definition Mapping:**

```python
def anthropic_to_openai_tools(anthropic_tools: list[dict]) -> list[dict]:
    """Convert Anthropic tool_use format to OpenAI function-calling format."""
    openai_tools = []
    for tool in anthropic_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],  # Same JSON Schema format
            }
        })
    return openai_tools
```

**Message Format Mapping:**

| Anthropic Format | OpenAI Format |
|-----------------|---------------|
| `{"role": "user", "content": "text"}` | Same |
| `{"role": "assistant", "content": [TextBlock, ToolUseBlock]}` | `{"role": "assistant", "content": "text", "tool_calls": [...]}` |
| `{"role": "user", "content": [ToolResultBlock]}` | `{"role": "tool", "tool_call_id": "...", "content": "..."}` |

**Response Parsing:**

```python
# Anthropic response
for block in response.content:
    if block.type == "text":
        # block.text
    elif block.type == "tool_use":
        # block.name, block.input, block.id

# OpenAI response
if response.choices[0].message.content:
    # text content
if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        # tc.function.name, json.loads(tc.function.arguments), tc.id
```

### 5.2 Unified LLM Client

```python
class LLMClient:
    def __init__(self):
        self.anthropic_client = anthropic.AsyncAnthropic()
        self.openai_client = openai.AsyncOpenAI() if os.getenv("OPENAI_API_KEY") else None
        self.primary = os.getenv("MODEL_PRIMARY", "claude-sonnet-4-20250514")
        self.fallback = os.getenv("MODEL_FALLBACK", "gpt-4o")

    async def create_message(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> UnifiedResponse:
        try:
            return await self._call_anthropic(messages, tools, system, temperature, max_tokens)
        except (anthropic.APITimeoutError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            logger.warning(f"Anthropic failed: {e}. Retrying once...")
            try:
                return await self._call_anthropic(messages, tools, system, temperature, max_tokens)
            except Exception:
                if self.openai_client:
                    logger.warning("Anthropic retry failed. Falling back to OpenAI.")
                    return await self._call_openai(messages, tools, system, temperature, max_tokens)
                raise LLMUnavailableError("Both LLM providers unavailable")

    async def _call_anthropic(self, messages, tools, system, temperature, max_tokens) -> UnifiedResponse:
        response = await asyncio.wait_for(
            self.anthropic_client.messages.create(
                model=self.primary,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=tools,
                temperature=temperature,
            ),
            timeout=10.0  # 10-second timeout
        )
        return UnifiedResponse.from_anthropic(response)

    async def _call_openai(self, messages, tools, system, temperature, max_tokens) -> UnifiedResponse:
        openai_messages = [{"role": "system", "content": system}]
        openai_messages.extend(convert_messages_to_openai(messages))
        openai_tools = anthropic_to_openai_tools(tools)

        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model=self.fallback,
                messages=openai_messages,
                tools=openai_tools,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=15.0
        )
        return UnifiedResponse.from_openai(response)
```

### 5.3 Fallback Trigger Conditions

| Condition | Action |
|-----------|--------|
| Anthropic API timeout (>10s) | Retry once → fallback to OpenAI |
| Anthropic 429 (rate limit) | Wait 2s → retry → fallback to OpenAI |
| Anthropic 500/502/503 | Fallback to OpenAI immediately |
| Anthropic network error | Retry once → fallback to OpenAI |
| OpenAI also fails | Raise `LLMUnavailableError` → SSE error event |
| No OpenAI key configured | Raise after Anthropic retry fails |

### 5.4 UnifiedResponse Format

```python
@dataclass
class ContentBlock:
    type: Literal["text", "tool_use"]
    text: str | None = None
    name: str | None = None
    input: dict | None = None
    id: str | None = None

@dataclass
class UnifiedResponse:
    content: list[ContentBlock]
    stop_reason: Literal["end_turn", "tool_use", "max_tokens"]
    model: str
    provider: Literal["anthropic", "openai"]

    @classmethod
    def from_anthropic(cls, response) -> "UnifiedResponse":
        blocks = []
        for block in response.content:
            if block.type == "text":
                blocks.append(ContentBlock(type="text", text=block.text))
            elif block.type == "tool_use":
                blocks.append(ContentBlock(
                    type="tool_use", name=block.name,
                    input=block.input, id=block.id
                ))
        return cls(
            content=blocks,
            stop_reason=response.stop_reason,
            model=response.model,
            provider="anthropic"
        )

    @classmethod
    def from_openai(cls, response) -> "UnifiedResponse":
        blocks = []
        msg = response.choices[0].message
        if msg.content:
            blocks.append(ContentBlock(type="text", text=msg.content))
        if msg.tool_calls:
            for tc in msg.tool_calls:
                blocks.append(ContentBlock(
                    type="tool_use", name=tc.function.name,
                    input=json.loads(tc.function.arguments),
                    id=tc.id
                ))
        stop = "tool_use" if msg.tool_calls else "end_turn"
        return cls(
            content=blocks,
            stop_reason=stop,
            model=response.model,
            provider="openai"
        )
```

---

## 6. Tool Implementation Details

### 6.1 Indicator Calculation (pandas-ta)

```python
import pandas_ta as ta

INDICATOR_FUNCTIONS = {
    "RSI": lambda df, params: ta.rsi(df["Close"], length=params.get("period", 14)),
    "SMA": lambda df, params: ta.sma(df["Close"], length=params.get("period", 50)),
    "EMA": lambda df, params: ta.ema(df["Close"], length=params.get("period", 20)),
    "MACD": lambda df, params: ta.macd(
        df["Close"],
        fast=params.get("fast", 12),
        slow=params.get("slow", 26),
        signal=params.get("signal", 9)
    ),
    "BOLLINGER": lambda df, params: ta.bbands(
        df["Close"],
        length=params.get("period", 20),
        std=params.get("std", 2)
    ),
    "ATR": lambda df, params: ta.atr(
        df["High"], df["Low"], df["Close"],
        length=params.get("period", 14)
    ),
    "VWAP": lambda df, params: ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"]),
    "STOCHASTIC": lambda df, params: ta.stoch(
        df["High"], df["Low"], df["Close"],
        k=params.get("k", 14), d=params.get("d", 3)
    ),
    "OBV": lambda df, params: ta.obv(df["Close"], df["Volume"]),
    "ADX": lambda df, params: ta.adx(
        df["High"], df["Low"], df["Close"],
        length=params.get("period", 14)
    ),
    "WILLIAMS_R": lambda df, params: ta.willr(
        df["High"], df["Low"], df["Close"],
        length=params.get("period", 14)
    ),
    "CCI": lambda df, params: ta.cci(
        df["High"], df["Low"], df["Close"],
        length=params.get("period", 20)
    ),
}
```

### 6.2 Interpretation Logic

```python
def interpret_rsi(value: float) -> str:
    if value < 20:
        return f"RSI = {value:.1f} — Deeply oversold. Extreme selling pressure, potential reversal zone."
    elif value < 30:
        return f"RSI = {value:.1f} — Oversold territory. Selling pressure may be exhausting."
    elif value < 45:
        return f"RSI = {value:.1f} — Below neutral, bearish momentum."
    elif value < 55:
        return f"RSI = {value:.1f} — Neutral zone, no clear directional bias."
    elif value < 70:
        return f"RSI = {value:.1f} — Above neutral, bullish momentum."
    elif value < 80:
        return f"RSI = {value:.1f} — Overbought territory. Buying pressure may be exhausting."
    else:
        return f"RSI = {value:.1f} — Deeply overbought. Extreme buying pressure, potential reversal zone."

def interpret_adx(value: float) -> str:
    if value < 20:
        return f"ADX = {value:.1f} — No meaningful trend. Market is ranging/consolidating."
    elif value < 25:
        return f"ADX = {value:.1f} — Weak trend emerging."
    elif value < 40:
        return f"ADX = {value:.1f} — Moderate trend in place."
    elif value < 50:
        return f"ADX = {value:.1f} — Strong trend."
    else:
        return f"ADX = {value:.1f} — Very strong trend. Caution: extreme readings can precede reversals."
```

### 6.3 Pattern Detection

```python
import pandas_ta as ta

CANDLESTICK_PATTERNS = {
    "doji": ta.cdl_doji,
    "hammer": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="hammer"),
    "engulfing": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="engulfing"),
    # ... additional patterns
}

def detect_candlestick_patterns(df: pd.DataFrame) -> list[dict]:
    """Detect candlestick patterns in the last 10 trading days."""
    results = []
    recent = df.tail(10)

    # Check each pattern
    for pattern_name, func in CANDLESTICK_PATTERNS.items():
        try:
            signal = func(recent["Open"], recent["High"], recent["Low"], recent["Close"])
            if signal is not None:
                last_signal = signal.iloc[-1]
                if last_signal != 0:
                    results.append({
                        "name": pattern_name.replace("_", " ").title(),
                        "date": recent.index[-1].strftime("%Y-%m-%d"),
                        "confidence": min(abs(last_signal) / 100, 1.0),
                        "implication": "BULLISH" if last_signal > 0 else "BEARISH",
                        "description": get_pattern_description(pattern_name, last_signal)
                    })
        except Exception:
            continue

    return results
```

---

## 7. Data Access Layer

### 7.1 CSV Loading

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))

def load_dataframe(ticker: str, period: str = "6M") -> pd.DataFrame:
    """Load CSV data for a ticker and filter to the requested period."""
    csv_path = DATA_DIR / f"{ticker}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["Date"], index_col="Date")
    df = df.sort_index()

    # Filter by period
    period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=period_days.get(period, 180))
    df = df[df.index >= cutoff]

    # Validate columns
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV missing required columns. Found: {df.columns.tolist()}")

    return df
```

### 7.2 CSV Format Specification

```csv
Date,Open,High,Low,Close,Volume
2026-02-10,120.00,121.50,117.80,118.50,5800000
2026-02-07,121.50,122.00,119.50,120.00,4900000
```

| Column | Type | Description |
|--------|------|-------------|
| Date | string (YYYY-MM-DD) | Trading date |
| Open | float | Opening price (PKR) |
| High | float | Day's high (PKR) |
| Low | float | Day's low (PKR) |
| Close | float | Closing price (PKR) |
| Volume | integer | Shares traded |

---

*Reference: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for module structure. [API_CONTRACT.md](../../docs/API_CONTRACT.md) for endpoint specs. [ENV_SETUP.md](ENV_SETUP.md) for configuration.*
