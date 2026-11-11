import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { InsightCard } from '../components/trends/InsightCard';
import { TrendChart } from '../components/trends/TrendChart';
import type { ChartPoint } from '../components/trends/TrendChart';
import { TrendTable } from '../components/trends/TrendTable';
import { Icon } from '../components/ui/Icon';
import { Notice } from '../components/ui/Notice';
import { getTrend, listConnections, listInsights } from '../lib/api-client';
import { formatDateTime } from '../lib/format';
import { ApiError } from '../types/api';
import type { ConnectionItem } from '../types/connection';
import type { Insight } from '../types/insight';
import type { TrendMetric, TrendRange, TrendResponse } from '../types/trend';

const METRICS: Record<TrendMetric, { option: string; name: string; unit: string; source: string; sourceKind: 'scale' | 'wearable' }> = {
  weight: { option: 'Weight (kg)', name: 'Weight', unit: 'kilograms (kg)', source: 'Sapphire scale', sourceKind: 'scale' },
  steps: { option: 'Steps (steps per day)', name: 'Steps', unit: 'steps per day', source: 'Approved wearable', sourceKind: 'wearable' },
  sleep_duration: { option: 'Sleep duration (hours)', name: 'Sleep duration', unit: 'hours', source: 'Approved wearable', sourceKind: 'wearable' },
};
const RANGES: ReadonlyArray<{ value: TrendRange; label: string; days: number }> = [
  { value: '7d', label: '7 days', days: 7 },
  { value: '30d', label: '30 days', days: 30 },
  { value: '90d', label: '90 days', days: 90 },
  { value: '365d', label: '365 days', days: 365 },
];
const dateFmt = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const DAY_MS = 86_400_000;

