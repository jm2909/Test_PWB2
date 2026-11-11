import { useState } from 'react';
import type { FormEvent } from 'react';
import { Notice } from '../ui/Notice';
import { connectScale } from '../../lib/api-client';
import { ApiError } from '../../types/api';
import type { ConnectionResult } from '../../types/connection';

export const SCALES = [
  { id: 'SSC-0482', label: 'Bathroom' },
  { id: 'SSC-0517', label: 'Bedroom' },
  { id: 'SSC-0733', label: 'Living room' },
] as const;

interface Props {
  disabled: boolean;
  /** Labels of scales already linked, so a repeat is explained rather than shown as new. */
  connectedLabels: string[];
  onConnected: () => void;
}

/** "Sapphire scale" form: choose a scale and connect it (FR-006). */
export function ScaleConnectForm({ disabled, connectedLabels, onConnected }: Props) {
  const [scaleId, setScaleId] = useState<string>(SCALES[0].id);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ConnectionResult | null>(null);
  const [existing, setExisting] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const scale = SCALES.find((s) => s.id === scaleId) ?? SCALES[0];
    setBusy(true);
    setError(null);
    setResult(null);
    setExisting(false);
    try {
      const created = await connectScale({ device_identifier: scale.id, device_label: scale.label });
      setResult(created);
      // A repeat of an already-linked scale returns the same association, not a new one.
      setExisting(created.status !== 'failed' && connectedLabels.includes(scale.label));
      onConnected();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'The scale could not be connected. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="tile">
      <h2 id="scale-h" className="mb-3 text-xl">
        Sapphire scale
      </h2>
      <form noValidate aria-labelledby="scale-h" onSubmit={submit}>
        <div className="mb-6">
          <label className="field-label" htmlFor="scale-sel">
            Choose your scale
          </label>
          <select
            id="scale-sel"
            name="scale"
            className="field-input"
            aria-describedby="scale-help"
            value={scaleId}
            onChange={(e) => setScaleId(e.target.value)}
            disabled={disabled}
          >
            {SCALES.map((s) => (
              <option key={s.id} value={s.id}>
                Sapphire Smart Scale – {s.label} ({s.id})
              </option>
            ))}
          </select>
          <p className="field-help" id="scale-help">
            Each scale can be connected to one account at a time. A scale that is already connected cannot be added
            twice.
          </p>
        </div>
        <button className="btn" type="submit" disabled={disabled || busy}>
          Connect scale
        </button>
      </form>
      <div className="mt-4 space-y-3" aria-live="polite">
        {error && <Notice kind="error">{error}</Notice>}
        {result && result.status === 'failed' && (
          <Notice kind="error" title="Connection could not be completed.">
            <p>Retry or contact support. Your account and other connections still work.</p>
          </Notice>
        )}
        {result && result.status === 'pending' && (
          <Notice kind="info">
            <p>We are finishing the connection. Data from this source is not shown yet.</p>
          </Notice>
        )}
        {result && result.status !== 'failed' && result.status !== 'pending' && existing && (
          <Notice kind="info">
            <p>
              This scale is already connected to your account. Choose a different scale or manage the existing
              connection below.
            </p>
          </Notice>
        )}
        {result && result.status !== 'failed' && result.status !== 'pending' && !existing && (
          <Notice kind="success">
            <p>Scale connected.</p>
          </Notice>
        )}
      </div>
    </div>
  );
}
