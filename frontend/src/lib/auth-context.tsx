import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  api,
  clearSession,
  getStoredSession,
  setUnauthorizedHandler,
  storeSession,
} from './api-client';
import type { AccountUser, SessionResponse } from '../types/account';

interface AuthContextValue {
  user: AccountUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AccountUser | null>(() => getStoredSession()?.user ?? null);

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const session = await api.post<SessionResponse>('/auth/sessions', { email, password });
    storeSession({
      access_token: session.access_token,
      expires_at: session.expires_at,
      user: session.user,
    });
    setUser(session.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.delete<void>('/auth/sessions/current');
    } catch {
      // The local session is dropped even if the server could not be reached.
    } finally {
      clearSession();
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: user !== null, login, logout }),
    [user, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
