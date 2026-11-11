import { Link } from 'react-router-dom';
import { formatDateTime } from '../../lib/format';
import { ROUTES } from '../../routes';
import type { ConsentRecord } from '../../types/consent';
import { Icon } from '../ui/Icon';
import { Notice } from '../ui/Notice';

export function ConsentStatus({ record }: { record: ConsentRecord | null }) {
  const granted = record?.decision === 'granted' && record.collection_allowed;
  return (
    <div className="tile-white">
      <h2 className="!mb-3 text-xl">Consent status</h2>
      {!record && (
        <Notice kind="warning" title="No consent recorded." role="status">
          <p>
            Active consent is required before connecting a source. Connections and manual entry stay
            unavailable.
          </p>
        </Notice>
      )}
      {record && granted && (
        <Notice kind="success" role="status">
          <p>
            <strong>Consent granted</strong> for notice {record.notice_version}.
          </p>
          <p className="text-xs tracking-label text-ink-secondary">
            Recorded {formatDateTime(record.recorded_at)}
          </p>
          <p>
            You can now <Link to={ROUTES.connections}>connect a scale or wearable</Link>.
          </p>
        </Notice>
      )}
      {record && !granted && (
        <Notice kind="info" role="status">
          <p>
            <strong>Consent withdrawn.</strong> New nonessential collection has stopped.
          </p>
          <p className="text-xs tracking-label text-ink-secondary">
            Recorded {formatDateTime(record.recorded_at)}
          </p>
          <p>
            You can ask for an export or deletion in <a href="#rights-h">Your data rights</a> at any time.
          </p>
        </Notice>
      )}
      <p className="my-4 text-xs tracking-label text-ink-helper">Collection gate</p>
      <ul className="m-0 list-none space-y-3 pl-4">
        <li>
          <span className="inline-flex items-center gap-2">
            <Icon name={granted ? 'ok' : 'off'} className={granted ? 'text-success' : 'text-ink-helper'} />
            <span>
              {granted
                ? 'Connect scale or wearable: available'
                : 'Connect scale or wearable: unavailable until consent is granted'}
            </span>
          </span>
        </li>
        <li>
          <span className="inline-flex items-center gap-2">
            <Icon name={granted ? 'ok' : 'off'} className={granted ? 'text-success' : 'text-ink-helper'} />
            <span>
              {granted ? 'Manual entry: available' : 'Manual entry: unavailable until consent is granted'}
            </span>
          </span>
        </li>
      </ul>
    </div>
  );
}
