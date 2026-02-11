import type { StockListResponse, ReportDetail, AgentResult, ChartDataPoint } from './api-types';

/**
 * Fallback data for when API calls fail
 */

// Generate sample OHLCV data for the last 6 months
function generateChartData(): ChartDataPoint[] {
  const data: ChartDataPoint[] = [];
  const basePrice = 180;
  const startDate = new Date();
  startDate.setMonth(startDate.getMonth() - 6);
  
  let currentPrice = basePrice;
  
  for (let i = 0; i < 120; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    
    // Simulate price movement with trend and volatility
    const trend = Math.sin(i / 20) * 5;
    const volatility = (Math.random() - 0.5) * 3;
    const change = trend + volatility;
    
    currentPrice += change;
    
    const open = currentPrice;
    const close = currentPrice + (Math.random() - 0.5) * 4;
    const high = Math.max(open, close) + Math.random() * 2;
    const low = Math.min(open, close) - Math.random() * 2;
    const volume = Math.floor(40000000 + Math.random() * 20000000);
    
    // Calculate moving averages
    const sma_9 = data.length >= 8
      ? data.slice(-8).reduce((sum, d) => sum + d.close, 0) / 9 + close / 9
      : undefined;
    const sma_50 = data.length >= 49
      ? data.slice(-49).reduce((sum, d) => sum + d.close, 0) / 50 + close / 50
      : i > 49 ? currentPrice - 5 : undefined;
    const sma_200 = i > 100 ? currentPrice - 15 : undefined;
    
    // Calculate RSI (simplified)
    const rsi = 30 + Math.random() * 40; // Random RSI between 30-70
    
    // Bollinger Bands (simplified)
    const bb_width = 8;
    const upper_bb = sma_9 ? sma_9 + bb_width : undefined;
    const lower_bb = sma_9 ? sma_9 - bb_width : undefined;
    
    data.push({
      date: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume,
      sma_9: sma_9 ? parseFloat(sma_9.toFixed(2)) : undefined,
      sma_50: sma_50 ? parseFloat(sma_50.toFixed(2)) : undefined,
      sma_200: sma_200 ? parseFloat(sma_200.toFixed(2)) : undefined,
      rsi: parseFloat(rsi.toFixed(1)),
      upper_bb: upper_bb ? parseFloat(upper_bb.toFixed(2)) : undefined,
      lower_bb: lower_bb ? parseFloat(lower_bb.toFixed(2)) : undefined,
    });
  }
  
  return data;
}

export const FALLBACK_STOCKS: StockListResponse = {
  stocks: [
    {
      ticker: "AAPL",
      name: "Apple Inc.",
      sector: "Technology",
      current_price: 189.84,
      change_percent: 1.23,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "MSFT",
      name: "Microsoft Corp.",
      sector: "Technology",
      current_price: 378.91,
      change_percent: 0.87,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "GOOGL",
      name: "Alphabet Inc.",
      sector: "Technology",
      current_price: 141.80,
      change_percent: -0.34,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "AMZN",
      name: "Amazon.com Inc.",
      sector: "Consumer Cyclical",
      current_price: 178.25,
      change_percent: 2.10,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "NVDA",
      name: "NVIDIA Corp.",
      sector: "Technology",
      current_price: 875.28,
      change_percent: 3.45,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "TSLA",
      name: "Tesla Inc.",
      sector: "Consumer Cyclical",
      current_price: 248.42,
      change_percent: -1.67,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "JPM",
      name: "JPMorgan Chase",
      sector: "Financial Services",
      current_price: 196.14,
      change_percent: 0.52,
      last_updated: new Date().toISOString(),
    },
    {
      ticker: "META",
      name: "Meta Platforms",
      sector: "Technology",
      current_price: 505.75,
      change_percent: 1.89,
      last_updated: new Date().toISOString(),
    },
  ],
};

export const FALLBACK_ANALYSIS: AgentResult = {
  thesis: "The technical outlook indicates a consolidation phase with potential for bullish breakout",
  signal: "BULLISH",
  confidence: "MEDIUM",
  summary: "The technical outlook for this stock indicates a consolidation phase following recent momentum shifts. Key indicators suggest a potential breakout scenario, with RSI approaching oversold territory and MACD showing early signs of bullish divergence.",
  detailed_analysis: {
    trend: "Consolidating after recent uptrend with higher lows forming",
    momentum: "RSI showing bullish divergence, MACD crossing above signal line",
    key_levels: "Support at $180, resistance at $195",
    volume_context: "institutional accumulation patterns observed",
    market_context: "Broader market showing strength in technology sector",
  },
  key_levels: {
    support: [180.50, 175.20],
    resistance: [195.80, 202.50],
    stop_loss: 172.00,
    target: 205.00,
  },
  evidence_chain: [
    "Price holding above 50-day moving average",
    "Volume increasing on up days",
    "RSI forming higher lows while price forms lower lows",
    "MACD histogram expanding positively",
    "Price respecting key support levels",
  ],
  risk_factors: [
    "Broader market volatility increasing",
    "Sector rotation concerns",
    "Upcoming earnings announcement uncertainty",
    "Elevated valuation metrics compared to peers",
  ],
  chart_config: {
    ticker: "AAPL",
    period: "6M",
    overlays: ["SMA(50)", "SMA(200)", "BB(20)"],
    annotations: ["Support", "Resistance"],
    style: "dark",
    data: generateChartData(),
  },
  final_commentary: "The stock has demonstrated a follow-through pattern after last week's consolidation near the upper boundary of an ascending triangle formation, reinforcing signs of continued momentum within the broader uptrend. Price action remains constructive above the rising 9-week simple moving average, maintaining the primary bullish structure, though momentum indicators are beginning to show signs of short-term exhaustion with the weekly RSI holding near overbought territory at 68. This keeps the near-term bias cautiously optimistic as long as the index trades above the triangle support zone. Immediate resistance is clearly defined at the $195.00-$198.00 zone, representing the recent swing highs and the measured move target from the triangle pattern, while critical support lies at $180.50-$175.20 around the triangle base, 50-day moving average, and the key psychological $175 level. A decisive break and close below the $175 support zone on elevated volume may trigger a deeper retracement toward the $172.00-$168.00 area, potentially filling the gap from the previous breakout, while only a sustained move above $198.00 with strong participation would negate the consolidation risk and open the path toward the $205.00 measured target. Current strategy favors reducing partial exposure into strength near resistance levels and maintaining a disciplined approach of waiting for pullbacks toward the $180-$182 support zone for selective re-entry opportunities, with stop losses placed strategically below $172.00 to manage downside risk. Volume patterns suggest institutional accumulation during the consolidation phase, with above-average volume on up days and lighter volume on pullbacks, indicating underlying strength. The broader market context remains supportive with the technology sector showing relative strength, though investors should remain vigilant of potential sector rotation and increasing volatility as we approach key economic data releases. Risk management is paramount in the current environment given elevated valuations and the potential for sudden sentiment shifts."
};

export const FALLBACK_REPORT: ReportDetail = {
  id: "fallback-report-001",
  ticker: "AAPL",
  signal: "BULLISH",
  confidence: "MEDIUM",
  thesis: "The technical outlook indicates a consolidation phase with potential for bullish breakout",
  generated_at: new Date().toISOString(),
  tool_calls_count: 14,
  execution_time_ms: 8400,
  analysis: FALLBACK_ANALYSIS,
  reasoning_trace: [],
  pdf_url: "#",
};
