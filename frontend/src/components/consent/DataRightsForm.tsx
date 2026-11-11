import { useState } from 'react';
import type { FormEvent } from 'react';
import { createDataRightsRequest } from '../../lib/api-client';
import { formatDateTime } from '../../lib/format';
import { ApiError } from '../../types/api';
import type { DataRightsRequest, DataRightsType } from '../../types/dataRights';
import { Notice } from '../ui/Notice';

export const TYPE_LABEL: Record<DataRightsType, string> = { export: 'Export', deletion: 'Deletion' };

interface Props {
  onCreated: (request: DataRightsRequest) => void;
}

export function DataRightsForm({ onCreated }: Props) {
  const [type, setType] = useState<DataRightsType>('export');
  const [submitted, setSubmitted] = useState<DataRightsRequest | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitted(null);
    setBusy(true);
    try {
      const created = await createDataRightsRequest({ request_type: type });
      setSubmitted(created);
      onCreated(created);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Your request could not be submitted. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="tile">
      <h2 id="rights-h" className="!mb-3 text-xl">
        Your data rights
      </h2>
      <p className="mb-4 text-xs tracking-label text-ink-secondary">
        Available in Account settings, including after you withdraw consent.
      </p>
      <form noValidate aria-labelledby="rights-h" onSubmit={onSubmit}>
        <fieldset className="mb-6 min-w-0 border-0 p-0">
          <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">Request type</legend>
          <div className="mb-3 flex items-start gap-2">
            <input
              className="mt-0.5 h-4 w-4 flex-none"
              type="radio"
              name="rtype"
              id="r-export"
              checked={type === 'export'}
              onChange={() => setType('export')}
            />
            <label htmlFor="r-export" className="cursor-pointer">
              Export my data
              <span className="block text-xs tracking-label text-ink-secondary">
                A copy of the information held in your account.
              </span>
            </label>
          </div>
          <div className="mb-3 flex items-start gap-2">
            <input
              className="mt-0.5 h-4 w-4 flex-none"
              type="radio"
              name="rtype"
              id="r-delete"
              checked={type === 'deletion'}
              onChange={() => setType('deletion')}
            />
            <label htmlFor="r-delete" className="cursor-pointer">
              Delete my data
              <span className="block text-xs tracking-label text-ink-secondary">
                Asks for your account data to be deleted. This request is reviewed before it is completed.
              </span>
            </label>
          </div>
        </fieldset>
        <button className="btn" type="submit" disabled={busy}>
          Submit request
        </button>
      </form>
      {error && (
        <div className="mt-4">
          <Notice kind="error" title="Request not submitted.">
            <p>{error}</p>
          </Notice>
        </div>
      )}
      {submitted && (
        <div className="mt-4">
          <Notice kind="success" title="Request received. Keep this reference.">
            <dl className="mt-3 grid grid-cols-[minmax(8rem,12rem)_1fr] gap-x-4 gap-y-2">
              <dt className="text-ink-secondary">Reference</dt>
              <dd className="m-0">{submitted.reference}</dd>
              <dt className="text-ink-secondary">Type</dt>
              <dd className="m-0">{TYPE_LABEL[submitted.request_type]}</dd>
              <dt className="text-ink-secondary">Status</dt>
              <dd className="m-0">{statusLabel(submitted.status)}</dd>
              <dt className="text-ink-secondary">Requested</dt>
              <dd className="m-0">{formatDateTime(submitted.requested_at)}</dd>
              <dt className="text-ink-secondary">Fulfilment due by</dt>
              <dd className="m-0">{formatDateTime(submitted.fulfillment_due_at)}</dd>
            </dl>
          </Notice>
        </div>
      )}
    </div>
  );
}

export function statusLabel(status: string): string {
  const text = status.replace(/_/g, ' ');
  return text.charAt(0).toUpperCase() + text.slice(1);
}
