import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { SupportPage } from '../pages/SupportPage';
import { renderWithProviders } from '../test/render';

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

const ALERT_ID = '3f2b8c1e-1111-4222-8333-444455556666';

afterEach(() => vi.unstubAllGlobals());

describe('SupportPage', () => {
  it('prefills the context from the query string and submits with the alert id', async () => {
    const fetchMock = vi.fn(async () =>
      json({ id: 'x', reference: 'SUP-ABCDEF0123456789', status: 'submitted', submitted_at: '2026-11-11T10:05:00Z' }, 201),
    );
    vi.stubGlobal('fetch', fetchMock);
    renderWithProviders(<SupportPage />, `/support?context=alert&id=${ALERT_ID}`);

    expect(screen.getByRole('heading', { name: 'Contact support', level: 1 })).toBeInTheDocument();
    expect(screen.getByLabelText(/An alert/)).toBeChecked();
    expect(screen.getByLabelText('Category')).toHaveValue('alert');

    await userEvent.type(screen.getByLabelText('Describe the problem'), 'The alert looks wrong');
    expect(screen.getByText('21 of 2000 characters')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Send request' }));

    expect(await screen.findByText('SUP-ABCDEF0123456789')).toBeInTheDocument();
    expect(screen.getByText('Request received.')).toBeInTheDocument();
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(JSON.parse(String(init.body))).toEqual({
      category: 'alert',
      description: 'The alert looks wrong',
      context_type: 'alert',
      context_id: ALERT_ID,
    });
  });

  it('requires a description and makes no call', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    renderWithProviders(<SupportPage />, '/support?context=account');
    expect(screen.getByLabelText(/My account/)).toBeChecked();
    await userEvent.click(screen.getByRole('button', { name: 'Send request' }));
    expect(await screen.findByText('Enter a description of 1 to 2000 characters.')).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('shows the not-sent state when the request fails', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => json({ detail: 'boom' }, 500)));
    renderWithProviders(<SupportPage />, '/support?context=device');
    await userEvent.type(screen.getByLabelText('Describe the problem'), 'Cannot connect');
    await userEvent.click(screen.getByRole('button', { name: 'Send request' }));
    expect(await screen.findByText(/Your request was not sent/)).toBeInTheDocument();
    expect(screen.queryByText('Request received.')).not.toBeInTheDocument();
  });
});
