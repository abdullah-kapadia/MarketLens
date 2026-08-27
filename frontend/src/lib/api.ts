import { API_BASE_URL, apiClient } from "./api-client";
import type {
  AgentStep,
  HealthResponse,
  ReportDetail,
  ReportListResponse,
  StockListResponse,
  StockSummary,
} from "./api-types";

/**
 * Health Check API
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>("/api/v1/health");
  return response.data;
};

/**
 * Get list of available stocks
 */
export const listStocks = async (): Promise<StockListResponse> => {
  const response = await apiClient.get<StockListResponse>("/api/v1/stocks");
  return response.data;
};

/**
 * Get stock summary data for a specific ticker
 */
export const getStockSummary = async (ticker: string): Promise<StockSummary> => {
  const response = await apiClient.get<StockSummary>(`/api/v1/stocks/${ticker}/summary`);
  return response.data;
};

const SSE_EVENT_TYPES = ["reasoning", "tool_call", "observation", "complete", "error"] as const;

/**
 * Analyze a stock via the SSE analysis stream. Streams AgentStep events to
 * onMessage as they arrive, and reports terminal state via onError/onComplete.
 */
export const analyzeStock = (
  ticker: string,
  onMessage: (step: AgentStep) => void,
  onError: (err: unknown) => void,
  onComplete: () => void
): (() => void) => {
  const url = `${API_BASE_URL}/api/v1/analyze/${encodeURIComponent(ticker)}`;
  const eventSource = new EventSource(url);

  const close = () => {
    eventSource.close();
  };

  // Note: "error" is both a custom SSE event name the backend emits (an
  // AgentStep with type "error", carrying JSON `data`) and the browser's
  // built-in EventSource connection-error event (a plain Event with no
  // `data`) -- both are dispatched to the same "error" listeners, so this
  // handler has to distinguish them instead of assuming `event.data` exists.
  SSE_EVENT_TYPES.forEach((eventType) => {
    eventSource.addEventListener(eventType, (event: Event) => {
      const data = (event as MessageEvent).data;
      if (typeof data !== "string") {
        // A real connection-level failure, not an app-level error step.
        onError(event);
        close();
        onComplete();
        return;
      }

      try {
        const step = JSON.parse(data) as AgentStep;
        onMessage(step);
      } catch (err) {
        onError(err);
        close();
        onComplete();
        return;
      }

      if (eventType === "complete" || eventType === "error") {
        close();
        onComplete();
      }
    });
  });

  return close;
};

/**
 * Get list of reports with optional filters
 */
export const listReports = async (params?: {
  limit?: number;
  ticker?: string;
}): Promise<ReportListResponse> => {
  const response = await apiClient.get<ReportListResponse>("/api/v1/reports", { params });
  return response.data;
};

/**
 * Get detailed report by ID
 */
export const getReportDetail = async (reportId: string): Promise<ReportDetail> => {
  const response = await apiClient.get<ReportDetail>(`/api/v1/reports/${reportId}`);
  return response.data;
};

/**
 * Get PDF report by ID
 */
export const getReportPdf = async (reportId: string): Promise<Blob> => {
  const response = await apiClient.get(`/api/v1/reports/${reportId}/pdf`, {
    responseType: "blob",
  });
  return response.data;
};
