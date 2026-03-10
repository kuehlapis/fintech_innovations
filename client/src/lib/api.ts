// client/src/lib/api.ts
import { clearAuthStorage, getAccessToken } from "@/lib/storage";
import type { FinalAgentDecision, IngestionRequestPayload } from "@/lib/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(init?.headers ?? {});
  if (!headers.has("Content-Type") && init?.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(url, { ...init, headers });

  if (res.status === 401) {
    clearAuthStorage();
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) return (await res.json()) as T;
  return {} as T;
}

export function signup(email: string, password: string) {
  return request<{ user_id: string; portfolio_id: string }>(`${API_BASE_URL}/api/auth/signup`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function login(email: string, password: string) {
  return request<{ user_id: string; access_token: string; refresh_token: string; token_type: string }>(
    `${API_BASE_URL}/api/auth/login`,
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );
}

export function getDashboard(userId: string) {
  return request(`${API_BASE_URL}/api/dashboard/${userId}`);
}

export function getPortfolio(userId: string) {
  return request<{ portfolio: { id: string }; assets: unknown[] }>(`${API_BASE_URL}/api/portfolio/${userId}`);
}

export function addAsset(payload: {
  user_id: string;
  asset_type: string;
  asset_name: string;
  ticker?: string;
  sector?: string;
  quantity?: number;
  value?: number;
  country?: string;
  city?: string;
  property_type?: string;
  metadata?: Record<string, unknown>;
}) {
  return request(`${API_BASE_URL}/api/portfolio/assets`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAsset(assetId: string, payload: Record<string, unknown>) {
  return request(`${API_BASE_URL}/api/portfolio/assets/${assetId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteAsset(assetId: string) {
  return request(`${API_BASE_URL}/api/portfolio/assets/${assetId}`, { method: "DELETE" });
}

export function createAccount(payload: {
  user_id: string;
  account_type: "bank" | "credit_card";
  institution_name?: string;
  account_name: string;
  currency?: string;
}) {
  return request<{ account: { id: string; account_name: string } }>(`${API_BASE_URL}/api/transactions/accounts`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getAccounts(userId: string) {
  return request<{ accounts: Array<{ id: string; account_name: string }> }>(
    `${API_BASE_URL}/api/transactions/accounts/${userId}`
  );
}

export function createTransaction(payload: {
  account_id: string;
  transaction_date: string;
  transaction_type: "income" | "expense" | "transfer";
  category?: string;
  description?: string;
  amount: number;
}) {
  return request(`${API_BASE_URL}/api/transactions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateTransaction(transactionId: string, payload: Record<string, unknown>) {
  return request(`${API_BASE_URL}/api/transactions/${transactionId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteTransaction(transactionId: string) {
  return request(`${API_BASE_URL}/api/transactions/${transactionId}`, { method: "DELETE" });
}

export function runAnalysis(userId: string, query = "") {
  return request<{ run_id: string; status: string; result: FinalAgentDecision }>(
    `${API_BASE_URL}/api/analyse/run/${userId}?query=${encodeURIComponent(query)}`,
    { method: "POST" }
  );
}

export function getAnalysisHistory(userId: string) {
  return request<{ runs: unknown[] }>(`${API_BASE_URL}/api/analyse/history/${userId}`);
}

export function getLatestAnalysis(userId: string) {
  return request<{ latest: unknown }>(`${API_BASE_URL}/api/analyse/latest/${userId}`);
}

export async function analyzePortfolio(payload: IngestionRequestPayload): Promise<FinalAgentDecision> {
  const uid = payload.user_id ?? "";
  const response = await runAnalysis(uid, payload.raw_text ?? "");
  return response.result;
}

/* Keep old holdings page working */
export function addHolding(userId: string, ticker: string, quantity: number) {
  return addAsset({
    user_id: userId,
    asset_type: "equity",
    asset_name: ticker,
    ticker,
    quantity,
  });
}