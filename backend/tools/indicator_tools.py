from __future__ import annotations

from typing import Any, Callable

import pandas as pd
import pandas_ta as ta

from tools.data_tools import load_dataframe


def _trend_label(current: float, previous: float) -> str:
    if current > previous:
        return "rising"
    if current < previous:
        return "declining"
    return "flat"


def interpret_rsi(value: float) -> str:
    if value < 20:
        return f"RSI = {value:.1f} — Deeply oversold. Extreme selling pressure, potential reversal zone."
    if value < 30:
        return f"RSI = {value:.1f} — Oversold territory. Selling pressure may be exhausting."
    if value < 45:
        return f"RSI = {value:.1f} — Below neutral, bearish momentum."
    if value < 55:
        return f"RSI = {value:.1f} — Neutral zone, no clear directional bias."
    if value < 70:
        return f"RSI = {value:.1f} — Above neutral, bullish momentum."
    if value < 80:
        return f"RSI = {value:.1f} — Overbought territory. Buying pressure may be exhausting."
    return f"RSI = {value:.1f} — Deeply overbought. Extreme buying pressure, potential reversal zone."


def interpret_adx(value: float) -> str:
    if value < 20:
        return f"ADX = {value:.1f} — No meaningful trend. Market is ranging/consolidating."
    if value < 25:
        return f"ADX = {value:.1f} — Weak trend emerging."
    if value < 40:
        return f"ADX = {value:.1f} — Moderate trend in place."
    if value < 50:
        return f"ADX = {value:.1f} — Strong trend."
    return f"ADX = {value:.1f} — Very strong trend. Caution: extreme readings can precede reversals."


def interpret_sma(price: float, sma: float) -> str:
    direction = "above" if price >= sma else "below"
    distance = abs(price - sma) / sma * 100 if sma else 0.0
    return f"Price is {direction} SMA at {sma:.2f} by {distance:.1f}%."


def interpret_ema(price: float, ema: float) -> str:
    direction = "above" if price >= ema else "below"
    distance = abs(price - ema) / ema * 100 if ema else 0.0
    return f"Price is {direction} EMA at {ema:.2f} by {distance:.1f}%."


def interpret_macd(macd: float, signal: float, hist: float) -> str:
    bias = "bullish" if hist > 0 else "bearish"
    return f"MACD {macd:.2f} vs signal {signal:.2f} — histogram {hist:.2f} ({bias} momentum)."


def interpret_bollinger(price: float, lower: float, upper: float) -> str:
    if price <= lower:
        return f"Price {price:.2f} is at or below lower band ({lower:.2f}) — oversold risk."
    if price >= upper:
        return f"Price {price:.2f} is at or above upper band ({upper:.2f}) — overbought risk."
    return f"Price {price:.2f} is within Bollinger bands ({lower:.2f}–{upper:.2f})."


def interpret_atr(value: float) -> str:
    return f"ATR = {value:.2f} — current volatility level."


def interpret_vwap(price: float, vwap: float) -> str:
    direction = "above" if price >= vwap else "below"
    return f"Price {price:.2f} is {direction} VWAP at {vwap:.2f}."


def interpret_stochastic(value: float) -> str:
    if value < 20:
        return f"Stochastic = {value:.1f} — Oversold territory."
    if value > 80:
        return f"Stochastic = {value:.1f} — Overbought territory."
    return f"Stochastic = {value:.1f} — Neutral zone."


def interpret_obv(trend: str) -> str:
    return f"OBV trend is {trend}, indicating {'accumulation' if trend == 'rising' else 'distribution' if trend == 'declining' else 'stability'}."


def interpret_williams_r(value: float) -> str:
    if value <= -80:
        return f"Williams %R = {value:.1f} — Oversold."
    if value >= -20:
        return f"Williams %R = {value:.1f} — Overbought."
    return f"Williams %R = {value:.1f} — Neutral."


def interpret_cci(value: float) -> str:
    if value <= -100:
        return f"CCI = {value:.1f} — Oversold."
    if value >= 100:
        return f"CCI = {value:.1f} — Overbought."
    return f"CCI = {value:.1f} — Neutral."


