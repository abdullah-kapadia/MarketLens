import { apiClient } from './api-client';
import type {
  StockListResponse,
  StockSummary,
  ReportListResponse,
  ReportDetail,
  HealthResponse,
} from './api-types';

/**
 * Health Check API
 */
export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/api/v1/health');
  return response.data;
};

/**
 * Get list of available stocks
 */
export const listStocks = async (): Promise<StockListResponse> => {
  const response = await apiClient.get<StockListResponse>('/api/v1/stocks');
  return response.data;
};

/**
 * Get stock summary data for a specific ticker
 */
export const getStockSummary = async (ticker: string): Promise<StockSummary> => {
  const response = await apiClient.get<StockSummary>(`/api/v1/stocks/${ticker}/summary`);
  return response.data;
};

/**
 * Analyze a stock and generate report
 */
export const analyzeStock = async (ticker: string): Promise<any> => {
  const response = await apiClient.post(`/api/v1/analyze/${ticker}`);
  return response.data;
};

/**
 * Get list of reports with optional filters
 */
export const listReports = async (params?: {
  limit?: number;
  ticker?: string;
}): Promise<ReportListResponse> => {
  const response = await apiClient.get<ReportListResponse>('/api/v1/reports', { params });
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
    responseType: 'blob',
  });
  return response.data;
};
