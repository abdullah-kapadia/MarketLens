from __future__ import annotations

from typing import Any

import pandas as pd

from tools.data_tools import load_dataframe


def analyze_volume(ticker: str, period: str = "1M") -> dict[str, Any]:
    df = load_dataframe(ticker, period)
    df = df.copy()
    df["return"] = df["Close"].pct_change() * 100

    avg_volume_20d = float(df["Volume"].tail(20).mean())
    recent_volume = float(df["Volume"].iloc[-1])
    volume_ratio = recent_volume / avg_volume_20d if avg_volume_20d else 0.0

    recent_avg = float(df["Volume"].tail(10).mean())
    prior_avg = float(df["Volume"].tail(20).head(10).mean()) if len(df) >= 20 else recent_avg
    if recent_avg > prior_avg * 1.05:
        volume_trend = "increasing"
    elif recent_avg < prior_avg * 0.95:
        volume_trend = "decreasing"
    else:
        volume_trend = "flat"

    up_days = df[df["return"] > 0]["Volume"]
    down_days = df[df["return"] < 0]["Volume"]
    up_avg = float(up_days.mean()) if not up_days.empty else 0.0
    down_avg = float(down_days.mean()) if not down_days.empty else 0.0
    volume_price_divergence = down_avg > up_avg * 1.2 if up_avg else False

    unusual = df[df["Volume"] > avg_volume_20d * 1.5]
    unusual_days = [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "volume": int(row["Volume"]),
            "ratio": round(row["Volume"] / avg_volume_20d, 2) if avg_volume_20d else 0,
            "price_change": round(row["return"], 2) if pd.notna(row["return"]) else 0,
        }
        for idx, row in unusual.iterrows()
    ]

    summary = (
        f"Volume {volume_trend} with {volume_ratio:.2f}x recent/avg. "
        f"Down-day volume {'exceeds' if volume_price_divergence else 'does not exceed'} up-day volume."
    )

    return {
        "ticker": ticker,
        "period": period,
        "avg_volume_20d": int(avg_volume_20d),
        "recent_volume": int(recent_volume),
        "volume_ratio": round(volume_ratio, 2),
        "volume_trend": volume_trend,
        "up_day_avg_volume": int(up_avg),
        "down_day_avg_volume": int(down_avg),
        "volume_price_divergence": volume_price_divergence,
        "unusual_volume_days": unusual_days,
        "summary": summary,
    }


if __name__ == "__main__":
    print(analyze_volume("OGDC", "1M"))
