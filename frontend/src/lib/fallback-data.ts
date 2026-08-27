import type { AgentResult, Stock } from "./api-types";

// Static fallback data used only if the backend is unreachable, so the UI
// still has something reasonable to render.

export const FALLBACK_STOCKS: Stock[] = [
  {
    ticker: "AAPL",
    name: "Apple Inc.",
    sector: "Technology",
    current_price: 190.5,
    change_percent: 1.24,
    last_updated: new Date().toISOString(),
  },
  {
    ticker: "MSFT",
    name: "Microsoft Corporation",
    sector: "Technology",
    current_price: 415.2,
    change_percent: -0.35,
    last_updated: new Date().toISOString(),
  },
  {
    ticker: "GOOGL",
    name: "Alphabet Inc.",
    sector: "Technology",
    current_price: 172.8,
    change_percent: 0.68,
    last_updated: new Date().toISOString(),
  },
];

export const FALLBACK_ANALYSIS: AgentResult = {
  thesis: "No live analysis available. Displaying placeholder data.",
  signal: "NEUTRAL",
  confidence: "LOW",
  summary:
    "The backend could not be reached, so this preview shows placeholder content instead of a generated report.",
  detailed_analysis: {
    trend: "Unavailable",
    momentum: "Unavailable",
    key_levels: "Unavailable",
    volume_context: "Unavailable",
    market_context: "Unavailable",
  },
  key_levels: {
    support: [0, 0],
    resistance: [0, 0],
    stop_loss: 0,
    target: 0,
  },
  evidence_chain: ["No data available."],
  risk_factors: ["No data available."],
  chart_config: {
    ticker: "",
    period: "6M",
    overlays: [],
    annotations: [],
    style: "dark",
    data: [],
  },
  final_commentary: "Connect to the backend to generate a live report.",
};
