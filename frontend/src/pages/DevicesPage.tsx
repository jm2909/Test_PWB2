import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Notification from '../components/common/Notification';
import ScaleCard from '../components/devices/ScaleCard';
import WearableList from '../components/devices/WearableList';
import { ApiError, api } from '../lib/api-client';
import type { ConsentListResponse, DeviceConnection, ListResponse } from '../types';

export default function DevicesPage() {
  const [connections, setConnections] = useState<DeviceConnection[]>([]);
  const [paused, setPaused] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [scaleFailed, setScaleFailed] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [list, consents] = await Promise.all([
        api.get<ListResponse<DeviceConnection>>('/device-connections'),
        api.get<ConsentListResponse>('/consents'),
      ]);
      setConnections(list.items);
      const device = consents.latest.find((c) => c.purpose === 'device_processing');
      setPaused(device?.status === 'declined');
    } catch (e) {
      setLoadError(e instanceof ApiError ? e.message : 'Devices could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const connect = async (provider: string, mode: 'pair' | 'authorize') => {
    setBusy(provider);
    setActionError(null);
    if (provider === 'sapphire_scale') setScaleFailed(false);
    try {
      const saved = await api.post<DeviceConnection>('/device-connections', {
        provider,
        connection_mode: mode,
      });
      setConnections((prev) => [...prev.filter((c) => c.provider !== provider), saved]);
      if (provider === 'sapphire_scale') setScaleFailed(saved.status !== 'connected');
    } catch (e) {
      if (e instanceof ApiError && e.status === 403) setPaused(true);
      else if (provider === 'sapphire_scale') setScaleFailed(true);
      else setActionError(e instanceof ApiError ? e.message : 'The device could not be connected.');
    } finally {
      setBusy(null);
    }
  };

  return (
    <section aria-labelledby="devices-h">
      <h1 id="devices-h" className="text-[2rem] leading-10">Devices</h1>
      <p className="mt-2 max-w-3xl text-base text-text-secondary">
        Connect your Sapphire smart scale and the wearable you already use. FitConnect only reads the data
        categories you allow.
      </p>

      {paused && (
        <Notification kind="warning" title="Device connection is paused" className="mt-6">
          <p>
            Device connection is paused because you declined device processing.{' '}
            <Link to="/onboarding" className="text-link underline">Review consent</Link>.
          </p>
        </Notification>
      )}
      {loadError && (
        <Notification kind="error" title="Devices not loaded" role="alert" className="mt-6">
          <p>{loadError}</p>
          <button type="button" onClick={() => void load()} className="mt-2 text-link underline">
            Retry
          </button>
        </Notification>
      )}
      {actionError && (
        <Notification kind="error" title="Device not connected" role="alert" className="mt-6">
          <p>{actionError}</p>
        </Notification>
      )}

      {loading ? (
        <p role="status" className="mt-8 text-text-secondary">Loading devices…</p>
      ) : (
        !loadError && (
          <div className="mt-8 grid gap-6 lg:grid-cols-16">
            <ScaleCard
              connection={connections.find((c) => c.provider === 'sapphire_scale')}
              failed={scaleFailed}
              busy={busy === 'sapphire_scale'}
              paused={paused}
              onPair={() => void connect('sapphire_scale', 'pair')}
            />
            <WearableList
              connections={connections}
              busyProvider={busy}
              paused={paused}
              onAuthorize={(p) => void connect(p, 'authorize')}
            />
          </div>
        )
      )}
    </section>
  );
}
