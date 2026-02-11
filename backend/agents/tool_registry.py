from __future__ import annotations

from typing import Any, Callable

from tools import (
    chart_tools,
    comparison_tools,
    data_tools,
    indicator_tools,
    level_tools,
    pattern_tools,
    volume_tools,
)


TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "load_stock_data",
        "description": "Load stock OHLCV data and compute summary stats.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "period": {"type": "string", "enum": ["1M", "3M", "6M", "1Y"]},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "calculate_indicator",
        "description": "Calculate a technical indicator using pandas-ta.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "indicator": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["ticker", "indicator"],
        },
    },
    {
        "name": "detect_patterns",
        "description": "Detect candlestick and chart patterns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "pattern_type": {"type": "string", "enum": ["candlestick", "chart", "both"]},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "find_support_resistance",
        "description": "Find key support and resistance levels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "method": {"type": "string", "enum": ["pivot", "fibonacci", "both"]},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "compare_with_index",
        "description": "Compare a stock with KSE-100 index performance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "period": {"type": "string", "enum": ["1M", "3M", "6M", "1Y"]},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "compare_with_sector",
        "description": "Compare stock performance with sector peers.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "analyze_volume",
        "description": "Analyze volume trends and unusual activity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "period": {"type": "string", "enum": ["1M", "3M", "6M", "1Y"]},
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "generate_chart",
        "description": "Generate a candlestick chart with overlays and annotations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "period": {"type": "string"},
                "overlays": {"type": "array", "items": {"type": "string"}},
                "annotations": {"type": "array", "items": {"type": "string"}},
                "style": {"type": "string", "enum": ["dark", "light"]},
            },
            "required": ["ticker"],
        },
    },
]


TOOL_DISPATCH: dict[str, Callable[..., Any]] = {
    "load_stock_data": data_tools.load_stock_data,
    "calculate_indicator": indicator_tools.calculate_indicator,
    "detect_patterns": pattern_tools.detect_patterns,
    "find_support_resistance": level_tools.find_support_resistance,
    "compare_with_index": comparison_tools.compare_with_index,
    "compare_with_sector": comparison_tools.compare_with_sector,
    "analyze_volume": volume_tools.analyze_volume,
    "generate_chart": chart_tools.generate_chart,
}


async def dispatch(tool_name: str, tool_input: dict) -> dict:
    if tool_name not in TOOL_DISPATCH:
        raise ValueError(f"Unknown tool: {tool_name}")
    handler = TOOL_DISPATCH[tool_name]
    return handler(**tool_input)
