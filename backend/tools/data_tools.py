from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

PERIOD_DAYS = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}


def _data_dir() -> Path:
    return Path(os.getenv("DATA_DIR", "data"))


def _fallback_data_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir.parent / "data"


def _config_path() -> Path:
    primary = _data_dir() / "config.json"
    if primary.exists():
        return primary
    fallback = _fallback_data_dir() / "config.json"
    return fallback


def load_config() -> dict[str, Any]:
    config_path = _config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def load_dataframe(ticker: str, period: str = "6M") -> pd.DataFrame:
    csv_path = _data_dir() / f"{ticker}.csv"
    if not csv_path.exists():
        fallback_path = _fallback_data_dir() / f"{ticker}.csv"
        if fallback_path.exists():
            csv_path = fallback_path
        else:
            raise FileNotFoundError(f"Data file not found: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date")
    df = df.set_index("Date")

    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV missing required columns. Found: {df.columns.tolist()}")

    period_days = PERIOD_DAYS.get(period, 180)
    data_end = df.index.max()
    cutoff = data_end - pd.Timedelta(days=period_days)
    df = df[df.index >= cutoff]

    if df.empty:
        raise ValueError(f"No data for {ticker} in period {period}")

    return df


def load_stock_data(ticker: str, period: str = "6M") -> dict[str, Any]:
    df = load_dataframe(ticker, period)
    current_price = float(df["Close"].iloc[-1])
    start_price = float(df["Close"].iloc[0])
    price_change = current_price - start_price
    change_percent = (price_change / start_price) * 100 if start_price else 0.0

    period_high = float(df["High"].max())
    period_low = float(df["Low"].min())
    avg_volume = int(df["Volume"].mean())

    last_5 = df.tail(5).reset_index()
    last_5_days = [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        }
        for _, row in last_5.iterrows()
    ]

    summary = (
        f"{ticker}: Current PKR {current_price:.2f}, "
        f"{'up' if price_change >= 0 else 'down'} {abs(change_percent):.1f}% over {period}. "
        f"Range: {period_low:.0f}-{period_high:.0f}. "
        f"Avg volume: {avg_volume / 1_000_000:.1f}M shares/day."
    )

    return {
        "ticker": ticker,
        "period": period,
        "current_price": round(current_price, 2),
        "price_change": round(price_change, 2),
        "change_percent": round(change_percent, 2),
        "period_high": round(period_high, 2),
        "period_low": round(period_low, 2),
        "avg_volume": avg_volume,
        "data_points": int(len(df)),
        "last_5_days": last_5_days,
        "summary": summary,
    }


def generate_chart_data(ticker: str, period: str = "6M") -> list[dict]:
    """Generate chart data with OHLCV and technical indicators for frontend."""
    try:
        import pandas_ta as ta
        
        df = load_dataframe(ticker, period)
        
        # Calculate indicators
        df['sma_9'] = ta.sma(df['Close'], length=9)
        df['sma_50'] = ta.sma(df['Close'], length=50)
        df['sma_200'] = ta.sma(df['Close'], length=200)
        df['rsi'] = ta.rsi(df['Close'], length=14)
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        if bb is not None and not bb.empty:
            # Find the correct column names (they may vary by pandas_ta version)
            upper_col = [col for col in bb.columns if 'BBU' in col]
            lower_col = [col for col in bb.columns if 'BBL' in col]
            if upper_col:
                df['upper_bb'] = bb[upper_col[0]]
            if lower_col:
                df['lower_bb'] = bb[lower_col[0]]
        
        # Convert to list of dicts for frontend
        chart_data = []
        for date, row in df.iterrows():
            data_point = {
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']),
            }
            
            # Add indicators (only if not NaN)
            for indicator in ['sma_9', 'sma_50', 'sma_200', 'rsi', 'upper_bb', 'lower_bb']:
                if indicator in row and pd.notna(row[indicator]):
                    data_point[indicator] = round(float(row[indicator]), 2)
            
            chart_data.append(data_point)
        
        return chart_data
    except Exception as e:
        print(f"[ERROR] Failed to generate chart data: {e}")
        return []


if __name__ == "__main__":
    print(load_stock_data("OGDC", "6M"))
