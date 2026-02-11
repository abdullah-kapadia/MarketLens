from __future__ import annotations

from typing import Any

import numpy as np

from tools.data_tools import load_config, load_dataframe


def _return_percent(df) -> float:
    start = float(df["Close"].iloc[0])
    end = float(df["Close"].iloc[-1])
    return ((end - start) / start) * 100 if start else 0.0


def compare_with_index(ticker: str, period: str = "3M") -> dict[str, Any]:
    stock_df = load_dataframe(ticker, period)
    index_df = load_dataframe("KSE100", period)

    stock_return = _return_percent(stock_df)
    index_return = _return_percent(index_df)
    relative = stock_return - index_return

    stock_returns = stock_df["Close"].pct_change().dropna()
    index_returns = index_df["Close"].pct_change().dropna()
    min_len = min(len(stock_returns), len(index_returns))
    stock_returns = stock_returns[-min_len:]
    index_returns = index_returns[-min_len:]

    correlation = float(stock_returns.corr(index_returns)) if min_len > 1 else 0.0
    beta = float(correlation * (stock_returns.std() / index_returns.std())) if index_returns.std() else 0.0

    summary = (
        f"{ticker} {'outperformed' if relative >= 0 else 'underperformed'} "
        f"KSE-100 by {abs(relative):.1f}% over {period}. "
        f"Correlation {correlation:.2f}."
    )

    return {
        "ticker": ticker,
        "index": "KSE-100",
        "period": period,
        "stock_return": round(stock_return, 2),
        "index_return": round(index_return, 2),
        "relative_performance": round(relative, 2),
        "correlation": round(correlation, 2),
        "beta": round(beta, 2),
        "summary": summary,
    }


def compare_with_sector(ticker: str) -> dict[str, Any]:
    config = load_config()
    stock_meta = config["stocks"].get(ticker)
    if not stock_meta:
        raise ValueError(f"Ticker not found in config: {ticker}")

    sector = stock_meta["sector"]
    peers = list({*stock_meta.get("peers", []), ticker})

    rankings = []
    for peer in peers:
        try:
            df = load_dataframe(peer, "1M")
            ret = _return_percent(df)
            rankings.append({"ticker": peer, "return": round(ret, 2)})
        except Exception:
            continue

    rankings = sorted(rankings, key=lambda r: r["return"], reverse=True)
    for idx, row in enumerate(rankings, start=1):
        row["rank"] = idx

    sector_avg = float(np.mean([r["return"] for r in rankings])) if rankings else 0.0
    stock_row = next((r for r in rankings if r["ticker"] == ticker), None)
    stock_return = stock_row["return"] if stock_row else 0.0
    relative = stock_return - sector_avg

    summary = (
        f"{ticker} ranks {stock_row['rank'] if stock_row else 'N/A'} in {sector} peers "
        f"with {stock_return:.1f}% return vs sector avg {sector_avg:.1f}%."
    )

    return {
        "ticker": ticker,
        "sector": sector,
        "period": "1M",
        "rankings": rankings,
        "sector_avg_return": round(sector_avg, 2),
        "relative_to_sector": round(relative, 2),
        "summary": summary,
    }


if __name__ == "__main__":
    print(compare_with_index("OGDC", "3M"))
    print(compare_with_sector("OGDC"))