INDICATOR_FUNCTIONS: dict[str, Callable[[pd.DataFrame, dict], Any]] = {
    "RSI": lambda df, params: ta.rsi(df["Close"], length=params.get("period", 14)),
    "SMA": lambda df, params: ta.sma(df["Close"], length=params.get("period", 50)),
    "EMA": lambda df, params: ta.ema(df["Close"], length=params.get("period", 20)),
    "MACD": lambda df, params: ta.macd(
        df["Close"],
        fast=params.get("fast", 12),
        slow=params.get("slow", 26),
        signal=params.get("signal", 9),
    ),
    "BOLLINGER": lambda df, params: ta.bbands(
        df["Close"],
        length=params.get("period", 20),
        std=params.get("std", 2),
    ),
    "ATR": lambda df, params: ta.atr(
        df["High"], df["Low"], df["Close"], length=params.get("period", 14)
    ),
    "VWAP": lambda df, params: ta.vwap(
        df["High"], df["Low"], df["Close"], df["Volume"]
    ),
    "STOCHASTIC": lambda df, params: ta.stoch(
        df["High"],
        df["Low"],
        df["Close"],
        k=params.get("k", 14),
        d=params.get("d", 3),
    ),
    "OBV": lambda df, params: ta.obv(df["Close"], df["Volume"]),
    "ADX": lambda df, params: ta.adx(
        df["High"], df["Low"], df["Close"], length=params.get("period", 14)
    ),
    "WILLIAMS_R": lambda df, params: ta.willr(
        df["High"], df["Low"], df["Close"], length=params.get("period", 14)
    ),
    "CCI": lambda df, params: ta.cci(
        df["High"], df["Low"], df["Close"], length=params.get("period", 20)
    ),
}


def calculate_indicator(ticker: str, indicator: str, params: dict | None = None) -> dict:
    params = params or {}
    indicator_key = indicator.upper()
    if indicator_key not in INDICATOR_FUNCTIONS:
        raise ValueError(f"Unsupported indicator: {indicator}")

    df = load_dataframe(ticker, params.get("period", "6M"))
    result = INDICATOR_FUNCTIONS[indicator_key](df, params)

    if isinstance(result, pd.DataFrame):
        series = result.iloc[:, 0]
    else:
        series = result

    series = series.dropna()
    if series.empty or len(series) < 2:
        raise ValueError(f"Insufficient data for {indicator}")

    current = float(series.iloc[-1])
    previous = float(series.iloc[-2])
    trend = _trend_label(current, previous)

    price = float(df["Close"].iloc[-1])

    if indicator_key == "RSI":
        interpretation = interpret_rsi(current)
    elif indicator_key == "SMA":
        interpretation = interpret_sma(price, current)
    elif indicator_key == "EMA":
        interpretation = interpret_ema(price, current)
    elif indicator_key == "MACD":
        macd_line = float(result.iloc[-1, 0])
        signal_line = float(result.iloc[-1, 2])
        hist = float(result.iloc[-1, 1])
        interpretation = interpret_macd(macd_line, signal_line, hist)
        current = macd_line
        previous = float(result.iloc[-2, 0])
        trend = _trend_label(current, previous)
    elif indicator_key == "BOLLINGER":
        lower = float(result.iloc[-1, 0])
        upper = float(result.iloc[-1, 2])
        interpretation = interpret_bollinger(price, lower, upper)
    elif indicator_key == "ATR":
        interpretation = interpret_atr(current)
    elif indicator_key == "VWAP":
        interpretation = interpret_vwap(price, current)
    elif indicator_key == "STOCHASTIC":
        interpretation = interpret_stochastic(current)
    elif indicator_key == "OBV":
        interpretation = interpret_obv(trend)
    elif indicator_key == "ADX":
        interpretation = interpret_adx(current)
    elif indicator_key == "WILLIAMS_R":
        interpretation = interpret_williams_r(current)
    elif indicator_key == "CCI":
        interpretation = interpret_cci(current)
    else:
        interpretation = f"{indicator_key} = {current:.2f}"

    return {
        "indicator": indicator_key,
        "params": params,
        "value": round(current, 4),
        "interpretation": interpretation,
        "data": {"current": round(current, 4), "previous": round(previous, 4), "trend": trend},
    }


if __name__ == "__main__":
    print(calculate_indicator("OGDC", "RSI", {"period": 14}))
