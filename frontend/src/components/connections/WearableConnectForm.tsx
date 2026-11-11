import { useState } from 'react';
import type { FormEvent } from 'react';
import { Notice } from '../ui/Notice';
import { beginWearableAuthorization, completeWearableAuthorization } from '../../lib/api-client';
import { ApiError } from '../../types/api';
import type { ConnectionResult, WearableProvider } from '../../types/connection';

interface Props {
  providers: WearableProvider[];
  disabled: boolean;
  onFinished: () => void;
}

/** "Approved wearable" form: pick from the approved list, authorize, finish the callback (FR-007). */
export function WearableConnectForm({ providers, disabled, onFinished }: Props) {
  const [choice, setChoice] = useState<string>(providers[0]?.provider ?? '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notSupported, setNotSupported] = useState(false);
  const [result, setResult] = useState<ConnectionResult | null>(null);

  const selected = choice;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotSupported(false);
    setResult(null);
    if (!selected) {
      setNotSupported(true);
      return;
    }
    setBusy(true);
    try {
      const started = await beginWearableAuthorization(selected);
      const state = new URL(started.authorization_url, window.location.origin).searchParams.get('state') ?? '';
      const done = await completeWearableAuthorization(selected, {
        connection_id: started.connection_id,
        state,
        code: 'granted',
      });
      setResult(done);
      onFinished();
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) setNotSupported(true);
      else setError(err instanceof ApiError ? err.detail : 'The wearable could not be connected. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="tile">
      <h2 id="wear-h" className="mb-3 text-xl">
        Approved wearable
      </h2>
      <form noValidate aria-labelledby="wear-h" onSubmit={submit}>
        <fieldset className="mb-6 min-w-0 border-0 p-0">
          <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">
            Wearable provider (approved list)
          </legend>
          {providers.map((p, index) => (
            <div key={p.provider} className="mb-3 flex items-start gap-2">
              <input
                type="radio"
                name="prov"
                id={`prov-${p.provider}`}
                className="mt-0.5 h-4 w-4 flex-none"
                value={p.provider}
                checked={selected === p.provider}
                onChange={() => setChoice(p.provider)}
                disabled={disabled}
              />
              <label htmlFor={`prov-${p.provider}`}>
                Wearable provider {String.fromCharCode(65 + index)} ({p.display_name})
              </label>
            </div>
          ))}
          <p className="field-help">Only providers approved for this service are listed.</p>
        </fieldset>
        <p className="mb-3 text-xs text-ink-secondary">
          You will be asked to allow Sapphire FitConnect to read activity and sleep data. You can disconnect at any
          time.
        </p>
        <button className="btn" type="submit" disabled={disabled || busy}>
          Authorize and connect
        </button>
      </form>
      <div className="mt-4 space-y-3" aria-live="polite">
        {notSupported && (
          <Notice kind="error">
            <p>Wearable provider is not supported. Choose a provider from the list.</p>
          </Notice>
        )}
        {error && <Notice kind="error">{error}</Notice>}
        {result && result.status === 'failed' && (
          <Notice kind="error" title="Connection could not be completed.">
            <p>Retry or contact support.</p>
            <p>Your account and other connections still work.</p>
          </Notice>
        )}
        {result && result.status !== 'failed' && (
          <Notice kind={result.status === 'pending' ? 'info' : 'success'}>
            <p>
              {result.status === 'pending'
                ? 'We are finishing the connection. Data from this source is not shown yet.'
                : 'Wearable connected.'}
            </p>
          </Notice>
        )}
      </div>
    </div>
  );
}
