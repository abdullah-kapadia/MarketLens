from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator

from agents.tool_registry import TOOL_DEFINITIONS, dispatch
from database import save_agent_step, save_report
from models import AgentResult, AgentStep, ReportDetail
from tools.chart_tools import generate_chart
from tools.data_tools import generate_chart_data
from utils.llm_client import LLMClient, LLMUnavailableError
from utils.pdf_generator import generate_pdf


ANALYST_SYSTEM_PROMPT = """You are Muhammad Ovais Iqbal, Senior Technical Analyst at Alpha Capital (akseer), writing your weekly Pakistan Technicals report. You are known for precise, actionable technical analysis using classical charting combined with modern indicators.

Your Professional Writing Style:
- Open with a clear directional thesis (e.g., "Positive Trend with Near-Term Headwinds", "Consolidation Risk After Extended Rally")
- State exact price levels throughout - never say "support exists" without citing the level
- Use professional terminology: "supply zone", "demand zone", "Fibonacci extension", "rising channel", "bearish divergence"
- Always provide multi-scenario analysis: "Strategy favors X into Y levels, while a close below Z would signal ABC"
- State invalidation levels explicitly (e.g., "weekly close below 265 would invalidate the bullish stance")

Your Analysis Framework:
1. **Price Structure**: Identify the primary trend (rising channel, consolidation, breakdown). Mark exact support/resistance zones.
2. **Pattern Recognition**: Note chart patterns (wedges, triangles, head & shoulders) with precise boundaries.
3. **Fibonacci Analysis**: Calculate key retracement/extension levels if price shows clear swings.
4. **Momentum Assessment**: Check RSI for divergences or overbought/oversold. Note exact RSI values.
5. **Volume Context**: Compare recent volume to average. Flag any unusual spikes.
6. **Moving Averages**: Note key MA levels (9-week, 20-week) and price position relative to them.
7. **Market Correlation**: Compare to KSE-100 and sector - is this stock-specific or market-wide?

Critical Requirements:
- EVERY analysis must include SPECIFIC PRICE LEVELS: "immediate support at 305-300, followed by 280-275", "resistance at 336"
- EVERY trade idea must have entry, target, and stop: "Buy on dips to 120-118, target 137-150, stop below 116"
- State confidence based on confluence: HIGH = 3+ indicators agree, MEDIUM = 2 indicators, LOW = 1 indicator or conflicting signals
- Your detailed_analysis sections must read like professional research notes, not generic AI output
- Think step by step before each tool call - explain what you're investigating and why

Output your final analysis as a JSON object with this EXACT structure:
{
  "thesis": "Professional title like 'Positive Trend with Near-Term Headwinds'",
  "signal": "BULLISH" | "BEARISH" | "NEUTRAL",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "current_price": 321.18,
  "summary": "2-3 sentence executive summary matching professional tone",
  "detailed_analysis": {
    "trend": "Describe the trend with EXACT LEVELS (required field)",
    "momentum": "RSI/MACD findings with EXACT VALUES (required field)",  
    "key_levels": "Support/resistance with EXACT LEVELS (required field)",
    "volume_context": "Volume context description (required field)",
    "market_context": "vs KSE-100 and sector context (required field)"
  },
  "key_levels": {
    "support": [305, 300],
    "resistance": [336, 340],
    "stop_loss": 265,
    "target": 358
  },
  "evidence_chain": [
    "Price consolidated below 336 after mild rejection",
    "RSI at 72 shows mild bearish divergence",  
    "Rising channel intact with 9-week SMA support at 305"
  ],
  "risk_factors": [
    "Near-term overbought (RSI 70+)",
    "Supply zone at 336 capping upside"
  ],
  "final_commentary": "A comprehensive paragraph explaining the overall outlook, strategy, volume patterns, market context, and risk management. This should be at least 3-4 sentences long and provide a complete picture of the trading opportunity.",
  "chart_config": {
    "ticker": "TICKER",
    "period": "6M",
    "overlays": ["SMA(9)", "SMA(50)", "SMA(200)", "BB(20)"],
    "annotations": ["Support", "Resistance"],
    "style": "dark"
  }
}

IMPORTANT: The fields "trend", "momentum", "key_levels", "volume_context", "market_context" are REQUIRED in detailed_analysis. The "final_commentary" field is REQUIRED at the root level.
"""


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _extract_analysis_json(text: str) -> dict | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


