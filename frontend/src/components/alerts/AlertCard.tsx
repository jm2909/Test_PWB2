import { Link } from 'react-router-dom';
import { formatDateTime } from '../../lib/format';
import type { WellnessAlert } from '../../types/alert';
import { StatusBadge } from '../ui/StatusBadge';

interface Props {
  alert: WellnessAlert;
  onAcknowledge?: (alert: WellnessAlert) => void;
  busy?: boolean;
}

const TITLES: Record<string, string> = {
  weight: 'Weight change pattern',
  steps: 'Activity pattern',
  active_minutes: 'Activity pattern',
  sleep_duration: 'Sleep pattern',
};

export function alertTitle(metric: string): string {
  return TITLES[metric] ?? 'Pattern in your readings';
}

/** One alert: metric, event time, non-clinical reason, rule identifier and version, and its actions. */
export function AlertCard({ alert, onAcknowledge, busy }: Props) {
  const acknowledged = alert.state === 'acknowledged';
  const titleId = `alert-${alert.id}`;
  return (
    <article
      className={`mb-4 border border-l-4 border-line-subtle p-4 ${
        acknowledged ? 'border-l-line-strong bg-surface' : 'border-l-warn-icon bg-white'
      }`}
      aria-labelledby={titleId}
    >
      <header className="mb-3 flex flex-wrap justify-between gap-2">
        <h3 id={titleId}>{alertTitle(alert.metric_type)}</h3>
        <strong className="font-semibold">
          <StatusBadge status={acknowledged ? 'acknowledged' : 'active'} />
        </strong>
      </header>
      <dl className="grid gap-x-4 gap-y-2 sm:grid-cols-[minmax(8rem,12rem)_1fr]">
        <dt className="text-ink-secondary">Event time</dt>
        <dd className="m-0">{formatDateTime(alert.event_at)}</dd>
        <dt className="text-ink-secondary">What was noticed</dt>
        <dd className="m-0">{alert.reason}</dd>
        <dt className="text-ink-secondary">Rule</dt>
        <dd className="m-0">
          {alert.rule_identifier} · version {alert.rule_version}
        </dd>
        {acknowledged && (
          <>
            <dt className="text-ink-secondary">Acknowledged</dt>
            <dd className="m-0">{formatDateTime(alert.acknowledged_at)}</dd>
          </>
        )}
      </dl>
      <p className="mt-3 text-xs tracking-label text-ink-secondary">{alert.wellness_boundary}</p>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        {!acknowledged && onAcknowledge && (
          <button className="btn" type="button" disabled={busy} onClick={() => onAcknowledge(alert)}>
            Acknowledge alert
          </button>
        )}
        <Link className="btn btn-tertiary" to={`/support?context=alert&id=${encodeURIComponent(alert.id)}`}>
          Get help with this alert
        </Link>
      </div>
    </article>
  );
}
