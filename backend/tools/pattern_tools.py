from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pandas_ta as ta

from tools.data_tools import load_dataframe


CANDLESTICK_PATTERNS = {
    "doji": ta.cdl_doji,
    "hammer": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="hammer"),
    "inverted_hammer": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="inverted_hammer"),
    "engulfing": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="engulfing"),
    "morning_star": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="morningstar"),
    "evening_star": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="eveningstar"),
    "three_white_soldiers": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="3whitesoldiers"),
    "three_black_crows": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="3blackcrows"),
    "harami": lambda o, h, l, c: ta.cdl_pattern(o, h, l, c, name="harami"),
}


def _pattern_description(name: str, signal: float) -> str:
    implication = "bullish" if signal > 0 else "bearish"
    readable = name.replace("_", " ").title()
    return f"{readable} pattern — {implication} reversal signal."


def _detect_candlestick_patterns(df: pd.DataFrame) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    recent = df.tail(10)

    for pattern_name, func in CANDLESTICK_PATTERNS.items():
        try:
            signal = func(recent["Open"], recent["High"], recent["Low"], recent["Close"])
            if signal is None:
                continue
            last_signal = float(signal.iloc[-1])
            if last_signal == 0:
                continue
            results.append(
                {
                    "name": pattern_name.replace("_", " ").title(),
                    "date": recent.index[-1].strftime("%Y-%m-%d"),
                    "confidence": min(abs(last_signal) / 100, 1.0),
                    "implication": "BULLISH" if last_signal > 0 else "BEARISH",
                    "description": _pattern_description(pattern_name, last_signal),
                }
            )
        except Exception:
            continue

    return results


def _local_extrema(series: pd.Series, order: int = 3) -> tuple[list[int], list[int]]:
    highs = []
    lows = []
    for i in range(order, len(series) - order):
        window = series.iloc[i - order : i + order + 1]
        if series.iloc[i] == window.max():
            highs.append(i)
        if series.iloc[i] == window.min():
            lows.append(i)
    return highs, lows


def _detect_double_top_bottom(df: pd.DataFrame) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    recent = df.tail(60)
    highs_idx, lows_idx = _local_extrema(recent["High"])

    if len(highs_idx) >= 2:
        first, second = highs_idx[-2], highs_idx[-1]
        p1 = recent["High"].iloc[first]
        p2 = recent["High"].iloc[second]
        if abs(p1 - p2) / p1 <= 0.03:
            results.append(
                {
                    "name": "Double Top",
                    "start_date": recent.index[first].strftime("%Y-%m-%d"),
                    "end_date": recent.index[second].strftime("%Y-%m-%d"),
                    "confidence": 0.6,
                    "implication": "BEARISH",
                    "description": "Two peaks at similar highs suggest resistance and potential downside.",
                }
            )

    if len(lows_idx) >= 2:
        first, second = lows_idx[-2], lows_idx[-1]
        p1 = recent["Low"].iloc[first]
        p2 = recent["Low"].iloc[second]
        if abs(p1 - p2) / p1 <= 0.03:
            results.append(
                {
                    "name": "Double Bottom",
                    "start_date": recent.index[first].strftime("%Y-%m-%d"),
                    "end_date": recent.index[second].strftime("%Y-%m-%d"),
                    "confidence": 0.6,
                    "implication": "BULLISH",
                    "description": "Two lows at similar levels suggest support and potential upside.",
                }
            )

    return results


def _slope(values: np.ndarray) -> float:
    x = np.arange(len(values))
    if len(values) < 2:
        return 0.0
    return float(np.polyfit(x, values, 1)[0])


