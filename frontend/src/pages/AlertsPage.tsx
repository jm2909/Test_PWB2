import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCard } from '../components/alerts/AlertCard';
import { Notice } from '../components/ui/Notice';
import { acknowledgeAlert, listAlerts } from '../lib/api-client';
import { formatDateTime } from '../lib/format';
import { ApiError } from '../types/api';
import type { WellnessAlert } from '../types/alert';

export function AlertsPage() {
  const [alerts, setAlerts] = useState<WellnessAlert[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const page = await listAlerts();
      setAlerts(page.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Alerts could not be loaded. Try again.');
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const acknowledge = async (alert: WellnessAlert) => {
    setBusy(true);
    setSavedAt(null);
    try {
      const updated = await acknowledgeAlert(alert.id);
      setSavedAt(updated.acknowledged_at);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'The alert could not be acknowledged. Try again.');
    } finally {
      setBusy(false);
    }
  };

  const active = alerts.filter((a) => a.state === 'active');
  const acknowledged = alerts
    .filter((a) => a.state === 'acknowledged')
    .sort((a, b) => String(b.acknowledged_at).localeCompare(String(a.acknowledged_at)));

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Your own data only</p>
          <h1 id="page-title">Alerts</h1>
          <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
            Alerts point out patterns in your own readings that may be worth a look. They are general wellness
            notices, not medical findings.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="bound-h">
        <h2 className="sr-only" id="bound-h">
          Wellness boundary
        </h2>
        <div className="page-grid">
          <Notice kind="info">
            <p>
              <strong>About these alerts.</strong> Sapphire FitConnect supports general wellness. An alert does not
              diagnose a condition or tell you what to do about your health. If something worries you, or you feel
              unwell, speak to a qualified health professional. In an emergency, contact your local emergency
              services.
            </p>
          </Notice>
        </div>
      </section>

      {!loaded && (
        <div className="page-grid mt-8" role="status">
          Loading your alerts…
        </div>
      )}
      {error && (
        <div className="page-grid mt-8">
          <Notice kind="error">
            <p>{error}</p>
          </Notice>
        </div>
      )}

      {loaded && (
        <>
          <section className="mt-8" aria-labelledby="act-h">
            <div className="page-grid grid gap-8 lg:grid-cols-[3fr_2fr]">
              <div>
                <h2 id="act-h">Active alerts</h2>
                {savedAt && (
                  <div className="mb-4">
                    <Notice kind="success" role="status">
                      <p>
                        <strong>Alert acknowledged.</strong> Recorded {formatDateTime(savedAt)}. It moves to your
                        acknowledged alerts and stays in your history. Acknowledging again has no further effect.
                      </p>
                    </Notice>
                  </div>
                )}
                {active.map((a) => (
                  <AlertCard key={a.id} alert={a} onAcknowledge={acknowledge} busy={busy} />
                ))}
              </div>
              <div>
                <div className="tile-white">
                  <h2>When no alerts are active</h2>
                  {active.length === 0 && (
                    <Notice kind="info" role="status">
                      <p>
                        No active alerts right now. This only reflects data we have received; if a source is out of
                        date, new patterns may not show yet.
                      </p>
                    </Notice>
                  )}
                  <p className="mt-4">
                    <Link to="/connections">Check source status</Link>
                  </p>
                  <p className="field-help mt-4">Duplicate prevention</p>
                  <p className="text-xs tracking-label text-ink-secondary">
                    The same event under the same rule version creates only one active alert.
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-8" aria-labelledby="ack-h">
            <div className="page-grid grid gap-8 lg:grid-cols-[3fr_2fr]">
              <div>
                <h2 id="ack-h">Acknowledged alerts and history</h2>
                <p className="mb-4 text-xs tracking-label text-ink-secondary">
                  Acknowledged alerts stay in your history so you can look back at them.
                </p>
                {acknowledged.length === 0 && <p>No acknowledged alerts yet.</p>}
                {acknowledged.map((a) => (
                  <AlertCard key={a.id} alert={a} />
                ))}
              </div>
              <div>
                <div className="tile">
                  <h2>Need help?</h2>
                  <p>
                    If an alert looks wrong, or you cannot tell why you received it, our support team can look into
                    it. Please do not include health readings in your message.
                  </p>
                  <p className="mt-4">
                    <Link className="btn" to="/support?context=alert&id=">
                      Contact support
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </>
  );
}
