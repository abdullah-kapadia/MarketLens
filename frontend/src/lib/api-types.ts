// API Type Definitions based on OpenAPI schema

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
}

export interface KeyLevels {
  support: number[];
  resistance: number[];
  stop_loss: number;
  target: number;
}

export interface ChartDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_9?: number;
  sma_50?: number;
  sma_200?: number;
  rsi?: number;
  upper_bb?: number;
  lower_bb?: number;
}

export interface ChartConfig {
  ticker: string;
  period: string;
  overlays: string[];
  annotations: string[];
  style: ChartStyle;
  data: ChartDataPoint[];
}

export interface AgentResult {
  thesis: string;
  signal: Signal;
  confidence: Confidence;
  summary: string;
  detailed_analysis: DetailedAnalysis;
  key_levels: KeyLevels;
  evidence_chain: string[];
  risk_factors: string[];
  chart_config: ChartConfig;
  final_commentary: string;
}

export type AgentStepType = "reasoning" | "tool_call" | "observation" | "complete" | "error";

export interface AgentStep {
  type: AgentStepType;
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

export interface ReportDetail {
  id: string;
  ticker: string;
  signal: Signal;
  confidence: Confidence;
  thesis: string;
  generated_at: string;
  tool_calls_count: number;
  execution_time_ms: number;
  analysis: AgentResult;
  reasoning_trace: AgentStep[];
  pdf_url: string;
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

export interface HTTPValidationError {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}
