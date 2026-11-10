import { Link } from 'react-router-dom';
import { WEARABLES, categoryLabel } from '../../types/device';
import type { DeviceConnection } from '../../types/device';
import CategoryChips from './CategoryChips';

interface Props {
  connections: DeviceConnection[];
  busyProvider: string | null;
  paused: boolean;
  onAuthorize: (provider: string) => void;
}

const ICON_OK = 'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z';
const ICON_ERR = 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z';
const ICON_INFO = 'M8.5,11 L8.5,6.5 L6.5,6.5 L6.5,7.5 L7.5,7.5 L7.5,11 L6,11 L6,12 L10,12 L10,11 Z M8,3.5 a0.8,0.8 0 1 0 0.01,0 Z M8,15 c-3.9,0 -7,-3.1 -7,-7 s3.1,-7 7,-7 s7,3.1 7,7 S11.9,15 8,15 Z M8,2 C4.7,2 2,4.7 2,8 s2.7,6 6,6 s6,-2.7 6,-6 S11.3,2 8,2 Z';

function StatusLine({ kind, label }: { kind: 'ok' | 'err' | 'info'; label: string }) {
  const fill = kind === 'ok' ? 'fill-support-success' : kind === 'err' ? 'fill-support-error' : 'fill-support-info';
  const path = kind === 'ok' ? ICON_OK : kind === 'err' ? ICON_ERR : ICON_INFO;
  return (
    <p className="mt-1 flex items-center gap-2">
      <svg width="16" height="16" viewBox="0 0 16 16" className={fill} aria-hidden="true">
        <path d={path} />
      </svg>
      {label}
    </p>
  );
}

export default function WearableList({ connections, busyProvider, paused, onAuthorize }: Props) {
  return (
    <section className="bg-layer p-6 lg:col-span-8" aria-labelledby="wear-h">
      <h2 id="wear-h" className="text-xl">Wearables</h2>
      <p className="mt-1 text-sm text-text-secondary">Each provider is connected separately. You choose what it can share.</p>
      <ul className="mt-4 divide-y divide-border-subtle">
        {WEARABLES.map((w) => {
          const conn = connections.find((c) => c.provider === w.provider);
          const status = conn?.status ?? 'not_connected';
          const busy = busyProvider === w.provider;
          let action: { label: string; variant: 'primary' | 'secondary' } | null = null;
          let body;
          if (status === 'connected') {
            body = (
              <>
                <StatusLine kind="ok" label="Connected" />
                <CategoryChips categories={conn?.permitted_categories ?? []} />
              </>
            );
          } else if (status === 'revoked') {
            body = (
              <>
                <StatusLine kind="err" label="Revoked" />
                <p className="mt-1 text-sm text-text-secondary">Access was revoked. Reconnect to continue syncing.</p>
              </>
            );
            action = { label: 'Reconnect', variant: 'primary' };
          } else if (conn) {
            body = (
              <>
                <StatusLine kind="err" label={status === 'failed' ? 'Connection failed' : 'Action required'} />
                {conn.failure_reason && <p className="mt-1 text-sm text-text-secondary">{conn.failure_reason}</p>}
              </>
            );
            action = { label: conn.recovery_action ?? 'Try again', variant: 'primary' };
          } else {
            body = (
              <>
                <StatusLine kind="info" label="Not connected" />
                <p className="mt-1 text-sm text-text-secondary">
                  Before you authorize, you will see this list: {w.categories.map(categoryLabel).join(', ')}.
                </p>
              </>
            );
            action = { label: 'Connect', variant: 'secondary' };
          }
          return (
            <li key={w.provider} className="flex flex-wrap items-start justify-between gap-4 py-4">
              <div>
                <p className="font-semibold">{w.name}</p>
                {body}
              </div>
              {status === 'connected' ? (
                <Link to="/devices/sync" className="inline-flex min-h-10 items-center px-4 text-link">
                  View sync status
                </Link>
              ) : (
                action && (
                  <button
                    type="button"
                    onClick={() => onAuthorize(w.provider)}
                    disabled={busy || paused}
                    className={`inline-flex min-h-10 items-center px-4 disabled:opacity-50 ${
                      action.variant === 'primary'
                        ? 'bg-button-primary text-white'
                        : 'border border-link text-link'
                    }`}
                  >
                    {action.label}
                  </button>
                )
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
