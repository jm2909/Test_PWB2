import type { DeviceConnection } from '../../types/device';
import { formatLastSync, providerName } from '../../types/sync';
import StateBadge from './StateBadge';

interface Props {
  connections: DeviceConnection[];
  busyId: string | null;
  onSync: (connection: DeviceConnection) => void;
}

function actionFor(c: DeviceConnection): { label: string; primary: boolean } | null {
  switch (c.status) {
    case 'connected':
      return { label: 'Sync now', primary: false };
    case 'failed':
      return { label: 'Retry', primary: true };
    case 'revoked':
      return { label: 'Reconnect', primary: true };
    case 'action_required':
      return { label: 'Review permissions', primary: false };
    default:
      return null;
  }
}

export default function SyncTable({ connections, busyId, onSync }: Props) {
  return (
    <div className="overflow-x-auto border border-border-subtle" role="region" aria-label="Sync status by connection" tabIndex={0}>
      <table className="w-full min-w-[760px] border-collapse">
        <caption className="bg-layer p-4 text-left font-semibold">Connections</caption>
        <thead>
          <tr className="bg-[#e0e0e0] text-left text-sm">
            <th scope="col" className="h-12 px-4 font-semibold">Connection</th>
            <th scope="col" className="h-12 px-4 font-semibold">State</th>
            <th scope="col" className="h-12 px-4 font-semibold">Last successful sync</th>
            <th scope="col" className="h-12 px-4 font-semibold">Reason</th>
            <th scope="col" className="h-12 px-4 font-semibold">Action</th>
          </tr>
        </thead>
        <tbody>
          {connections.map((c) => {
            const action = actionFor(c);
            const busy = busyId === c.id;
            return (
              <tr key={c.id} className="border-t border-border-subtle bg-white align-top">
                <th scope="row" className="px-4 py-3 text-left font-normal">{providerName(c.provider)}</th>
                <td className="px-4 py-3"><StateBadge status={busy ? 'pending' : c.status} /></td>
                <td className="px-4 py-3">{busy ? 'Syncing now' : formatLastSync(c.last_successful_sync_at)}</td>
                <td className="px-4 py-3">{c.failure_reason ?? 'None'}</td>
                <td className="px-4 py-3">
                  {action ? (
                    <button
                      type="button"
                      disabled={busyId !== null}
                      onClick={() => onSync(c)}
                      aria-label={`${action.label}: ${providerName(c.provider)}`}
                      className={`inline-flex min-h-8 items-center px-3 disabled:opacity-50 ${
                        action.primary ? 'bg-button-primary text-white' : 'border border-button-primary text-button-primary'
                      }`}
                    >
                      {action.label}
                    </button>
                  ) : (
                    'None'
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
