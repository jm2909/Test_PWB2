import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import ExplanationTile from '../components/trends/ExplanationTile';
import MetricControls from '../components/trends/MetricControls';
import TrendChart from '../components/trends/TrendChart';
import TrendTable from '../components/trends/TrendTable';
import Notification from '../components/common/Notification';
import { ApiError, api } from '../lib/api-client';
import { METRIC_OPTIONS } from '../types/trend';
import type { MetricExplanation, TrendMetric, TrendPeriod, TrendResponse } from '../types/trend';

const WAITING_TEXT = 'Once there are enough readings across this period, you will see the overall direction here.';

export default function TrendsPage() {
  const [metric, setMetric] = useState<TrendMetric>('weight');
  const [period, setPeriod] = useState<TrendPeriod>(30);
  const [trend, setTrend] = useState<TrendResponse | null>(null);
  const [explanation, setExplanation] = useState<MetricExplanation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setTrend(null);
    setExplanation(null);
    setError(null);
    const run = async () => {
      try {
        const [t, e] = await Promise.all([
          api.get<TrendResponse>(`/trends?metric_type=${metric}&period_days=${period}`),
          api.post<MetricExplanation>('/metric-explanations', { metric_type: metric, period_days: period }),
        ]);
        if (!cancelled) {
          setTrend(t);
          setExplanation(e);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Your trend could not be loaded.');
      }
    };
    void run();
    return () => {
      cancelled = true;
    };
  }, [metric, period]);

  const option = METRIC_OPTIONS.find((o) => o.value === metric) ?? METRIC_OPTIONS[0];
  const heading = `${option.label} over the last ${period} days`;
  const unavailable = explanation?.status === 'unavailable';
  const points = trend?.points ?? [];
  const tableColumn = `${option.label} (${option.unit})`;

  let tileText = '';
  if (explanation) tileText = explanation.status === 'insufficient_history' ? WAITING_TEXT : explanation.explanation;

  return (
    <section aria-labelledby="trends-h">
      <h1 id="trends-h" className="text-[2rem] leading-10">Trends</h1>
      <p className="mt-2 max-w-3xl text-base text-text-secondary">
        Pick a measurement and a time period to see how it has changed, with a plain-language explanation.
      </p>
      <div className="mt-8">
        <MetricControls metric={metric} period={period} onMetric={setMetric} onPeriod={setPeriod} />
      </div>
      {error && (
        <Notification kind="error" title="Trend not loaded" role="alert" className="mb-4">
          <p>{error}</p>
        </Notification>
      )}
      <div className="grid gap-8 lg:grid-cols-16">
        <section className="border border-[#e0e0e0] bg-white p-6 lg:col-span-10" aria-labelledby="chart-h">
          <h2 id="chart-h" className="text-base font-semibold">{heading}</h2>
          {!trend && !error && <p role="status" className="mt-4 text-text-secondary">Loading trend…</p>}
          {trend && trend.status === 'available' && (
            <>
              <TrendChart points={points} metricLabel={option.label} unit={option.unit} />
              <div className="mt-2 flex items-center gap-2">
                <span className="inline-block h-0.5 w-4 bg-[#6929c4]" />
                <span>{option.label}</span>
              </div>
              <div className="mt-4">
                <button
                  type="button"
                  aria-expanded={showTable}
                  aria-controls="trend-table"
                  onClick={() => setShowTable((s) => !s)}
                  className="inline-flex min-h-10 items-center border border-[#0f62fe] px-4 text-[#0f62fe]"
                >
                  {showTable ? 'Hide table view' : 'Show table view'}
                </button>
              </div>
              <div id="trend-table">
                {showTable && (
                  <TrendTable
                    points={points}
                    caption={`${option.label} readings, ${option.unit}`}
                    column={tableColumn}
                    label={`${option.label} values`}
                  />
                )}
              </div>
            </>
          )}
          {trend && trend.status === 'insufficient_history' && unavailable && points.length > 0 && (
            <TrendTable
              points={points}
              caption={`${option.label} readings, ${option.unit}`}
              column={tableColumn}
              label={`${option.label} values`}
            />
          )}
          {trend && trend.status === 'insufficient_history' && !(unavailable && points.length > 0) && (
            <div className="mt-4 border border-dashed border-[#8d8d8d] bg-white px-6 py-12 text-center" role="status">
              <p><strong>A reliable trend is not available yet.</strong></p>
              <p className="mt-2">We need more readings over this period. Keep syncing your devices.</p>
              <p className="mt-4">
                <Link to="/devices/sync" className="text-link underline">Check sync status</Link>
              </p>
            </div>
          )}
        </section>
        <div className="lg:col-span-6">
          <ExplanationTile
            text={tileText}
            loading={!explanation && !error}
            unavailable={unavailable}
            readingCount={explanation?.reading_count}
            sourceLabel={explanation?.source_label}
          />
        </div>
      </div>
    </section>
  );
}
