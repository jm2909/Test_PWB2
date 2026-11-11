import { Link } from 'react-router-dom';
import { formatDateTime } from '../../lib/format';
import type { DashboardAlert } from '../../types/dashboard';
import { alertTitle } from '../alerts/AlertCard';
import { StatusBadge } from '../ui/StatusBadge';

/** Active and acknowledged alerts, visibly distinct, each linking to /alerts. */
export function AlertSummary({ alerts }: { alerts: DashboardAlert[] }) {
  return (
    <div className="tile">
      <h2 id="al-h">Alerts</h2>
      <p className="mb-3 text-xs tracking-label text-ink-secondary">
        General wellness notices about your own readings. They are not medical advice.
      </p>
      {alerts.length === 0 && <p>No alerts right now.</p>}
      <ul className="list-none p-0">
        {alerts.map((a) => {
          const acknowledged = a.state === 'acknowledged';
          return (
            <li
              key={a.id}
              data-state={acknowledged ? 'acknowledged' : 'active'}
              className={`mb-3 border border-l-4 border-line-subtle px-4 py-3 ${
                acknowledged ? 'border-l-line-strong bg-surface' : 'border-l-warn-icon bg-white'
              }`}
            >
              <p className="flex flex-wrap items-center gap-2">
                <strong className="font-semibold">
                  <StatusBadge status={acknowledged ? 'acknowledged' : 'active'} />
                </strong>
                <span>· {alertTitle(a.metric_type)}</span>
              </p>
              <p className="mt-1 text-xs tracking-label text-ink-secondary">
                Event time: {formatDateTime(a.event_at)}
                {acknowledged && ` · Acknowledged ${formatDateTime(a.acknowledged_at)}`}
              </p>
              <p className="mt-1">
                <Link to="/alerts">{acknowledged ? 'View in history' : 'View details and acknowledge'}</Link>
              </p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