export function TrendsPage() {
  const [metric, setMetric] = useState<TrendMetric>('weight');
  const [range, setRange] = useState<TrendRange>('30d');
  const [trend, setTrend] = useState<TrendResponse | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [connections, setConnections] = useState<ConnectionItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([listInsights(), listConnections()])
      .then(([ins, conns]) => {
        if (!active) return;
        setInsights(ins.items);
        setConnections(conns.items);
      })
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getTrend(metric, range)
      .then((response) => {
        if (!active) return;
        setTrend(response);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setTrend(null);
        setError(err instanceof ApiError ? err.detail : 'The trend could not be loaded. Try again.');
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [metric, range]);

  const meta = METRICS[metric];
  const rangeInfo = RANGES.find((r) => r.value === range) ?? RANGES[1];

  const points: ChartPoint[] = useMemo(
    () =>
      (trend?.points ?? [])
        .map((p) => ({ time: new Date(p.captured_at).getTime(), value: Number(p.value) }))
        .filter((p) => Number.isFinite(p.time) && Number.isFinite(p.value))
        .sort((a, b) => a.time - b.time),
    [trend],
  );

  const insight = useMemo(
    () =>
      insights
        .filter((i) => i.metric_type === metric)
        .sort((a, b) => b.created_at.localeCompare(a.created_at))[0],
    [insights, metric],
  );

  const attention = connections.filter(
    (c) => c.source === meta.sourceKind && (c.status === 'stale' || c.status === 'failed'),
  );

  const heading = `${meta.name} over the last ${rangeInfo.days} days`;
  const available = trend?.status === 'available' && points.length > 0;
  const valueHeading = `${meta.name} (${trend?.unit ?? ''})`.replace(' ()', '');
  const rangeText = available
    ? `${dateFmt.format(new Date(points[0].time))} to ${dateFmt.format(new Date(points[points.length - 1].time))}`
    : rangeInfo.label;

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Your own data only</p>
          <h1 id="page-title">Trends and insights</h1>
          <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
            See how one measurement has changed over time and read general wellness observations. Trends describe your
            recorded readings; they are not medical findings.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="ctl-h">
        <h2 className="sr-only" id="ctl-h">
          Choose a metric and time range
        </h2>
        <div className="page-grid grid gap-8 lg:grid-cols-[5fr_10fr]">
          <div>
            <label className="field-label" htmlFor="metric">
              Metric
            </label>
            <select
              id="metric"
              name="metric"
              className="field-input"
              value={metric}
              onChange={(e) => setMetric(e.target.value as TrendMetric)}
            >
              {(Object.keys(METRICS) as TrendMetric[]).map((key) => (
                <option key={key} value={key}>
                  {METRICS[key].option}
                </option>
              ))}
            </select>
          </div>
          <fieldset className="min-w-0 border-0 p-0">
            <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">Time range</legend>
            <div className="flex">
              {RANGES.map((r, index) => (
                <label key={r.value} className={`relative min-w-0 flex-1 ${index > 0 ? '-ml-px' : ''}`}>
                  <input
                    type="radio"
                    name="range"
                    value={r.value}
                    checked={range === r.value}
                    onChange={() => setRange(r.value)}
                    className="peer absolute inset-0 m-0 h-full w-full cursor-pointer opacity-0"
                  />
                  <span className="flex min-h-[2.5rem] items-center justify-center border border-line-strong bg-surface px-3 text-center text-ink-secondary peer-checked:border-[#393939] peer-checked:bg-[#393939] peer-checked:text-white peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:-outline-offset-2 peer-focus-visible:outline-primary">
                    {r.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="chart-h">
        <div className="page-grid">
          <div className="tile">
            <h2 id="chart-h" className="mb-3 text-xl">
              {heading}
            </h2>
            {loading && <p role="status">Loading trend…</p>}
            {error && <Notice kind="error">{error}</Notice>}
            {!loading && trend && (
              <>
                <p className="mb-2 text-xs text-ink-secondary">
                  Unit: {meta.unit} · Range: {rangeText} · Source: {meta.source}
                </p>
                {attention.length > 0 && (
                  <div className="mb-3">
                    <Notice kind="warning" role="status">
                      <p>
                        {meta.name} comes from a source that is out of date
                        {attention[0].last_successful_sync_at
                          ? `. The trend shows only readings up to ${formatDateTime(attention[0].last_successful_sync_at)}.`
                          : '. Newer readings may be missing.'}{' '}
                        <Link to="/connections">Check your connections</Link>
                      </p>
                    </Notice>
                  </div>
                )}
                {available ? (
                  <>
                    <TrendChart
                      points={points}
                      title={`${meta.name}, ${rangeText}`}
                      description={`Line chart of ${meta.name.toLowerCase()} over ${rangeInfo.label}, ${points.length} readings. Values are in the table below.`}
                      unitLabel={valueHeading}
                      gapMs={Math.max(2 * DAY_MS, (rangeInfo.days / 10) * DAY_MS)}
                    />
                    <TrendTable points={points} valueHeading={valueHeading} source={meta.source} />
                  </>
                ) : (
                  <div
                    className="flex min-h-[12rem] flex-col items-center justify-center border border-dashed border-line-strong bg-white p-6 text-center"
                    role="status"
                  >
                    <span className="inline-flex items-start gap-2">
                      <Icon name="warn" size={20} className="text-warn-icon" />
                      <strong>Not enough data to show a trend</strong>
                    </span>
                    <p className="mt-2 max-w-[22rem]">
                      {trend.explanation ??
                        'A trend needs more readings, so none is shown and nothing is implied.'}
                    </p>
                    <p className="mt-2 text-xs text-ink-secondary">
                      Try a shorter range or <Link to="/connections">check your connections</Link>.
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="ins-h">
        <div className="page-grid">
          <h2 id="ins-h" className="mb-4 text-xl">
            Insight
          </h2>
          {insight ? (
            <InsightCard key={insight.id} insight={insight} />
          ) : (
            <Notice kind="info">
              <p>No insight is available for {meta.name.toLowerCase()} yet.</p>
            </Notice>
          )}
        </div>
      </section>
    </>
  );
}
