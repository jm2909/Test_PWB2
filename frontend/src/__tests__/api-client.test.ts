import { API_BASE, ApiError, api, getStoredSession, storeSession } from '../lib/api-client';

function mockFetch(status: number, body?: unknown) {
  const fn = vi.fn().mockResolvedValue(
    new Response(body === undefined ? null : JSON.stringify(body), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
  vi.stubGlobal('fetch', fn);
  return fn;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('api-client', () => {
  it('uses the /api/v1 base by default', () => {
    expect(API_BASE).toBe('/api/v1');
  });

  it('prefixes paths with the base and sends the bearer token', async () => {
    storeSession({
      access_token: 'tok',
      expires_at: '2030-01-01T00:00:00Z',
      user: { id: 1, email: 'a@example.com', onboarding_status: 'complete' },
    });
    const fetchMock = mockFetch(200, { items: [], total: 0 });
    const result = await api.get<{ items: unknown[]; total: number }>('/insights');
    expect(result.total).toBe(0);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('/api/v1/insights');
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer tok');
  });

  it('throws ApiError with status and detail', async () => {
    mockFetch(409, { detail: 'exists' });
    await expect(api.post('/accounts', {})).rejects.toMatchObject({ status: 409, detail: 'exists' });
    mockFetch(500, { detail: 'boom' });
    await expect(api.get('/x')).rejects.toBeInstanceOf(ApiError);
  });

  it('clears the stored session on 401 for an authenticated call', async () => {
    storeSession({
      access_token: 'tok',
      expires_at: '2030-01-01T00:00:00Z',
      user: { id: 1, email: 'a@example.com', onboarding_status: 'complete' },
    });
    mockFetch(401, { detail: 'Not authenticated' });
    await expect(api.get('/insights')).rejects.toMatchObject({ status: 401 });
    expect(getStoredSession()).toBeNull();
  });

  it('returns undefined for 204 responses', async () => {
    mockFetch(204);
    await expect(api.delete('/auth/sessions/current')).resolves.toBeUndefined();
  });
});
