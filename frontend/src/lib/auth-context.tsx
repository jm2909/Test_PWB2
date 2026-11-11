import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { api, getStoredToken, SESSION_EXPIRED_EVENT, setStoredToken } from './api-client';
import type { Account, LoginRequest, TokenResponse } from '../types/auth';

const USER_KEY = 'fitconnect.user';

interface AuthState {
  user: Account | null;
  /** True after a 401 ended the session; cleared by the next login. */
  sessionTimedOut: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

function readStoredUser(): Account | null {
  if (!getStoredToken()) return null;
  const raw = window.sessionStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Account;
  } catch {
    return null;
  }
}

function clearSession(): void {
  setStoredToken(null);
  window.sessionStorage.removeItem(USER_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Account | null>(readStoredUser);
  const [sessionTimedOut, setSessionTimedOut] = useState(false);

  useEffect(() => {
    const onExpired = () => {
      if (!getStoredToken()) return;
      clearSession();
      setUser(null);
      setSessionTimedOut(true);
    };
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    const result = await api.post<TokenResponse>('/v1/auth/tokens', credentials, {
      skipSessionExpiry: true,
    });
    setStoredToken(result.access_token);
    window.sessionStorage.setItem(USER_KEY, JSON.stringify(result.account));
    setUser(result.account);
    setSessionTimedOut(false);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.delete<void>('/v1/auth/tokens/current');
    } catch {
      // The local session is ended regardless of the server response.
    }
    clearSession();
    setUser(null);
    setSessionTimedOut(false);
  }, []);

  const value = useMemo(
    () => ({ user, sessionTimedOut, login, logout }),
    [user, sessionTimedOut, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
