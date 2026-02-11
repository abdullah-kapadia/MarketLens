
# MarketLens API Documentation

This document provides detailed information about the MarketLens backend API.

## Base URL

All API endpoints are prefixed with `/api/v1`.

---

## Endpoints

### 1. Analyze Stock

- **Method:** `POST`
- **Path:** `/analyze/{ticker}`
- **Description:** Initiates a real-time analysis for a given stock ticker. The analysis is streamed back to the client using Server-Sent Events (SSE).

#### Path Parameters

- `ticker` (string, required): The stock ticker symbol (e.g., "AAPL").

#### Responses

- **`200 OK`**: The analysis stream is successfully initiated. The response body will be an SSE stream.
    - **Event:** `reasoning` - Provides insight into the agent's thought process.
    - **Event:** `tool_call` - Indicates which tool the agent is using.
    - **Event:** `observation` - The result from the tool call.
    - **Event:** `complete` - The final analysis report.
    - **Event:** `error` - If an error occurs during analysis.
- **`404 Not Found`**: The requested ticker was not found.
- **`422 Unprocessable Entity`**: Validation error.

---

### 2. List Reports

- **Method:** `GET`
- **Path:** `/reports`
- **Description:** Retrieves a list of previously generated analysis reports.

#### Query Parameters

- `limit` (integer, optional, default: 10, max: 50): The maximum number of reports to return.
- `ticker` (string, optional): Filter reports by a specific stock ticker.

#### Responses

- **`200 OK`**: A list of reports was successfully retrieved.
  ```json
  {
    "reports": [
      {
        "id": "report_123",
        "ticker": "AAPL",
        "signal": "BULLISH",
        "confidence": "HIGH",
        "thesis": "Positive earnings report and strong market sentiment.",
        "generated_at": "2024-07-30T10:00:00Z",
        "tool_calls_count": 5,
        "execution_time_ms": 15000
      }
    ],
    "total": 1
  }
  ```
- **`422 Unprocessable Entity`**: Validation error.

---

### 3. Get Report Detail

- **Method:** `GET`
- **Path:** `/reports/{report_id}`
- **Description:** Retrieves the detailed analysis for a specific report.

#### Path Parameters

- `report_id` (string, required): The unique identifier of the report.

#### Responses

- **`200 OK`**: The report detail was successfully retrieved.
  ```json
  {
    "id": "report_123",
    "ticker": "AAPL",
    "signal": "BULLISH",
    "confidence": "HIGH",
    "thesis": "Positive earnings report and strong market sentiment.",
    "generated_at": "2024-07-30T10:00:00Z",
    "tool_calls_count": 5,
    "execution_time_ms": 15000,
    "analysis": {
      "thesis": "...",
      "signal": "BULLISH",
      "confidence": "HIGH",
      "summary": "...",
      "detailed_analysis": {
        "trend": "...",
        "momentum": "...",
        "key_levels": "...",
        "volume_context": "...",
        "market_context": "..."
      },
      "key_levels": {
        "support": [180.50],
        "resistance": [190.00],
        "stop_loss": 178.00,
        "target": 195.00
      },
      "evidence_chain": ["..."],
      "risk_factors": ["..."],
      "chart_config": {
        "ticker": "AAPL",
        "period": "6M",
        "overlays": ["sma_50"],
        "annotations": ["earnings_call"],
        "style": "dark"
      }
    },
    "reasoning_trace": [],
    "pdf_url": "/api/v1/reports/report_123/pdf"
  }
  ```
- **`404 Not Found`**: The requested report was not found.
- **`422 Unprocessable Entity`**: Validation error.

---

### 4. Get Report PDF

- **Method:** `GET`
- **Path:** `/reports/{report_id}/pdf`
- **Description:** Retrieves the PDF version of a specific analysis report.

#### Path Parameters

- `report_id` (string, required): The unique identifier of the report.

#### Responses

- **`200 OK`**: The PDF file is returned.
- **`404 Not Found`**: The requested report was not found.

---

### 5. List Stocks

- **Method:** `GET`
- **Path:** `/stocks`
- **Description:** Retrieves a list of all available stocks for analysis.

#### Responses

- **`200 OK`**: A list of available stocks was successfully retrieved.
  ```json
  {
    "stocks": [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "current_price": 185.50,
        "change_percent": 1.25,
        "last_updated": "2024-07-30T16:00:00Z"
      }
    ]
  }
  ```

---

### 6. Get Stock Summary

- **Method:** `GET`
- **Path:** `/stocks/{ticker}/summary`
- **Description:** Retrieves a summary of key data points for a specific stock.

#### Path Parameters

- `ticker` (string, required): The stock ticker symbol.

#### Responses

- **`200 OK`**: The stock summary was successfully retrieved.
  ```json
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "current_price": 185.50,
    "change_percent": 1.25,
    "period_high": 195.00,
    "period_low": 175.00,
    "avg_volume": 50000000,
    "last_5_days": [
        {"date": "2024-07-26", "close": 184.00},
        {"date": "2024-07-29", "close": 185.00},
        {"date": "2024-07-30", "close": 185.50}
    ],
    "indicators_snapshot": {}
  }
  ```
- **`404 Not Found`**: The requested ticker was not found.
- **`422 Unprocessable Entity`**: Validation error.

---

### 7. Health Check

- **Method:** `GET`
- **Path:** `/health`
- **Description:** Provides the health status of the backend service.

#### Responses

- **`200 OK`**: The service is healthy.
  ```json
  {
    "status": "ok",
    "llm_provider": "claude-sonnet-4-20250514",
    "llm_fallback": "gpt-4o",
    "stocks_available": 10,
    "version": "1.0.0"
  }
  ```
