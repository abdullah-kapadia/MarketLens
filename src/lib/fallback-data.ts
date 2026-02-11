import type { StockListResponse, ReportDetail, AgentResult } from './api-types';

/**
 * Fallback data for when API calls fail
 */

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
  },
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
