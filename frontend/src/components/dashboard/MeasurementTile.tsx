import { Link } from 'react-router-dom';
import { formatDateTime, formatNumber } from '../../lib/format';
import type { DashboardMeasurement } from '../../types/dashboard';
import { StatusBadge } from '../ui/StatusBadge';

export const METRIC_LABELS: Record<string, string> = {
  weight: 'Weight',
  steps: 'Steps',
  sleep_duration: 'Sleep',
  active_minutes: 'Active time',
};

const UNIT_LABELS: Record<string, string> = { count: 'steps', hours: 'h', minutes: 'min' };
const SOURCE_LABELS: Record<string, string> = {
  scale: 'Sapphire scale',
  wearable: 'Approved wearable',
  manual: 'Manual entry',
};

interface Props {
  metric: string;
  measurement?: DashboardMeasurement;
  simplified: boolean;
}

/** One latest-reading tile: value, unit, source and time, or an explicit unavailable state. */
export function MeasurementTile({ metric, measurement, simplified }: Props) {
  const label = METRIC_LABELS[metric] ?? metric;
  const titleId = `reading-${metric}`;

  if (!measurement) {
    return (
      <article className="h-full border border-dashed border-t-[3px] border-line-strong bg-white p-4" aria-labelledby={titleId}>
        <h3 id={titleId}>{label}</h3>
        <p className="mt-2">
          <StatusBadge status="unavailable" />
        </p>
        <p className="mt-2 text-xs tracking-label text-ink-secondary">
          No recent {label.toLowerCase()} data, so no value is shown rather than an old or guessed one.
        </p>
        {!simplified && (
          <p className="mt-2">
            <Link to="/connections">Check connections</Link>
          </p>
        )}
      </article>
    );
  }

  const unit = UNIT_LABELS[measurement.unit] ?? measurement.unit;
  return (
    <article className="h-full border-t-[3px] border-line-strong bg-surface p-4" aria-labelledby={titleId}>
      <h3 id={titleId}>{label}</h3>
      <p className="text-[2.5rem] font-light leading-[3rem]">
        {formatNumber(Number(measurement.value))} <small className="text-base text-ink-secondary">{unit}</small>
      </p>
      {measurement.status === 'stale' && (
        <p className="mt-1">
          <StatusBadge status="stale" />
        </p>
      )}
      {!simplified && (
        <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-xs tracking-label text-ink-secondary">
          <dt>Source</dt>
          <dd>{SOURCE_LABELS[measurement.source] ?? measurement.source}</dd>
          <dt>Recorded</dt>
          <dd>{formatDateTime(measurement.captured_at)}</dd>
        </dl>
      )}
    </article>
  );
}
