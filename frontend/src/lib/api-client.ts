import axios from "axios";

// In production, requests go to a relative path so Vercel's rewrite
// (see vercel.json) routes them to the backend service on the same origin.
// In dev, default to the local FastAPI server unless overridden.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://localhost:8000" : "");

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("[API Error]", error.message);
    return Promise.reject(error);
  }
);
