import { useEffect, useState } from 'react';
import { AlertSummary } from '../components/dashboard/AlertSummary';
import { DashboardInsight } from '../components/dashboard/DashboardInsight';
import { GoalProgressList } from '../components/dashboard/GoalProgressList';
import { MeasurementTile, METRIC_LABELS } from '../components/dashboard/MeasurementTile';
import { SourceStatusList } from '../components/dashboard/SourceStatusList';
import { Notice } from '../components/ui/Notice';
import { getDashboard, listAlerts } from '../lib/api-client';
import { useAuth } from '../lib/auth-context';
import { ApiError } from '../types/api';
import type { DashboardAlert, DashboardData } from '../types/dashboard';

const METRICS = ['weight', 'steps', 'sleep_duration', 'active_minutes'] as const;

export function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [alerts, setAlerts] = useState<DashboardAlert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [simplified, setSimplified] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const dash = await getDashboard();
        let merged: DashboardAlert[] = dash.alerts;
        try {
          // The dashboard carries active alerts only; the alerts list adds acknowledged ones.
          merged = (await listAlerts()).items;
        } catch {
          merged = dash.alerts;
        }
        if (cancelled) return;
        setData(dash);
        setAlerts([...merged].sort((a, b) => Number(a.state === 'acknowledged') - Number(b.state === 'acknowledged')));
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.detail : 'The dashboard could not be loaded. Try again.');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const unavailable = data
    ? METRICS.filter((m) => !data.measurements.some((x) => x.metric_type === m)).map((m) => METRIC_LABELS[m])
    : [];
  const insight = data ? (data.insights.find((i) => i.metric_type === 'steps') ?? data.insights[0]) : undefined;

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Your own data only · Signed in as {user?.display_name}</p>
          <h1 id="page-title">Your wellness dashboard</h1>
          {!simplified && (
            <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
              Your latest readings, how each source is doing, any alerts, and your goals in one place. Where data is
              missing, we say so instead of guessing.
            </p>
          )}
          <p className="mt-4">
            <button
              type="button"
              className="btn btn-tertiary"
              aria-pressed={simplified}
              onClick={() => setSimplified((s) => !s)}
            >
              Simplified view
            </button>
          </p>
        </div>
      </section>

      {error && (
        <div className="page-grid mt-8">
          <Notice kind="error">
            <p>{error}</p>
          </Notice>
        </div>
      )}
      {!data && !error && (
        <div className="page-grid mt-8" role="status">
          Loading your dashboard…
        </div>
      )}

      {data && (
        <>
          <section className="mt-8" aria-labelledby="read-h">
            <div className="page-grid">
              <h2 id="read-h">Latest readings</h2>
              <ul className="grid list-none gap-4 p-0 sm:grid-cols-2 xl:grid-cols-4">
                {METRICS.map((m) => (
                  <li key={m}>
                    <MeasurementTile
                      metric={m}
                      measurement={data.measurements.find((x) => x.metric_type === m)}
                      simplified={simplified}
                    />
                  </li>
                ))}
              </ul>
              {unavailable.length > 0 && (
                <p className="mt-3 text-xs tracking-label text-ink-secondary">
                  Unavailable categories: {unavailable.join(', ')}. Only readings that passed our checks are shown.
                </p>
              )}
            </div>
          </section>

          <section className="mt-8" aria-label="Source status and alerts">
            <div className="page-grid grid gap-8 lg:grid-cols-2">
              <SourceStatusList items={data.source_statuses} />
              <AlertSummary alerts={alerts} />
            </div>
          </section>

          {!simplified && (
            <section className="mt-8" aria-label="Goals and insight">
              <div className="page-grid grid gap-8 lg:grid-cols-2">
                <GoalProgressList goals={data.goals} />
                <DashboardInsight insight={insight} />
              </div>
            </section>
          )}
        </>
      )}
    </>
  );
}
