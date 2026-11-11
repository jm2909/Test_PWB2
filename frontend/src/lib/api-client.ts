import { ApiError } from '../types/api';
import type { Page } from '../types/api';
import type { ConsentRecord, ConsentRequest } from '../types/consent';
import type {
  ConnectionItem,
  ConnectionResult,
  ScaleConnectRequest,
  WearableAuthorization,
  WearableCallback,
  WearableProvider,
} from '../types/connection';
import type { DataRightsRequest, DataRightsRequestCreate } from '../types/dataRights';
import type { WellnessAlert } from '../types/alert';
import type { DashboardData } from '../types/dashboard';
import type { SupportRequestCreate, SupportRequestReceipt } from '../types/support';
import type { Goal, GoalCreateRequest } from '../types/goal';
import type { Insight, InsightFeedback } from '../types/insight';
import type { TrendRange, TrendResponse } from '../types/trend';

/** The single API base. Call paths are relative to it and start with /v1/<domain>. */
const API_BASE = import.meta.env.VITE_API_URL ?? '/api';

export const SESSION_EXPIRED_EVENT = 'fitconnect:session-expired';
const TOKEN_KEY = 'fitconnect.token';

export function getStoredToken(): string | null {
  return window.sessionStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string | null): void {
  if (token) window.sessionStorage.setItem(TOKEN_KEY, token);
  else window.sessionStorage.removeItem(TOKEN_KEY);
}

type Query = Record<string, string | number | boolean | undefined>;

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  query?: Query;
  headers?: Record<string, string>;
  /** Do not treat a 401 as an expired session (used by the login call). */
  skipSessionExpiry?: boolean;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

/** Turns FastAPI error bodies (string detail or validation list) into one string. */
function extractDetail(payload: unknown, fallback: string): string {
  if (!isRecord(payload)) return fallback;
  const { detail } = payload;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => (isRecord(entry) && typeof entry.msg === 'string' ? entry.msg : null))
      .filter((m): m is string => m !== null);
    if (messages.length > 0) return messages.join('; ');
  }
  return fallback;
}

function buildUrl(path: string, query?: Query): string {
  const params = new URLSearchParams();
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value));
  });
  const qs = params.toString();
  return `${API_BASE}${path}${qs ? `?${qs}` : ''}`;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json', ...options.headers };
  const token = getStoredToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';

  let response: Response;
  try {
    response = await fetch(buildUrl(path, options.query), {
      method: options.method ?? 'GET',
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError(0, 'The service is unreachable. Check your connection and try again.');
  }

  if (response.status === 204) return undefined as T;

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = extractDetail(payload, `Request failed (${response.status})`);
    if (response.status === 401 && !options.skipSessionExpiry) {
      window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
    }
    throw new ApiError(response.status, detail);
  }
  return payload as T;
}

export const api = {
  get: <T>(path: string, query?: Query) => request<T>(path, { query }),
  post: <T>(path: string, body?: unknown, options: Omit<RequestOptions, 'method' | 'body'> = {}) =>
    request<T>(path, { ...options, method: 'POST', body }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PATCH', body }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};

// ---- Consent and data rights (FR-003, FR-005) ----

/** The current consent decision, or null when none has been recorded. */
export async function getCurrentConsent(): Promise<ConsentRecord | null> {
  return (await api.get<ConsentRecord | null>('/v1/consents/current')) ?? null;
}

export const saveConsent = (body: ConsentRequest) => api.put<ConsentRecord>('/v1/consents/current', body);

export const listDataRightsRequests = () =>
  api.get<Page<DataRightsRequest>>('/v1/data-rights-requests', { limit: 50 });

export const createDataRightsRequest = (body: DataRightsRequestCreate) =>
  api.post<DataRightsRequest>('/v1/data-rights-requests', body);

export const listConnections = () => api.get<Page<ConnectionItem>>('/v1/connections', { limit: 100 });

export const connectScale = (body: ScaleConnectRequest) =>
  api.post<ConnectionResult>('/v1/connections/scale', body, {
    headers: { 'Idempotency-Key': `scale-${body.device_identifier}` },
  });

export const listWearableProviders = () => api.get<WearableProvider[]>('/v1/connections/providers');

export const beginWearableAuthorization = (provider: string) =>
  api.post<WearableAuthorization>(`/v1/connections/wearables/${encodeURIComponent(provider)}/authorizations`, {});

export const completeWearableAuthorization = (provider: string, body: WearableCallback) =>
  api.post<ConnectionResult>(`/v1/connections/wearables/${encodeURIComponent(provider)}/callbacks`, body);

export const getTrend = (metric: string, range: TrendRange) =>
  api.get<TrendResponse>(`/v1/trends/${encodeURIComponent(metric)}`, { range });

export const listInsights = () => api.get<Page<Insight>>('/v1/insights', { limit: 100 });

export const submitInsightFeedback = (insightId: string, useful: boolean) =>
  api.post<InsightFeedback>(`/v1/insights/${encodeURIComponent(insightId)}/feedback`, { useful });

// ---- Alerts and goals (FR-015, FR-016, FR-017) ----

export const listAlerts = () => api.get<Page<WellnessAlert>>('/v1/alerts', { limit: 100 });

export const acknowledgeAlert = (alertId: string) =>
  api.post<WellnessAlert>(`/v1/alerts/${encodeURIComponent(alertId)}/acknowledgements`, {});

export const listGoals = () => api.get<Page<Goal>>('/v1/goals', { limit: 100 });

export const createGoal = (body: GoalCreateRequest) => api.post<Goal>('/v1/goals', body);

export const updateGoalState = (goalId: string, state: 'active' | 'paused' | 'closed') =>
  api.patch<Goal>(`/v1/goals/${encodeURIComponent(goalId)}`, { state });

// ---- Dashboard and support (FR-011, FR-023) ----

export const getDashboard = () => api.get<DashboardData>('/v1/dashboard');

export const listAlertsByState = (state: 'active' | 'acknowledged') =>
  api.get<Page<WellnessAlert>>('/v1/alerts', { limit: 100, state });

export const createSupportRequest = (body: SupportRequestCreate) =>
  api.post<SupportRequestReceipt>('/v1/support-requests', body);
