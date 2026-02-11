from __future__ import annotations

from typing import Any

from tools.data_tools import load_dataframe


def _pivot_levels(high: float, low: float, close: float) -> dict[str, float]:
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    return {
        "r2": round(r2, 2),
        "r1": round(r1, 2),
        "pivot": round(pivot, 2),
        "s1": round(s1, 2),
        "s2": round(s2, 2),
    }


def _fibonacci_levels(high: float, low: float) -> dict[str, float]:
    diff = high - low
    return {
        "0.0_high": round(high, 2),
        "0.236": round(high - diff * 0.236, 2),
        "0.382": round(high - diff * 0.382, 2),
        "0.5": round(high - diff * 0.5, 2),
        "0.618": round(high - diff * 0.618, 2),
        "1.0_low": round(low, 2),
    }


def find_support_resistance(ticker: str, method: str = "both") -> dict[str, Any]:
    df = load_dataframe(ticker, "6M")
    last_row = df.iloc[-1]
    period_high = float(df["High"].max())
    period_low = float(df["Low"].min())

    pivot_levels = _pivot_levels(float(last_row["High"]), float(last_row["Low"]), float(last_row["Close"]))
    fib_levels = _fibonacci_levels(period_high, period_low)

    key_support = sorted({pivot_levels["s1"], pivot_levels["s2"], fib_levels["0.618"], fib_levels["1.0_low"]})
    key_resistance = sorted({pivot_levels["r1"], pivot_levels["r2"], fib_levels["0.236"], fib_levels["0.0_high"]})

    summary = (
        f"Nearest support at {key_support[0]:.2f}, "
        f"nearest resistance at {key_resistance[-2]:.2f}."
    )

    result = {
        "method": method,
        "current_price": round(float(last_row["Close"]), 2),
        "key_support": [round(v, 2) for v in key_support[:2]],
        "key_resistance": [round(v, 2) for v in key_resistance[-2:]],
        "summary": summary,
    }

    if method in ("pivot", "both"):
        result["pivot_levels"] = pivot_levels
    if method in ("fibonacci", "both"):
        result["fibonacci_levels"] = fib_levels

    return result


if __name__ == "__main__":
    print(find_support_resistance("OGDC", "both"))
