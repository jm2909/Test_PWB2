import { useCallback, useEffect, useState } from 'react';
import AlertCard from '../components/insights/AlertCard';
import InsightCard from '../components/insights/InsightCard';
import RecommendationCard from '../components/insights/RecommendationCard';
import Notification from '../components/common/Notification';
import { ApiError, api } from '../lib/api-client';
import type { Alert } from '../types/alert';
import type { Insight, Recommendation } from '../types/insight';
import type { ListResponse } from '../types';

export default function InsightsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [insight, setInsight] = useState<Insight | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [a, i, r] = await Promise.all([
        api.get<ListResponse<Alert>>('/alerts'),
        api.get<ListResponse<Insight>>('/insights?limit=1'),
        api.get<Recommendation>('/recommendations'),
      ]);
      setAlerts(a.items);
      setInsight(i.items[0] ?? null);
      setRecommendation(r);
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Your insights could not be loaded.');
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function generate() {
    setGenerating(true);
    setGenerateError(null);
    try {
      await api.post<Insight>('/insights');
      await load();
    } catch (e) {
      setGenerateError(e instanceof ApiError ? e.message : 'We could not generate an insight right now.');
    } finally {
      setGenerating(false);
    }
  }

  const sectionHead = 'mb-2 border-b border-[#e0e0e0] pb-2 text-xl';
  return (
    <section aria-labelledby="ins-page-h">
      <h1 id="ins-page-h" className="text-[2rem] leading-10">Insights and alerts</h1>
      <p className="mt-2 max-w-3xl text-base text-text-secondary">
        What your recent readings show, why it matters for everyday wellness, and one step you could take.
      </p>
      {error && (
        <Notification kind="error" title="Insights not loaded" role="alert" className="mt-6">
          <p>{error}</p>
        </Notification>
      )}
      {!loaded && <p role="status" className="mt-6 text-text-secondary">Loading insights…</p>}
      <div className="mt-8 grid gap-8 lg:grid-cols-16">
        <div className="lg:col-span-10">
          <section aria-labelledby="alert-h">
            <h2 id="alert-h" className={sectionHead}>Alert</h2>
            <div className="mt-3 space-y-4">
              {loaded && alerts.length === 0 && !error && (
                <div className="bg-layer p-4" role="status">
                  <p>No alerts right now. We will let you know if a trend is worth noticing.</p>
                </div>
              )}
              {alerts.map((a) => (
                <AlertCard key={a.id} alert={a} />
              ))}
            </div>
          </section>

          <section className="mt-10" aria-labelledby="ins-h">
            <h2 id="ins-h" className={sectionHead}>Insight</h2>
            <div className="mt-3">{loaded && <InsightCard insight={insight} />}</div>
            <div className="mt-4">
              <button
                type="button"
                onClick={() => void generate()}
                disabled={generating}
                className="inline-flex min-h-10 items-center border border-[#0f62fe] px-4 text-[#0f62fe] disabled:opacity-50"
              >
                {generating ? 'Generating…' : 'Generate insight'}
              </button>
            </div>
            {generateError && (
              <Notification kind="error" title="Insight not generated" role="alert" className="mt-3">
                <p>{generateError}</p>
              </Notification>
            )}
          </section>

          <section className="mt-10" aria-labelledby="rec-h">
            <h2 id="rec-h" className={sectionHead}>Recommended next action</h2>
            <div className="mt-3">{loaded && <RecommendationCard recommendation={recommendation} />}</div>
          </section>
        </div>

        <aside className="lg:col-span-6" aria-labelledby="ctx-h">
          <div className="bg-layer p-4">
            <h2 id="ctx-h" className="text-base font-semibold">How to read this page</h2>
            <ul className="mt-3">
              <li className="border-t border-[#e0e0e0] py-2"><strong>Alert:</strong> a trend worth noticing, with its urgency and a next step.</li>
              <li className="border-t border-[#e0e0e0] py-2"><strong>Insight:</strong> what changed and what it can mean for daily wellness.</li>
              <li className="border-t border-[#e0e0e0] py-2"><strong>Next action:</strong> one practical step, or none if your data does not support one.</li>
            </ul>
            <p className="mt-3 text-xs text-[#6f6f6f]">
              Alerts and insights describe trends in your own readings. They are not a diagnosis.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}
