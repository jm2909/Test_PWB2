import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Notification from '../components/common/Notification';
import SyncAddedPanel from '../components/sync/SyncAddedPanel';
import SyncTable from '../components/sync/SyncTable';
import { StateKey } from '../components/sync/StateBadge';
import { ApiError, api } from '../lib/api-client';
import type { DeviceConnection, ListResponse } from '../types';
import { formatLastSync, providerName } from '../types/sync';

function newKey(): string {
  const id = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `sync-${id}`;
}

function clock(d: Date): string {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

export default function SyncStatusPage() {
  const [connections, setConnections] = useState<DeviceConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [result, setResult] = useState<DeviceConnection | null>(null);
  const [resultAt, setResultAt] = useState<Date | null>(null);
  const [checked, setChecked] = useState<Date>(new Date());

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const list = await api.get<ListResponse<DeviceConnection>>('/device-connections');
      setConnections(list.items);
      setChecked(new Date());
    } catch (e) {
      setLoadError(e instanceof ApiError ? e.message : 'Sync status could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const sync = async (c: DeviceConnection) => {
    setBusyId(c.id);
    setActionError(null);
    setResult(null);
    try {
      const updated = await api.post<DeviceConnection>(
        '/sync',
        { device_connection_id: c.id },
        { 'Idempotency-Key': newKey() },
      );
      setConnections((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));
      setResult(updated);
      setResultAt(new Date());
      setChecked(new Date());
    } catch (e) {
      setActionError(e instanceof ApiError ? e.message : 'The sync could not be started.');
    } finally {
      setBusyId(null);
    }
  };

  const failed = connections.filter((c) => c.status === 'failed' || c.status === 'revoked');
  const summary = result?.last_sync_summary ?? null;

  return (
    <section aria-labelledby="sync-h">
      <nav aria-label="Breadcrumb" className="mb-2 text-xs text-text-helper">
        <Link to="/devices" className="text-link">Devices</Link> / <span aria-current="page">Sync status</span>
      </nav>
      <h1 id="sync-h" className="text-[2rem] leading-10">Sync status</h1>
      <p className="mt-2 max-w-3xl text-base text-text-secondary">
        See when each connection last synced, why one needs attention, and what to do next. Last checked today at{' '}
        {clock(checked)}.
      </p>

      {loading && <p role="status" className="mt-8 text-text-secondary">Loading sync status…</p>}
      {loadError && (
        <Notification kind="error" role="alert" title="Sync status unavailable" className="mt-8">
          <p>{loadError}</p>
          <button type="button" onClick={() => void load()} className="text-link underline">Try again</button>
        </Notification>
      )}

      {!loading && !loadError && (
        <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-16">
          <div className="lg:col-span-10">
            <SyncTable connections={connections} busyId={busyId} onSync={(c) => void sync(c)} />
            <StateKey />
            <p className="mt-2 text-xs text-text-helper">
              Failed or revoked connections are never shown as up to date. Their last successful sync time stays
              visible so you can see how old the data is.
            </p>

            {failed.map((c) => (
              <Notification key={c.id} kind="error" role="alert" title={`Sync failed for ${providerName(c.provider)}`} className="mt-6">
                <p>
                  {c.failure_reason ?? 'The connection needs attention.'} Your last successful sync was{' '}
                  {c.last_successful_sync_at ? formatLastSync(c.last_successful_sync_at).toLowerCase() : 'never'}, so newer
                  readings are not included yet.
                </p>
              </Notification>
            ))}

            {actionError && (
              <Notification kind="error" role="alert" title="Sync could not run" className="mt-6">
                <p>{actionError}</p>
              </Notification>
            )}
            {result && result.status === 'connected' && (
              <Notification kind="success" title="Sync complete" className="mt-6">
                <p>Sync complete. {summary?.new_readings ?? 0} new readings added.</p>
              </Notification>
            )}
            {result && result.status !== 'connected' && (
              <Notification kind="warning" role="alert" title={`${providerName(result.provider)} still needs attention`} className="mt-6">
                <p>
                  {result.failure_reason ?? 'The sync did not finish.'}
                  {result.recovery_action ? ` Next step: ${result.recovery_action}.` : ''}
                </p>
              </Notification>
            )}
          </div>
          <div className="lg:col-span-6">
            <SyncAddedPanel summary={summary} at={resultAt} />
          </div>
        </div>
      )}
    </section>
  );
}
