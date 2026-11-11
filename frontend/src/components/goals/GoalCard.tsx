import { Link } from 'react-router-dom';
import { formatNumber } from '../../lib/format';
import type { Goal } from '../../types/goal';
import { Notice } from '../ui/Notice';
import { StatusBadge } from '../ui/StatusBadge';

interface Props {
  goal: Goal;
  onChange: (goal: Goal, state: 'active' | 'paused' | 'closed') => void;
  busy?: boolean;
}

const CATEGORY_LABEL: Record<string, string> = {
  weight_management: 'Weight management',
  fitness: 'Fitness',
  sleep_improvement: 'Sleep improvement',
  general_wellness: 'General wellness',
};

const METRIC_PHRASE: Record<string, (v: string) => string> = {
  weight: (v) => `Weight to ${v} kg`,
  steps: (v) => `${v} steps per day`,
  sleep_duration: (v) => `Sleep to ${v} hours`,
};

function unitLabel(metric: string, unit: string): string {
  if (metric === 'steps') return 'steps per day';
  return unit;
}

export function goalTitle(goal: Goal): string {
  const value = formatNumber(Number(goal.target_value), 2);
  const phrase = METRIC_PHRASE[goal.metric_type]?.(value) ?? `${goal.metric_type} ${value} ${goal.target_unit}`;
  return `${CATEGORY_LABEL[goal.category] ?? goal.category} · ${phrase}`;
}

const dateOnly = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });

function targetDate(iso: string): string {
  return dateOnly.format(new Date(`${iso}T00:00:00Z`));
}

/** One goal: target, progress (only when data exists) or a data-gap message, state badge and actions. */
export function GoalCard({ goal, onChange, busy }: Props) {
  const titleId = `goal-${goal.id}`;
  const state = goal.state;
  const value = formatNumber(Number(goal.target_value), 2);
  const current = goal.current_value === null ? null : formatNumber(Number(goal.current_value), 2);
  const unit = unitLabel(goal.metric_type, goal.target_unit);
  return (
    <article
      className={`mb-4 border border-line-subtle p-4 ${state === 'active' ? 'bg-white' : 'bg-surface'}`}
      aria-labelledby={titleId}
    >
      <header className="mb-2 flex flex-wrap justify-between gap-2">
        <h3 id={titleId}>{goalTitle(goal)}</h3>
        <strong className="font-semibold">
          {state === 'active' && <StatusBadge status="current" label="Active" />}
          {state === 'paused' && <StatusBadge status="unavailable" label="Paused" />}
          {state === 'closed' && <StatusBadge status="acknowledged" label="Closed" />}
        </strong>
      </header>
      <dl className="grid gap-x-4 gap-y-2 sm:grid-cols-[minmax(8rem,12rem)_1fr]">
        <dt className="text-ink-secondary">Target</dt>
        <dd className="m-0">
          {value} {unit} by {targetDate(goal.target_date)}
        </dd>
        {state === 'active' && (
          <>
            <dt className="text-ink-secondary">Progress</dt>
            <dd className="m-0">
              {goal.progress_status === 'available' ? (
                <>
                  <StatusBadge status="current" label="Available" /> · current {current} {unit}
                </>
              ) : (
                <StatusBadge status="stale" label="Data gap" />
              )}
            </dd>
          </>
        )}
        {state === 'paused' && (
          <>
            <dt className="text-ink-secondary">Progress</dt>
            <dd className="m-0">Not tracked while paused</dd>
          </>
        )}
      </dl>
      {state === 'active' && goal.progress_status === 'data_gap' && (
        <div className="mt-3">
          <Notice kind="warning" role="status">
            <p>
              No recent readings, so progress cannot be shown. <Link to="/connections">Check connection</Link>
            </p>
          </Notice>
        </div>
      )}
      {state === 'paused' && (
        <p className="mt-2 text-xs tracking-label text-ink-secondary">
          Your past readings are kept and still appear in your trends.
        </p>
      )}
      {state === 'closed' && (
        <div className="mt-3">
          <Notice kind="info">
            <p>This goal is closed. Your readings from while it was active have not been deleted.</p>
          </Notice>
        </div>
      )}
      {state !== 'closed' && (
        <div className="mt-3 flex flex-wrap gap-2">
          {state === 'active' ? (
            <button className="btn btn-tertiary" type="button" disabled={busy} onClick={() => onChange(goal, 'paused')}>
              Pause goal
            </button>
          ) : (
            <button className="btn" type="button" disabled={busy} onClick={() => onChange(goal, 'active')}>
              Resume goal
            </button>
          )}
          <button className="btn btn-tertiary" type="button" disabled={busy} onClick={() => onChange(goal, 'closed')}>
            Close goal
          </button>
        </div>
      )}
    </article>
  );
}
