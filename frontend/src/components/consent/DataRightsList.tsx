import { Link } from 'react-router-dom';
import { ROUTES } from '../../routes';
import type { DataRightsRequest } from '../../types/dataRights';
import { formatDateTime } from '../../lib/format';
import { StatusBadge } from '../ui/StatusBadge';
import type { StatusKind } from '../ui/StatusBadge';
import { statusLabel, TYPE_LABEL } from './DataRightsForm';

function badgeKind(status: string): StatusKind {
  if (status === 'fulfilled' || status === 'completed') return 'current';
  if (status === 'rejected') return 'failed';
  return 'pending';
}

export function DataRightsList({ items }: { items: DataRightsRequest[] }) {
  return (
    <div className="tile-white">
      <h2 id="hist-h" className="!mb-3 text-xl">
        Your requests
      </h2>
      {items.length === 0 ? (
        <p>You have not made any data-rights requests yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[30rem] border-collapse" aria-labelledby="hist-h">
            <thead>
              <tr className="bg-surface-selected text-left">
                <th scope="col" className="px-4 py-3 font-semibold">Reference</th>
                <th scope="col" className="px-4 py-3 font-semibold">Type</th>
                <th scope="col" className="px-4 py-3 font-semibold">Status</th>
                <th scope="col" className="px-4 py-3 font-semibold">Requested</th>
                <th scope="col" className="px-4 py-3 font-semibold">Due by</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id} className="border-b border-line">
                  <td className="px-4 py-3 align-top">{r.reference}</td>
                  <td className="px-4 py-3 align-top">{TYPE_LABEL[r.request_type]}</td>
                  <td className="px-4 py-3 align-top">
                    <StatusBadge status={badgeKind(r.status)} label={statusLabel(r.status)} />
                  </td>
                  <td className="px-4 py-3 align-top">{formatDateTime(r.requested_at)}</td>
                  <td className="px-4 py-3 align-top">{formatDateTime(r.fulfillment_due_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="field-help">
        Rejected requests include a reason in the request details. Questions about a request?{' '}
        <Link to={ROUTES.support}>Contact support</Link> and quote the reference.
      </p>
    </div>
  );
}
