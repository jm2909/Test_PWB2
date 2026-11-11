import { Link } from 'react-router-dom';
import { Notice } from '../ui/Notice';
import { StatusBadge } from '../ui/StatusBadge';
import type { StatusKind } from '../ui/StatusBadge';
import { formatDateTime } from '../../lib/format';
import type { ConnectionItem } from '../../types/connection';

interface Props {
  item: ConnectionItem;
  onRefresh: () => void;
  onRetry: (item: ConnectionItem) => void;
  busy?: boolean;
}

const BADGE: Partial<Record<string, StatusKind>> = {
  current: 'current',
  pending: 'pending',
  stale: 'stale',
  failed: 'failed',
  disconnected: 'unavailable',
};

export function connectionTitle(item: ConnectionItem): string {
  return item.source === 'scale' ? `Sapphire Smart Scale – ${item.display_label}` : item.display_label;
}

function authorizationText(item: ConnectionItem): string {
  if (item.status === 'pending') return 'Waiting for your authorization to finish';
  if (item.status === 'failed') return 'Not completed';
  return 'Connected';
}

/** One connection with status (icon + text), source, last sync, authorization, notice and actions. */
export function ConnectionCard({ item, onRefresh, onRetry, busy }: Props) {
  const titleId = `conn-${item.id}`;
  const lastSync = item.last_successful_sync_at ? formatDateTime(item.last_successful_sync_at) : 'No successful sync yet';
  const badge = BADGE[item.status] ?? 'unavailable';
  return (
    <article className="border border-line-subtle bg-white p-4" aria-labelledby={titleId}>
      <header className="mb-3 flex flex-wrap justify-between gap-2">
        <h3 id={titleId} className="text-base font-semibold">
          {connectionTitle(item)}
        </h3>
        <strong className="font-semibold">
          <StatusBadge status={badge} />
        </strong>
      </header>
      <dl className="grid gap-x-4 gap-y-2 sm:grid-cols-[minmax(8rem,12rem)_1fr]">
        <dt className="text-ink-secondary">Source</dt>
        <dd>{item.source === 'scale' ? 'Sapphire scale' : 'Approved wearable'}</dd>
        <dt className="text-ink-secondary">Last successful sync</dt>
        <dd>{lastSync}</dd>
        <dt className="text-ink-secondary">Authorization</dt>
        <dd>{authorizationText(item)}</dd>
      </dl>
      {item.status === 'pending' && (
        <div className="mt-3">
          <Notice kind="info">
            <p>We are finishing the connection. Data from this source is not shown yet.</p>
          </Notice>
        </div>
      )}
      {item.status === 'stale' && (
        <div className="mt-3">
          <Notice kind="warning" role="status">
            <p>
              <strong>This source is out of date.</strong> Newer readings may be missing, so it is not shown as
              current on your dashboard.
            </p>
          </Notice>
        </div>
      )}
      {item.status === 'failed' && (
        <div className="mt-3">
          <Notice kind="error">
            <p>
              <strong>Connection could not be completed.</strong> Retry or contact support.
            </p>
            <p>Your account and other connections still work.</p>
          </Notice>
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {item.status === 'pending' && (
          <button type="button" className="btn btn-tertiary min-h-[2rem] px-3" onClick={onRefresh} disabled={busy}>
            Refresh status
          </button>
        )}
        {item.status === 'stale' && (
          <button type="button" className="btn min-h-[2rem] px-3" onClick={onRefresh} disabled={busy}>
            Retry sync
          </button>
        )}
        {item.status === 'failed' && (
          <button type="button" className="btn min-h-[2rem] px-3" onClick={() => onRetry(item)} disabled={busy}>
            Retry
          </button>
        )}
        {(item.status === 'stale' || item.status === 'failed') && (
          <Link
            className="btn btn-tertiary min-h-[2rem] px-3"
            to={`/support?context=device&id=${encodeURIComponent(item.id)}`}
          >
            Contact support
          </Link>
        )}
      </div>
    </article>
  );
}
