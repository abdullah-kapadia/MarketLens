// API Type Definitions matching the MarketLens backend (backend/models.py)

export type Signal = "BULLISH" | "BEARISH" | "NEUTRAL";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";
export type ChartStyle = "dark" | "light";

export interface Stock {
  ticker: string;
  name: string;
  sector: string;
  current_price: number;
  change_percent: number;
  last_updated: string;
}

export interface StockListResponse {
  stocks: Stock[];
}

export interface StockSummary {
  ticker: string;
  name: string;
  sector: string;
  current_price: number;
  change_percent: number;
  period_high: number;
  period_low: number;
  avg_volume: number;
  last_5_days: Record<string, any>[];
  indicators_snapshot: Record<string, any>;
}

export interface DetailedAnalysis {
  trend: string;
  momentum: string;
  key_levels: string;
  volume_context: string;
  market_context: string;
  price_structure?: string | null;
  market_relative?: string | null;
}

export interface KeyLevels {
  support: number[];
  resistance: number[];
  stop_loss: number;
  target: number;
  immediate_support?: number[] | null;
  secondary_support?: number[] | null;
  immediate_resistance?: number[] | null;
  targets?: number[] | null;
}

export interface TradingStrategy {
  bias: string;
  entry_zones?: string[] | null;
  profit_taking?: string | null;
  invalidation?: string | null;
}

export interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_9?: number | null;
  sma_50?: number | null;
  sma_200?: number | null;
  rsi?: number | null;
  upper_bb?: number | null;
  lower_bb?: number | null;
}

export interface ChartConfig {
  ticker: string;
  period: string;
  overlays: string[];
  annotations: string[];
  fibonacci?: Record<string, any> | null;
  channels?: Record<string, any>[] | null;
  style: ChartStyle;
  data: ChartDataPoint[];
}

export interface AgentResult {
  thesis: string;
  signal: Signal;
  confidence: Confidence;
  current_price?: number | null;
  summary: string;
  detailed_analysis: DetailedAnalysis;
  key_levels: KeyLevels;
  strategy?: TradingStrategy | null;
  evidence_chain: string[];
  risk_factors: string[];
  chart_config: ChartConfig;
  final_commentary: string;
  generated_at?: string | null;
}

export interface AgentStep {
  type: "reasoning" | "tool_call" | "observation" | "complete" | "error";
  content?: string | null;
  tool_name?: string | null;
  tool_input?: Record<string, any> | null;
  iteration: number;
  timestamp: string;
  report_id?: string | null;
  analysis?: AgentResult | null;
  execution_time_ms?: number | null;
  tool_calls_count?: number | null;
  code?: string | null;
  result?: any;
}

export interface ReportSummary {
  id: string;
  ticker: string;
  signal: Signal;
  confidence: Confidence;
  thesis: string;
  generated_at: string;
  tool_calls_count: number;
  execution_time_ms: number;
}

export interface ReportDetail extends ReportSummary {
  analysis: AgentResult;
  reasoning_trace: AgentStep[];
  pdf_url?: string | null;
}

export interface ReportListResponse {
  reports: ReportSummary[];
  total: number;
}

export interface HealthResponse {
  status: string;
  llm_provider: string;
  llm_fallback: string;
  stocks_available: number;
  version: string;
}

export interface ErrorDetail {
  code: string;
  message: string;
  available_tickers?: string[] | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}
