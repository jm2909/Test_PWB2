import type { StoredSession } from '../types/account';

export const API_BASE: string = import.meta.env.VITE_API_URL ?? '/api/v1';
export const SESSION_KEY = 'fitconnect.session';

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export function getStoredSession(): StoredSession | null {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (
      typeof parsed === 'object' &&
      parsed !== null &&
      typeof (parsed as StoredSession).access_token === 'string' &&
      typeof (parsed as StoredSession).user === 'object'
    ) {
      return parsed as StoredSession;
    }
  } catch {
    // fall through to clearing the corrupt entry
  }
  sessionStorage.removeItem(SESSION_KEY);
  return null;
}

export function storeSession(session: StoredSession): void {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | null = null;

/** Registered by the auth context so a 401 on an authenticated call signs the user out. */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler;
}

function detailFrom(body: unknown, fallback: string): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const msgs = detail
        .map((d: unknown) =>
          typeof d === 'object' && d !== null && 'msg' in d ? String((d as { msg: unknown }).msg) : '',
        )
        .filter(Boolean);
      if (msgs.length > 0) return msgs.join('; ');
    }
  }
  return fallback;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  const session = getStoredSession();
  if (session) headers.Authorization = `Bearer ${session.access_token}`;
  Object.assign(headers, options.headers);
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError(0, 'Unable to reach the server. Check your connection and try again.');
  }

  if (response.status === 204) return undefined as T;

  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    if (response.status === 401 && session) {
      clearSession();
      unauthorizedHandler?.();
    }
    throw new ApiError(response.status, detailFrom(payload, response.statusText || 'Request failed'));
  }
  return payload as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown, headers?: Record<string, string>) =>
    request<T>(path, { method: 'POST', body, headers }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
