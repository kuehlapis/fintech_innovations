// client/src/lib/storage.ts
export interface GuestHolding {
  ticker: string;
  quantity: number;
}

const USER_ID_KEY = "onewealth_user_id";
const ACCESS_TOKEN_KEY = "onewealth_access_token";
const REFRESH_TOKEN_KEY = "onewealth_refresh_token";
const GUEST_HOLDINGS_KEY = "onewealth_guest_holdings";

export function getStoredUserId(): string {
  return localStorage.getItem(USER_ID_KEY) ?? "";
}

export function setStoredUserId(userId: string): void {
  localStorage.setItem(USER_ID_KEY, userId);
}

export function clearStoredUserId(): void {
  localStorage.removeItem(USER_ID_KEY);
}

export function getAccessToken(): string {
  return localStorage.getItem(ACCESS_TOKEN_KEY) ?? "";
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function getRefreshToken(): string {
  return localStorage.getItem(REFRESH_TOKEN_KEY) ?? "";
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearAuthStorage(): void {
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getStoredGuestHoldings(): GuestHolding[] {
  try {
    const raw = localStorage.getItem(GUEST_HOLDINGS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as GuestHolding[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function addStoredGuestHolding(ticker: string, quantity: number): void {
  const next = [...getStoredGuestHoldings(), { ticker, quantity }];
  localStorage.setItem(GUEST_HOLDINGS_KEY, JSON.stringify(next));
}