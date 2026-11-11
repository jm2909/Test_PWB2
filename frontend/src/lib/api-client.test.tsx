import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { api, SESSION_EXPIRED_EVENT } from './api-client';
import { ApiError } from '../types/api';
import { StatusBadge } from '../components/ui/StatusBadge';
import { formatDateTime } from './format';

describe('api-client', () => {
  it('throws ApiError with detail and emits session-expired on 401', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Session is not active' }), { status: 401 }),
    );
    const listener = vi.fn();
    window.addEventListener(SESSION_EXPIRED_EVENT, listener);
    await expect(api.get('/v1/dashboard')).rejects.toMatchObject({ status: 401, detail: 'Session is not active' });
    await expect(api.get('/v1/dashboard')).rejects.toBeInstanceOf(ApiError);
    expect(listener).toHaveBeenCalled();
    window.removeEventListener(SESSION_EXPIRED_EVENT, listener);
    vi.restoreAllMocks();
  });
});

describe('StatusBadge', () => {
  it('renders text with the icon, not colour alone', () => {
    const { container } = render(<StatusBadge status="stale" />);
    expect(screen.getByText('Stale')).toBeInTheDocument();
    expect(container.querySelector('svg')).not.toBeNull();
  });
});

describe('format', () => {
  it('returns a dash for missing values', () => {
    expect(formatDateTime(null)).toBe('—');
  });
});
