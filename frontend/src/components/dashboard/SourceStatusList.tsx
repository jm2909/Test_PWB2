import { Link } from 'react-router-dom';
import { formatDateTime } from '../../lib/format';
import type { DashboardSourceStatus } from '../../types/dashboard';
import { StatusBadge } from '../ui/StatusBadge';
import type { StatusKind } from '../ui/StatusBadge';

const BADGE: Record<string, StatusKind> = {
  current: 'current',
  stale: 'stale',
  failed: 'failed',
  pending: 'pending',
};

export function sourceName(item: DashboardSourceStatus): string {
  return item.source === 'scale' ? `Sapphire Smart Scale – ${item.display_label}` : item.display_label;
}

/** Source status table: badge, last successful sync and a recovery link for anything not current. */
export function SourceStatusList({ items }: { items: DashboardSourceStatus[] }) {
  const visible = items.filter((i) => i.status !== 'disconnected');
  return (
    <div className="tile-white">
      <h2 id="src-h">Source status</h2>
      {visible.length === 0 ? (
        <p>No sources are connected yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[26rem] border-collapse text-left" aria-labelledby="src-h">
            <thead>
              <tr className="bg-surface-selected">
                <th scope="col" className="px-4 py-3">Source</th>
                <th scope="col" className="px-4 py-3">Status</th>
                <th scope="col" className="px-4 py-3">Last successful sync</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((item) => (
                <tr key={item.id} className="border-b border-line-subtle align-top">
                  <th scope="row" className="px-4 py-3 font-normal">{sourceName(item)}</th>
                  <td className="px-4 py-3">
                    <StatusBadge status={BADGE[item.status] ?? 'unavailable'} />
                    {item.status !== 'current' && (
                      <p className="mt-1">
                        <Link to="/connections">Review connection</Link>
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {item.last_successful_sync_at ? formatDateTime(item.last_successful_sync_at) : 'No successful sync yet'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="mt-4 text-xs tracking-label text-ink-secondary">
        A source that is stale, failed, or missing is never shown as current. <Link to="/connections">Fix connections</Link>
      </p>
    </div>
  );
}