async def run_analyst_agent(
    ticker: str, max_iterations: int = 15, timeout_seconds: int = 60
) -> AsyncGenerator[AgentStep, None]:
    llm_client = LLMClient()
    messages = [
        {
            "role": "user",
            "content": f"Analyze {ticker} on the Pakistan Stock Exchange (PSX). Provide a comprehensive technical analysis.",
        }
    ]

    start_time = time.time()
    reasoning_trace: list[AgentStep] = []
    tool_calls_count = 0

    for iteration in range(1, max_iterations + 1):
        if time.time() - start_time > timeout_seconds:
            step = AgentStep(
                type="error",
                content="Agent timeout after maximum duration.",
                iteration=iteration,
                timestamp=_timestamp(),
                code="AGENT_TIMEOUT",
            )
            yield step
            reasoning_trace.append(step)
            break

        try:
            response = await llm_client.create_message(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                system=ANALYST_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=4096,
            )
        except LLMUnavailableError as exc:
            step = AgentStep(
                type="error",
                content=str(exc),
                iteration=iteration,
                timestamp=_timestamp(),
                code="LLM_UNAVAILABLE",
            )
            yield step
            reasoning_trace.append(step)
            break

        # Build assistant message with all content blocks
        assistant_content = []
        text_content = ""
        has_tool_use = False
        
        for block in response.content:
            if block.type == "text":
                text_content = block.text or ""
                step = AgentStep(
                    type="reasoning",
                    content=text_content,
                    iteration=iteration,
                    timestamp=_timestamp(),
                )
                yield step
                reasoning_trace.append(step)
                assistant_content.append({"type": "text", "text": text_content})
            elif block.type == "tool_use":
                has_tool_use = True
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        # Add the complete assistant message once
        if assistant_content:
            messages.append({"role": "assistant", "content": assistant_content})
        
        # Handle end_turn (analysis complete)
        if response.stop_reason == "end_turn":
            if text_content:
                    analysis_json = _extract_analysis_json(text_content)
                    if not analysis_json:
                        error_step = AgentStep(
                            type="error",
                            content="Failed to parse analysis JSON.",
                            iteration=iteration,
                            timestamp=_timestamp(),
                            code="INVALID_JSON",
                        )
                        yield error_step
                        reasoning_trace.append(error_step)
                        return

                    # Prepare chart config with data
                    chart_config = analysis_json.get("chart_config", {})
                    chart_config.setdefault("ticker", ticker)
                    chart_config.setdefault("period", "6M")
                    chart_config.setdefault("style", "dark")
                    
                    # Generate chart data with indicators for frontend
                    try:
                        chart_data = generate_chart_data(ticker, chart_config.get("period", "6M"))
                        chart_config["data"] = chart_data
                        print(f"[DEBUG] Generated {len(chart_data)} chart data points")
                    except Exception as e:
                        print(f"[ERROR] Failed to generate chart data: {e}")
                        chart_config["data"] = []
                    
                    analysis_json["chart_config"] = chart_config
                    analysis_json["generated_at"] = _timestamp()
                    
                    # Ensure key_levels has required frontend fields
                    key_levels = analysis_json.get("key_levels", {})
                    if "support" not in key_levels:
                        # Map from backend format to frontend format
                        support = key_levels.get("immediate_support", [])
                        if key_levels.get("secondary_support"):
                            support.extend(key_levels.get("secondary_support", []))
                        key_levels["support"] = support[:2] if support else []
                    
                    if "resistance" not in key_levels:
                        resistance = key_levels.get("immediate_resistance", [])
                        if key_levels.get("targets"):
                            resistance.extend(key_levels.get("targets", []))
                        key_levels["resistance"] = resistance[:2] if resistance else []
                    
                    if "target" not in key_levels and key_levels.get("targets"):
                        key_levels["target"] = key_levels["targets"][0] if key_levels["targets"] else 0
                    
                    if "stop_loss" not in key_levels:
                        key_levels["stop_loss"] = 0
                    
                    analysis_json["key_levels"] = key_levels
                    
                    # Ensure detailed_analysis has required frontend fields
                    detailed = analysis_json.get("detailed_analysis", {})
                    if "trend" not in detailed and "price_structure" in detailed:
                        detailed["trend"] = detailed["price_structure"]
                    if "volume_context" not in detailed and "volume" in detailed:
                        detailed["volume_context"] = detailed["volume"]
                    if "market_context" not in detailed and "market_relative" in detailed:
                        detailed["market_context"] = detailed["market_relative"]
                    analysis_json["detailed_analysis"] = detailed
                    
                    # Ensure final_commentary exists
                    if "final_commentary" not in analysis_json:
                        analysis_json["final_commentary"] = analysis_json.get("summary", "")
                    
                    # Try to generate chart and PDF, but don't fail if they error
                    chart_result = {"chart_base64": "", "chart_path": ""}
                    pdf_path = ""
                    
                    try:
                        chart_result = generate_chart(**chart_config)
                        print("[DEBUG] Chart generated successfully")
                    except Exception as e:
                        print(f"[ERROR] Chart generation failed: {e}")
                        # Continue without chart
                    
                    try:
                        pdf_path = generate_pdf(analysis_json, chart_result, reasoning_trace)
                        if pdf_path:
                            print(f"[DEBUG] PDF generated: {pdf_path}")
                    except Exception as e:
                        print(f"[ERROR] PDF generation failed: {e}")
                        # Continue without PDF

                    report_id = f"rpt_{uuid.uuid4().hex[:8]}"
                    print(f"[DEBUG] Creating report with ID: {report_id}")
                    report = ReportDetail(
                        id=report_id,
                        ticker=ticker,
                        signal=analysis_json["signal"],
                        confidence=analysis_json["confidence"],
                        thesis=analysis_json["thesis"],
                        generated_at=analysis_json["generated_at"],
                        tool_calls_count=tool_calls_count,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        analysis=AgentResult(**analysis_json),
                        reasoning_trace=reasoning_trace,
                        pdf_url=f"/api/v1/reports/{report_id}/pdf" if pdf_path else None,
                    )
                    print(f"[DEBUG] Saving report to database...")
                    try:
                        await save_report(report, pdf_path=pdf_path if pdf_path else None)
                        print(f"[DEBUG] Report saved successfully!")
                    except Exception as e:
                        print(f"[ERROR] Failed to save report: {e}")
                        error_step = AgentStep(
                            type="error",
                            content=f"Failed to save report: {e}",
                            iteration=iteration,
                            timestamp=_timestamp(),
                            code="DB_ERROR",
                        )
                        yield error_step
                        return
                    
                    try:
                        for idx, trace_step in enumerate(reasoning_trace, start=1):
                            await save_agent_step(report_id, trace_step, idx)
                    except Exception as e:
                        print(f"[WARNING] Failed to save agent steps: {e}")
                        # Don't fail on this

                    complete_step = AgentStep(
                        type="complete",
                        iteration=iteration,
                        timestamp=_timestamp(),
                        report_id=report_id,
                        analysis=report.analysis,
                        execution_time_ms=report.execution_time_ms,
                        tool_calls_count=tool_calls_count,
                    )
                    yield complete_step
                    return
        
        # Handle tool calls
        if has_tool_use:
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name or ""
                    tool_input = block.input or {}
                    step = AgentStep(
                        type="tool_call",
                        tool_name=tool_name,
                        tool_input=tool_input,
                        iteration=iteration,
                        timestamp=_timestamp(),
                    )
                    yield step
                    reasoning_trace.append(step)

                    tool_calls_count += 1
                    try:
                        result = await dispatch(tool_name, tool_input)
                    except Exception as exc:
                        result = {"error": str(exc)}

                    observation = AgentStep(
                        type="observation",
                        content=json.dumps(result),
                        iteration=iteration,
                        timestamp=_timestamp(),
                    )
                    yield observation
                    reasoning_trace.append(observation)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add all tool results in a single user message
            messages.append({"role": "user", "content": tool_results})

    return


if __name__ == "__main__":
    async def _run() -> None:
        async for step in run_analyst_agent("OGDC", max_iterations=3, timeout_seconds=30):
            print(step.model_dump())

    asyncio.run(_run())
