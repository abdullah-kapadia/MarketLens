from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

import mplfinance as mpf
import pandas as pd
import pandas_ta as ta

from tools.data_tools import load_dataframe
from tools.level_tools import find_support_resistance


def _output_dir() -> Path:
    return Path("output/charts")


def _dark_style() -> mpf.Style:
    mc = mpf.make_marketcolors(
        up="#26a69a",
        down="#ef5350",
        edge={"up": "#26a69a", "down": "#ef5350"},
        wick={"up": "#26a69a", "down": "#ef5350"},
        volume={"up": "#26a69a80", "down": "#ef535080"},
    )
    return mpf.make_mpf_style(
        base_mpl_style="dark_background",
        marketcolors=mc,
        rc={
            "figure.facecolor": "#131722",
            "axes.facecolor": "#131722",
            "axes.edgecolor": "#363A45",
            "axes.labelcolor": "#D1D4DC",
            "xtick.color": "#787B86",
            "ytick.color": "#787B86",
            "grid.color": "#1E222D",
        },
    )


def generate_chart(
    ticker: str,
    period: str = "6M",
    overlays: list[str] | None = None,
    annotations: list[str] | None = None,
    fibonacci: dict | None = None,
    channels: list[dict] | None = None,
    style: str = "dark",
    **kwargs  # Ignore any extra arguments from AI
) -> dict[str, Any]:
    overlays = overlays or []
    annotations = annotations or []

    df = load_dataframe(ticker, period)
    addplots: list[Any] = []
    hlines = []
    vlines = []

    # Process overlays (moving averages, indicators)
    for overlay in overlays:
        upper = overlay.upper()
        if upper.startswith("SMA_"):
            length = int(upper.split("_")[1])
            sma = ta.sma(df["Close"], length=length)
            if sma is not None and not sma.empty:
                addplots.append(mpf.make_addplot(sma, color="#F7A21B", width=1.5))
        elif upper.startswith("EMA_"):
            length = int(upper.split("_")[1])
            ema = ta.ema(df["Close"], length=length)
            if ema is not None and not ema.empty:
                addplots.append(mpf.make_addplot(ema, color="#E040FB", width=1.5))
        elif upper == "BOLLINGER":
            bands = ta.bbands(df["Close"])
            if bands is not None and not bands.empty:
                addplots.append(mpf.make_addplot(bands.iloc[:, 0], color="#78909C", alpha=0.5))
                addplots.append(mpf.make_addplot(bands.iloc[:, 2], color="#78909C", alpha=0.5))
        elif upper == "VWAP":
            vwap = ta.vwap(df["High"], df["Low"], df["Close"], df["Volume"])
            if vwap is not None and not vwap.empty:
                addplots.append(mpf.make_addplot(vwap, color="#FF9800", width=1.5))
        elif upper == "SUPPORT_RESISTANCE":
            levels = find_support_resistance(ticker, "both")
            hlines.extend(levels.get("key_support", []))
            hlines.extend(levels.get("key_resistance", []))
        elif upper == "RSI":
            rsi = ta.rsi(df["Close"], length=14)
            if rsi is not None and not rsi.empty:
                addplots.append(mpf.make_addplot(rsi, panel=1, color="#F7A21B", ylabel="RSI", secondary_y=False))
                # Add overbought/oversold lines
                addplots.append(mpf.make_addplot([70] * len(df), panel=1, color="#ef5350", linestyle="--", width=0.7, alpha=0.5))
                addplots.append(mpf.make_addplot([30] * len(df), panel=1, color="#26a69a", linestyle="--", width=0.7, alpha=0.5))

    # Process Fibonacci retracements
    if fibonacci and isinstance(fibonacci, dict):
        swing_low = fibonacci.get("swing_low")
        swing_high = fibonacci.get("swing_high")
        if swing_low and swing_high and swing_low < swing_high:
            diff = swing_high - swing_low
            fib_levels = {
                "0.0%": swing_high,
                "23.6%": swing_high - (diff * 0.236),
                "38.2%": swing_high - (diff * 0.382),
                "50.0%": swing_high - (diff * 0.5),
                "61.8%": swing_high - (diff * 0.618),
                "100.0%": swing_low,
            }
            for level_name, level_value in fib_levels.items():
                hlines.append(level_value)
                # Note: mplfinance doesn't support line labels easily, so we just draw the lines

    # Process channels
    if channels and isinstance(channels, list):
        for channel in channels:
            if isinstance(channel, dict):
                channel_type = channel.get("type", "")
                lower = channel.get("lower")
                upper = channel.get("upper")
                if lower and upper:
                    # Draw channel boundaries as horizontal lines
                    # For a proper channel, we'd need matplotlib axes access (future enhancement)
                    hlines.extend([lower, upper])

    # Process annotations
    if "current_price" in annotations:
        hlines.append(float(df["Close"].iloc[-1]))

    # Prepare output directory
    output_dir = _output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{ticker}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
    chart_path = output_dir / filename

    mpf_style = _dark_style() if style == "dark" else "classic"
    
    # Build plot kwargs dynamically
    plot_kwargs = {
        "type": "candle",
        "style": mpf_style,
        "volume": True,
        "returnfig": True,
        "figsize": (14, 10),
        "title": f"{ticker} Technical Analysis",
    }
    
    # Only add these if they have content
    if addplots:
        plot_kwargs["addplot"] = addplots
    if hlines:
        # Deduplicate hlines
        hlines_unique = list(set([round(h, 2) for h in hlines if h]))
        plot_kwargs["hlines"] = dict(
            hlines=hlines_unique,
            colors=["#FFD700"] * len(hlines_unique),  # Gold color for all lines
            linestyle="--",
            linewidths=0.8,
            alpha=0.6
        )
    
    try:
        fig, axes = mpf.plot(df, **plot_kwargs)
        
        # Add Fibonacci level labels using matplotlib if we have them
        if fibonacci and isinstance(fibonacci, dict) and len(axes) > 0:
            ax = axes[0]  # Main price axis
            swing_low = fibonacci.get("swing_low")
            swing_high = fibonacci.get("swing_high")
            if swing_low and swing_high and swing_low < swing_high:
                diff = swing_high - swing_low
                fib_levels = [
                    ("0.0%", swing_high),
                    ("23.6%", swing_high - (diff * 0.236)),
                    ("38.2%", swing_high - (diff * 0.382)),
                    ("50.0%", swing_high - (diff * 0.5)),
                    ("61.8%", swing_high - (diff * 0.618)),
                    ("100%", swing_low),
                ]
                for label, level in fib_levels:
                    ax.text(
                        len(df) - 1, level, f"  Fib {label}",
                        verticalalignment='center',
                        color='#FFD700',
                        fontsize=8,
                        alpha=0.8
                    )
        
        fig.savefig(chart_path, bbox_inches="tight", dpi=150)
        chart_base64 = base64.b64encode(chart_path.read_bytes()).decode("utf-8")
        
        return {
            "chart_base64": chart_base64,
            "chart_path": str(chart_path),
            "dimensions": {"width": 1400, "height": 1000},
            "dpi": 150,
            "overlays_applied": overlays,
            "annotations_applied": annotations,
        }
    except Exception as e:
        print(f"[ERROR] Chart generation failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "chart_base64": "",
            "chart_path": "",
            "dimensions": {"width": 0, "height": 0},
        }


if __name__ == "__main__":
    print(generate_chart("OGDC", "6M", ["SMA_50", "support_resistance"], ["current_price"]))
