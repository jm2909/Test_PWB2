import { useState } from 'react';
import type { FormEvent } from 'react';
import { saveConsent } from '../../lib/api-client';
import { ApiError } from '../../types/api';
import type { ConsentDecision, ConsentRecord, DataCategory } from '../../types/consent';
import { Notice } from '../ui/Notice';

export const NOTICE_VERSION = 'v1.0';
export const NOTICE_CATEGORIES: DataCategory[] = [
  'weight',
  'body_composition',
  'steps',
  'sleep_duration',
  'active_minutes',
];

interface Props {
  current: ConsentRecord | null;
  onSaved: (record: ConsentRecord) => void;
}

export function ConsentForm({ current, onSaved }: Props) {
  const [decision, setDecision] = useState<ConsentDecision>(current?.decision ?? 'granted');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const record = await saveConsent({
        decision,
        notice_version: NOTICE_VERSION,
        data_categories: NOTICE_CATEGORIES,
        purpose: 'wellness_support',
      });
      onSaved(record);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Your decision could not be saved. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <form noValidate className="mt-6" aria-labelledby="consent-h" onSubmit={onSubmit}>
      <fieldset className="mb-6 min-w-0 border-0 p-0">
        <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">
          Your decision for notice {NOTICE_VERSION}
        </legend>
        <div className="mb-3 flex items-start gap-2">
          <input
            className="mt-0.5 h-4 w-4 flex-none"
            type="radio"
            name="decision"
            id="d-grant"
            checked={decision === 'granted'}
            onChange={() => setDecision('granted')}
          />
          <label htmlFor="d-grant" className="cursor-pointer">
            I agree to the collection of the categories above for wellness support
            <span className="block text-xs tracking-label text-ink-secondary">
              Allows scale and wearable connections and manual entry.
            </span>
          </label>
        </div>
        <div className="mb-3 flex items-start gap-2">
          <input
            className="mt-0.5 h-4 w-4 flex-none"
            type="radio"
            name="decision"
            id="d-withdraw"
            checked={decision === 'withdrawn'}
            onChange={() => setDecision('withdrawn')}
          />
          <label htmlFor="d-withdraw" className="cursor-pointer">
            I do not agree, or I withdraw my agreement
            <span className="block text-xs tracking-label text-ink-secondary">
              Stops new collection of nonessential data. Your data rights stay available.
            </span>
          </label>
        </div>
      </fieldset>
      {error && (
        <div className="mb-4">
          <Notice kind="error" title="Decision not saved.">
            <p>{error}</p>
          </Notice>
        </div>
      )}
      <button className="btn" type="submit" disabled={busy}>
        Save my decision
      </button>
      <p className="field-help">
        Your decision is saved with the notice version and the date and time you made it.
      </p>
    </form>
  );
}
