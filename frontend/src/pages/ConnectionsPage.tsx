import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ConnectionCard } from '../components/connections/ConnectionCard';
import { ScaleConnectForm } from '../components/connections/ScaleConnectForm';
import { WearableConnectForm } from '../components/connections/WearableConnectForm';
import { Notice } from '../components/ui/Notice';
import {
  beginWearableAuthorization,
  completeWearableAuthorization,
  getCurrentConsent,
  listConnections,
  listWearableProviders,
} from '../lib/api-client';
import { ApiError } from '../types/api';
import type { ConnectionItem, WearableProvider } from '../types/connection';

export function ConnectionsPage() {
  const [items, setItems] = useState<ConnectionItem[]>([]);
  const [providers, setProviders] = useState<WearableProvider[]>([]);
  const [consentOk, setConsentOk] = useState<boolean | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const reload = useCallback(async () => {
    try {
      const page = await listConnections();
      setItems(page.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Connections could not be loaded. Try again.');
    }
  }, []);

  useEffect(() => {
    let active = true;
    Promise.all([getCurrentConsent(), listWearableProviders(), listConnections()])
      .then(([consent, list, page]) => {
        if (!active) return;
        setConsentOk(consent?.collection_allowed === true);
        setProviders(list);
        setItems(page.items);
        setLoaded(true);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof ApiError ? err.detail : 'This page could not be loaded. Try again.');
        setLoaded(true);
      });
    return () => {
      active = false;
    };
  }, []);

  const refresh = async () => {
    setBusy(true);
    await reload();
    setBusy(false);
  };

  const retry = async (item: ConnectionItem) => {
    setBusy(true);
    try {
      if (item.source === 'wearable' && item.provider) {
        const started = await beginWearableAuthorization(item.provider);
        const state = new URL(started.authorization_url, window.location.origin).searchParams.get('state') ?? '';
        await completeWearableAuthorization(item.provider, {
          connection_id: started.connection_id,
          state,
          code: 'granted',
        });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'The retry could not be completed.');
    }
    await reload();
    setBusy(false);
  };

  const blocked = consentOk !== true;

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Account settings</p>
          <h1 id="page-title">Device connections</h1>
          <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
            Connect your Sapphire scale and an approved wearable so your readings appear in one place. We show when a
            connection is current, waiting, out of date, or needs attention.
          </p>
        </div>
      </section>

      {!loaded && (
        <div className="page-grid mt-8" role="status">
          Loading your connections…
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
          <section className="mt-8" aria-labelledby="gate-h">
            <h2 className="sr-only" id="gate-h">
              Consent status for connections
            </h2>
            <div className="page-grid">
              {blocked ? (
                <Notice kind="warning" role="status">
                  <p>
                    <strong>Active consent is required before connecting a source.</strong>
                  </p>
                  <p>
                    Connect buttons are unavailable until you agree to the privacy notice.{' '}
                    <Link to="/consent">Review privacy consent</Link>
                  </p>
                </Notice>
              ) : (
                <Notice kind="success" role="status">
                  <p>Consent is active. You can connect a source.</p>
                </Notice>
              )}
            </div>
          </section>

          <section className="mt-8" aria-label="Connect a source">
            <div className="page-grid grid gap-8 lg:grid-cols-2">
              <ScaleConnectForm
                disabled={blocked}
                connectedLabels={items.filter((i) => i.source === 'scale').map((i) => i.display_label)}
                onConnected={reload}
              />
              <WearableConnectForm providers={providers} disabled={blocked} onFinished={reload} />
            </div>
          </section>

          <section className="mt-8" aria-labelledby="list-h">
            <div className="page-grid">
              <h2 id="list-h" className="mb-4 text-xl">
                Your connections and sync status
              </h2>
              <p className="mb-4 text-xs text-ink-secondary">
                Status is never shown as current unless the last sync succeeded recently. Times are shown in your
                local time.
              </p>
              {items.length === 0 ? (
                <Notice kind="info">
                  <p>No sources are connected yet. Connect a scale or wearable above.</p>
                </Notice>
              ) : (
                <div className="space-y-4">
                  {items.map((item) => (
                    <ConnectionCard key={item.id} item={item} onRefresh={refresh} onRetry={retry} busy={busy} />
                  ))}
                </div>
              )}
            </div>
          </section>
        </>
      )}
    </>
  );
}
