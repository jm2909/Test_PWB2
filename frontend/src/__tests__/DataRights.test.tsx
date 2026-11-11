import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ConsentPage } from '../pages/ConsentPage';
import { renderWithProviders } from '../test/render';

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const existing = {
  id: 'a',
  reference: 'DR-AAAAAAAAAAAAAAAA',
  request_type: 'deletion',
  status: 'in_review',
  requested_at: '2026-11-02T09:00:00Z',
  fulfillment_due_at: '2026-12-02T09:00:00Z',
};

afterEach(() => vi.restoreAllMocks());

describe('Data rights', () => {
  it('lists existing requests and adds a submitted export with its reference', async () => {
    const created = {
      id: 'b',
      reference: 'DR-BBBBBBBBBBBBBBBB',
      request_type: 'export',
      status: 'submitted',
      requested_at: '2026-11-11T09:20:00Z',
      fulfillment_due_at: '2026-12-11T09:20:00Z',
    };
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
      const url = String(input);
      if (url.includes('consents')) return Promise.resolve(jsonResponse(null));
      if (init?.method === 'POST') return Promise.resolve(jsonResponse(created, 201));
      return Promise.resolve(jsonResponse({ items: [existing], limit: 50, offset: 0, total: 1 }));
    });
    renderWithProviders(<ConsentPage />, '/consent');
    const table = await screen.findByRole('table', { name: 'Your requests' });
    expect(within(table).getByText('DR-AAAAAAAAAAAAAAAA')).toBeInTheDocument();
    expect(within(table).getByText('In review')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Submit request' }));
    expect(await screen.findByText('Request received. Keep this reference.')).toBeInTheDocument();
    expect(within(await screen.findByRole('table', { name: 'Your requests' })).getByText('DR-BBBBBBBBBBBBBBBB')).toBeInTheDocument();
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(post?.[0]).toBe('/api/v1/data-rights-requests');
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({ request_type: 'export' });
  });

  it('submits a deletion request when that option is chosen', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
      const url = String(input);
      if (url.includes('consents')) return Promise.resolve(jsonResponse(null));
      if (init?.method === 'POST') return Promise.resolve(jsonResponse({ ...existing, status: 'submitted' }, 201));
      return Promise.resolve(jsonResponse({ items: [], limit: 50, offset: 0, total: 0 }));
    });
    renderWithProviders(<ConsentPage />, '/consent');
    await userEvent.click(await screen.findByLabelText(/Delete my data/));
    await userEvent.click(screen.getByRole('button', { name: 'Submit request' }));
    await screen.findByText('Request received. Keep this reference.');
    const post = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(JSON.parse(String(post?.[1]?.body))).toEqual({ request_type: 'deletion' });
  });
});
