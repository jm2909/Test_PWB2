import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConsentPage } from '../pages/ConsentPage';
import { renderWithProviders } from '../test/render';

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const emptyPage = { items: [], limit: 50, offset: 0, total: 0 };
const granted = {
  id: '1',
  decision: 'granted',
  notice_version: 'v1.0',
  recorded_at: '2026-11-11T09:14:00Z',
  collection_allowed: true,
  data_rights_path: null,
};

afterEach(() => vi.restoreAllMocks());

describe('ConsentPage', () => {
  it('shows the not-recorded state with the collection gate when there is no consent', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) =>
      Promise.resolve(
        String(input).includes('consents')
          ? jsonResponse(null)
          : jsonResponse(emptyPage),
      ),
    );
    renderWithProviders(<ConsentPage />, '/consent');
    expect(await screen.findByText('No consent recorded.')).toBeInTheDocument();
    expect(screen.getByText(/Manual entry: unavailable until consent is granted/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Privacy consent and data rights' })).toBeInTheDocument();
    expect(screen.getByRole('table', { name: /Data categories/ })).toBeInTheDocument();
  });

  it('saves a granted decision with the notice version and categories', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
      const url = String(input);
      if (url.includes('consents') && init?.method === 'PUT') return Promise.resolve(jsonResponse(granted));
      if (url.includes('consents')) return Promise.resolve(jsonResponse(null));
      return Promise.resolve(jsonResponse(emptyPage));
    });
    renderWithProviders(<ConsentPage />, '/consent');
    await screen.findByText('No consent recorded.');
    await userEvent.click(screen.getByRole('button', { name: 'Save my decision' }));
    expect(await screen.findByText('Consent granted')).toBeInTheDocument();
    const put = fetchMock.mock.calls.find(([, init]) => init?.method === 'PUT');
    const body = JSON.parse(String(put?.[1]?.body)) as Record<string, unknown>;
    expect(body).toMatchObject({ decision: 'granted', notice_version: 'v1.0', purpose: 'wellness_support' });
    expect(body.data_categories).toHaveLength(5);
  });

  it('shows the withdrawn state after withdrawing', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
      const url = String(input);
      if (url.includes('consents') && init?.method === 'PUT') {
        return Promise.resolve(
          jsonResponse({ ...granted, decision: 'withdrawn', collection_allowed: false, data_rights_path: '/data-rights' }),
        );
      }
      if (url.includes('consents')) return Promise.resolve(jsonResponse(granted));
      return Promise.resolve(jsonResponse(emptyPage));
    });
    renderWithProviders(<ConsentPage />, '/consent');
    await screen.findByText('Consent granted');
    await userEvent.click(screen.getByLabelText(/I do not agree/));
    await userEvent.click(screen.getByRole('button', { name: 'Save my decision' }));
    const status = await screen.findByText('Consent withdrawn.');
    expect(status).toBeInTheDocument();
  });
});
