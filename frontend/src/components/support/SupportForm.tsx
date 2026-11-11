import { useState } from 'react';
import type { FormEvent } from 'react';
import { createSupportRequest } from '../../lib/api-client';
import type { SupportCategory, SupportContextType, SupportRequestReceipt } from '../../types/support';
import { Notice } from '../ui/Notice';
import { LabelledSelect } from './LabelledSelect';

export const MAX_DESCRIPTION = 2000;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const HEALTH_VALUE_RE = /\d\s?(kg|lbs?|bpm|mmhg|mg\/dl|mmol)/i;

const CONTEXTS: ReadonlyArray<{ value: SupportContextType; label: string; help: string }> = [
  {
    value: 'device',
    label: 'A device connection',
    help: 'We attach the device label, not any technical details.',
  },
  { value: 'account', label: 'My account', help: 'Sign-in, privacy, or data rights questions.' },
  { value: 'alert', label: 'An alert', help: 'We attach the alert reference only.' },
];

export const CATEGORIES: ReadonlyArray<{ value: SupportCategory; label: string }> = [
  { value: 'connection', label: 'Connection' },
  { value: 'data_quality', label: 'Data quality' },
  { value: 'account', label: 'Account' },
  { value: 'alert', label: 'Alert' },
];

const DEFAULT_CATEGORY: Record<SupportContextType, SupportCategory> = {
  device: 'connection',
  account: 'account',
  alert: 'alert',
};

interface Props {
  initialContext: SupportContextType;
  initialId: string | null;
  onSubmitted: (receipt: SupportRequestReceipt, categoryLabel: string) => void;
  onFailed: () => void;
}

export function SupportForm({ initialContext, initialId, onSubmitted, onFailed }: Props) {
  const [context, setContext] = useState<SupportContextType>(initialContext);
  const [category, setCategory] = useState<SupportCategory>(DEFAULT_CATEGORY[initialContext]);
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const contextId = initialId && UUID_RE.test(initialId) && context === initialContext ? initialId : undefined;
  const looksLikeHealthValue = HEALTH_VALUE_RE.test(description);

  const chooseContext = (value: SupportContextType) => {
    setContext(value);
    setCategory(DEFAULT_CATEGORY[value]);
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (trimmed.length < 1 || trimmed.length > MAX_DESCRIPTION) {
      setError(`Enter a description of 1 to ${MAX_DESCRIPTION} characters.`);
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const receipt = await createSupportRequest({
        category,
        description: trimmed,
        context_type: context,
        ...(context !== 'account' && contextId ? { context_id: contextId } : {}),
      });
      onSubmitted(receipt, CATEGORIES.find((c) => c.value === category)?.label ?? category);
    } catch {
      onFailed();
    } finally {
      setBusy(false);
    }
  };

  return (
    <form noValidate aria-labelledby="ctx-h" onSubmit={submit}>
      <fieldset className="mb-6 min-w-0 border-0 p-0">
        <legend className="mb-2 p-0 text-xs tracking-label text-ink-secondary">Where did you come from?</legend>
        {CONTEXTS.map((c) => (
          <div key={c.value} className="mb-3 flex items-start gap-2">
            <input
              className="mt-0.5 h-4 w-4 flex-none"
              type="radio"
              name="ctx"
              id={`c-${c.value}`}
              checked={context === c.value}
              onChange={() => chooseContext(c.value)}
            />
            <label htmlFor={`c-${c.value}`} className="cursor-pointer">
              {c.label}
              <span className="block text-xs tracking-label text-ink-secondary">{c.help}</span>
            </label>
          </div>
        ))}
      </fieldset>

      <LabelledSelect
        id="s-cat"
        labelText="Category"
        value={category}
        helperText="Connection, data quality, account, or alert."
        onChange={(e) => setCategory(e.target.value as SupportCategory)}
      >
        {CATEGORIES.map((c) => (
          <option key={c.value} value={c.value}>
            {c.label}
          </option>
        ))}
      </LabelledSelect>

      <div className="mb-6">
        <label className="field-label" htmlFor="s-desc">
          Describe the problem
        </label>
        <textarea
          className="field-input min-h-[8rem] py-3"
          id="s-desc"
          name="description"
          rows={5}
          value={description}
          aria-invalid={error ? true : undefined}
          aria-describedby={`s-desc-help s-desc-count${error ? ' s-desc-err' : ''}`}
          onChange={(e) => setDescription(e.target.value)}
        />
        {error && (
          <p className="mt-1 text-xs tracking-label text-danger" id="s-desc-err">
            {error}
          </p>
        )}
        <p className="field-help" id="s-desc-help">
          Describe what happened and when. Please do not include health readings, medical details, passwords, or other
          private information.
        </p>
        <p className="field-help" id="s-desc-count">
          {description.length} of {MAX_DESCRIPTION} characters
        </p>
      </div>

      {looksLikeHealthValue && (
        <div className="mb-6">
          <Notice kind="warning" role="status">
            <p>
              Your message looks like it may include health readings. Please remove them and describe the problem in
              words, for example “my weight did not appear on the dashboard”.
            </p>
          </Notice>
        </div>
      )}

      <button className="btn" type="submit" disabled={busy}>
        Send request
      </button>
    </form>
  );
}
