import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

export function getTransactions(page = 1, pageSize = 50) {
  return client.get("/transactions/", { params: { page, page_size: pageSize } });
}

export function getTransaction(id) {
  return client.get(`/transactions/${id}`);
}

export function getFlaggedTransactions(page = 1, pageSize = 50) {
  return client.get("/transactions/flagged/list", { params: { page, page_size: pageSize } });
}

export function getStats() {
  return client.get("/transactions/stats/summary");
}

export function analyzeTransaction(txn) {
  return client.post("/predictions/analyze", txn);
}

export function reviewTransaction(id, reviewer, action) {
  return client.post(`/transactions/${id}/review?reviewer=${reviewer}&action=${action}`);
}

export function getWebSocketUrl() {
  const wsBase = API_BASE.replace(/^http/, "ws");
  return `${wsBase}/ws/transactions`;
}

export default client;