def _detect_triangle(df: pd.DataFrame) -> list[dict[str, Any]]:
    recent = df.tail(60)
    highs = recent["High"].to_numpy()
    lows = recent["Low"].to_numpy()
    high_slope = _slope(highs)
    low_slope = _slope(lows)

    patterns: list[dict[str, Any]] = []
    if high_slope < -0.01 and low_slope > 0.01:
        patterns.append(
            {
                "name": "Symmetrical Triangle",
                "start_date": recent.index[0].strftime("%Y-%m-%d"),
                "end_date": recent.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.55,
                "implication": "NEUTRAL",
                "description": "Converging highs and lows suggest compression before breakout.",
            }
        )
    elif abs(high_slope) < 0.01 and low_slope > 0.01:
        patterns.append(
            {
                "name": "Ascending Triangle",
                "start_date": recent.index[0].strftime("%Y-%m-%d"),
                "end_date": recent.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.55,
                "implication": "BULLISH",
                "description": "Flat resistance with rising lows indicates upward pressure.",
            }
        )
    elif high_slope < -0.01 and abs(low_slope) < 0.01:
        patterns.append(
            {
                "name": "Descending Triangle",
                "start_date": recent.index[0].strftime("%Y-%m-%d"),
                "end_date": recent.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.55,
                "implication": "BEARISH",
                "description": "Lower highs with flat support indicate downside pressure.",
            }
        )

    return patterns


def _detect_channel_wedge_flag(df: pd.DataFrame) -> list[dict[str, Any]]:
    recent = df.tail(60)
    high_slope = _slope(recent["High"].to_numpy())
    low_slope = _slope(recent["Low"].to_numpy())
    patterns: list[dict[str, Any]] = []

    if high_slope > 0.01 and low_slope > 0.01:
        patterns.append(
            {
                "name": "Rising Channel",
                "start_date": recent.index[0].strftime("%Y-%m-%d"),
                "end_date": recent.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.5,
                "implication": "BULLISH",
                "description": "Parallel rising highs/lows suggest an orderly uptrend.",
            }
        )
    elif high_slope < -0.01 and low_slope < -0.01:
        patterns.append(
            {
                "name": "Falling Channel",
                "start_date": recent.index[0].strftime("%Y-%m-%d"),
                "end_date": recent.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.5,
                "implication": "BEARISH",
                "description": "Parallel declining highs/lows suggest an orderly downtrend.",
            }
        )

    # Simple flag detection: consolidation after a sharp move
    last_40 = df.tail(40)
    prior = last_40.iloc[:20]
    recent_window = last_40.iloc[20:]
    prior_range = prior["High"].max() - prior["Low"].min()
    recent_range = recent_window["High"].max() - recent_window["Low"].min()
    if prior_range > 0 and recent_range / prior_range < 0.35:
        patterns.append(
            {
                "name": "Flag",
                "start_date": recent_window.index[0].strftime("%Y-%m-%d"),
                "end_date": recent_window.index[-1].strftime("%Y-%m-%d"),
                "confidence": 0.45,
                "implication": "NEUTRAL",
                "description": "Tight consolidation after a sharp move suggests a flag pattern.",
            }
        )

    return patterns


def detect_patterns(ticker: str, pattern_type: str = "both") -> dict[str, Any]:
    df = load_dataframe(ticker, "6M")
    candlesticks = _detect_candlestick_patterns(df) if pattern_type in ("candlestick", "both") else []
    charts: list[dict[str, Any]] = []
    if pattern_type in ("chart", "both"):
        charts.extend(_detect_double_top_bottom(df))
        charts.extend(_detect_triangle(df))
        charts.extend(_detect_channel_wedge_flag(df))

    summary_parts = []
    if candlesticks:
        summary_parts.append(f"{len(candlesticks)} candlestick pattern(s)")
    if charts:
        summary_parts.append(f"{len(charts)} chart pattern(s)")
    summary = (
        f"{', '.join(summary_parts)} detected." if summary_parts else "No significant patterns detected."
    )

    return {
        "pattern_type": pattern_type,
        "candlestick_patterns": candlesticks,
        "chart_patterns": charts,
        "summary": summary,
    }


if __name__ == "__main__":
    print(detect_patterns("OGDC", "both"))
