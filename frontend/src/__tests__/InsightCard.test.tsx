import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { InsightCard } from '../components/trends/InsightCard';
import type { Insight } from '../types/insight';

const insight: Insight = {
  id: 'i1',
  metric_type: 'weight',
  observation_period: { start: '2026-10-12T00:00:00Z', end: '2026-11-11T00:00:00Z' },
  observation: 'Your recorded weight went from 73.6 kg to 72.4 kg.',
  wellness_guidance: 'Small, steady changes are common.',
  uncertainty: 'Some uncertainty: 6 days had no reading.',
  created_at: '2026-11-11T08:00:00Z',
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

afterEach(() => vi.restoreAllMocks());

describe('InsightCard', () => {
  it('separates what we measured from wellness guidance and uncertainty', () => {
    render(<InsightCard insight={insight} />);
    expect(screen.getByRole('heading', { name: 'What we measured' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Wellness guidance' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'How sure are we?' })).toBeInTheDocument();
    expect(screen.getByText(/Observation period: 12 Oct to 11 Nov 2026/)).toBeInTheDocument();
  });

  it('submits Useful, sets aria-pressed and shows the saved notice', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(json({ id: 'f1', insight_id: 'i1', useful: true, submitted_at: '2026-11-11T09:00:00Z' }, 201));
    render(<InsightCard insight={insight} />);
    const useful = screen.getByRole('button', { name: 'Useful' });
    expect(useful).toHaveAttribute('aria-pressed', 'false');
    await userEvent.click(useful);
    expect(await screen.findByText(/Your feedback was saved/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Useful' })).toHaveAttribute('aria-pressed', 'true');
    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toContain('/v1/insights/i1/feedback');
    expect(JSON.parse(String(init?.body))).toEqual({ useful: true });
  });

  it('treats a duplicate response as already saved', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(json({ detail: 'Feedback already submitted' }, 409));
    render(<InsightCard insight={insight} />);
    await userEvent.click(screen.getByRole('button', { name: 'Not useful' }));
    expect(await screen.findByText(/Your feedback was saved/)).toBeInTheDocument();
  });

  it('shows the limited-data insight as insufficient data', () => {
    render(
      <InsightCard
        insight={{
          ...insight,
          id: 'i2',
          metric_type: 'steps',
          wellness_guidance: 'Wellness guidance is not offered until enough readings are available.',
        }}
      />,
    );
    expect(screen.getByText('Insufficient data:')).toBeInTheDocument();
  });
});
