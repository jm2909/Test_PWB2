import { useState } from 'react';
import { Icon } from '../ui/Icon';
import { Notice } from '../ui/Notice';
import { submitInsightFeedback } from '../../lib/api-client';
import { ApiError } from '../../types/api';
import type { Insight } from '../../types/insight';

const dayFmt = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short' });
const fullFmt = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

const METRIC_NAMES: Record<string, string> = {
  weight: 'Weight',
  steps: 'Steps',
  sleep_duration: 'Sleep duration',
  active_minutes: 'Active minutes',
};

export function metricName(metric: string): string {
  return METRIC_NAMES[metric] ?? metric;
}

/** Limited-data insights carry the fixed "not offered" guidance (TASK-9 InsightService). */
export function isLimitedData(insight: Insight): boolean {
  return /not offered/i.test(insight.wellness_guidance);
}

function periodDays(insight: Insight): number {
  const ms = new Date(insight.observation_period.end).getTime() - new Date(insight.observation_period.start).getTime();
  return Math.max(1, Math.round(ms / 86_400_000));
}

/** One insight: what we measured, wellness guidance, how sure we are, and Useful / Not useful feedback. */
export function InsightCard({ insight }: { insight: Insight }) {
  const [choice, setChoice] = useState<boolean | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const start = new Date(insight.observation_period.start);
  const end = new Date(insight.observation_period.end);
  const name = metricName(insight.metric_type);
  const limited = isLimitedData(insight);
  const titleId = `ins-${insight.id}`;

  const send = async (useful: boolean) => {
    if (saved || busy) return;
    setBusy(true);
    setError(null);
    setChoice(useful);
    try {
      await submitInsightFeedback(insight.id, useful);
      setSaved(true);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) setSaved(true);
      else {
        setChoice(null);
        setError(err instanceof ApiError ? err.detail : 'Your feedback could not be saved. Try again.');
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <article className="border border-line-subtle bg-white p-4" aria-labelledby={titleId}>
      <h3 id={titleId} className="text-base font-semibold">
        {name} · {periodDays(insight)} days
      </h3>
      <p className="text-xs text-ink-secondary">
        Observation period: {dayFmt.format(start)} to {fullFmt.format(end)} · Metric: {name.toLowerCase()}
      </p>
      <h4 className="mt-3 text-xs tracking-label text-ink-secondary">What we measured</h4>
      <p>{insight.observation}</p>
      <h4 className="mt-3 text-xs tracking-label text-ink-secondary">Wellness guidance</h4>
      {limited ? (
        <p className="inline-flex items-start gap-2">
          <Icon name="warn" className="mt-0.5 text-warn-icon" />
          <span>
            <strong>Insufficient data:</strong> {insight.wellness_guidance}
          </span>
        </p>
      ) : (
        <p>{insight.wellness_guidance}</p>
      )}
      <h4 className="mt-3 text-xs tracking-label text-ink-secondary">How sure are we?</h4>
      <p className="inline-flex items-start gap-2">
        <Icon name="warn" className="mt-0.5 text-warn-icon" />
        <span>{insight.uncertainty}</span>
      </p>
      <fieldset className="mt-4 min-w-0 border-0 p-0">
        <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">Was this insight useful?</legend>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn btn-tertiary min-h-[2rem] px-3"
            aria-pressed={choice === true}
            disabled={saved || busy}
            onClick={() => send(true)}
          >
            Useful
          </button>
          <button
            type="button"
            className="btn btn-tertiary min-h-[2rem] px-3"
            aria-pressed={choice === false}
            disabled={saved || busy}
            onClick={() => send(false)}
          >
            Not useful
          </button>
        </div>
      </fieldset>
      <div className="mt-3" aria-live="polite">
        {saved && (
          <Notice kind="success">
            <p>Thanks. Your feedback was saved. You can give one response for each insight.</p>
          </Notice>
        )}
        {error && <Notice kind="error">{error}</Notice>}
      </div>
    </article>
  );
}
