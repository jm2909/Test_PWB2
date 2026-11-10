import { useState } from 'react';
import type { FormEvent } from 'react';
import Notification from '../common/Notification';
import { ApiError, api } from '../../lib/api-client';
import { WELLNESS_GOAL_OPTIONS } from '../../types/goal';
import type { Goal, GoalType } from '../../types/goal';

interface Props {
  onSaved: (goal: Goal) => void;
}

const GUIDANCE = 'Enter a target above 0 that is realistic for you, for example 65.';

export default function GoalForm({ onSaved }: Props) {
  const [type, setType] = useState<GoalType>('weight_loss');
  const [value, setValue] = useState('65');
  const [unit, setUnit] = useState('kg');
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const option = WELLNESS_GOAL_OPTIONS.find((o) => o.type === type) ?? WELLNESS_GOAL_OPTIONS[0];

  const choose = (next: GoalType) => {
    const o = WELLNESS_GOAL_OPTIONS.find((x) => x.type === next) ?? WELLNESS_GOAL_OPTIONS[0];
    setType(next);
    setUnit(o.units[0]);
    setSaved(false);
    setError(null);
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSaved(false);
    const num = Number(value.trim());
    if (value.trim() === '' || !Number.isFinite(num)) {
      setError(GUIDANCE);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const goal = await api.post<Goal>('/goals', { goal_type: type, target_value: num, target_unit: unit });
      setSaved(true);
      onSaved(goal);
    } catch (err) {
      setError(err instanceof ApiError && err.status === 422 ? err.message : 'The goal could not be saved. Try again.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="bg-layer p-6" aria-labelledby="gf-h" noValidate onSubmit={(e) => void submit(e)}>
      <h2 id="gf-h" className="mb-4 text-xl">Set a goal</h2>
      <fieldset>
        <legend className="mb-2 text-xs text-text-secondary">Goal type</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {WELLNESS_GOAL_OPTIONS.map((o) => (
            <label
              key={o.type}
              className={`block min-h-[72px] bg-background p-4 ${
                type === o.type ? 'border border-link outline outline-1 outline-link' : 'border border-transparent'
              }`}
            >
              <input
                type="radio"
                name="goal_type"
                value={o.type}
                checked={type === o.type}
                onChange={() => choose(o.type)}
                className="mr-2"
              />
              <strong>{o.label}</strong>
              {o.help && <p className="mt-1 ml-6 text-sm text-text-secondary">{o.help}</p>}
            </label>
          ))}
        </div>
      </fieldset>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="goal-value" className="mb-2 block text-xs text-text-secondary">Target value</label>
          <input
            id="goal-value"
            type="text"
            inputMode="decimal"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? 'goal-value-err' : undefined}
            className={`block h-10 w-full bg-field px-4 ${
              error ? 'outline outline-2 -outline-offset-2 outline-support-error' : 'border-b border-border-strong'
            }`}
          />
          {error && (
            <p id="goal-value-err" className="mt-1 flex items-start gap-2 text-sm text-text-error">
              <svg width="16" height="16" viewBox="0 0 16 16" className="mt-0.5 flex-none fill-support-error" aria-hidden="true">
                <path d="M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z" />
              </svg>
              <span>{error}</span>
            </p>
          )}
        </div>
        <div>
          <label htmlFor="goal-unit" className="mb-2 block text-xs text-text-secondary">Unit</label>
          <select
            id="goal-unit"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            className="block h-10 w-full border-b border-border-strong bg-field px-4"
          >
            {option.units.map((u) => (
              <option key={u} value={u}>{u}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={saving}
        className="mt-6 inline-flex min-h-12 items-center gap-8 bg-button-primary px-4 text-white disabled:opacity-50"
      >
        <span>Save goal</span>
        <span aria-hidden="true">→</span>
      </button>

      {saved && (
        <Notification kind="success" title="Goal saved" className="mt-6">
          <p>Goal saved and active.</p>
        </Notification>
      )}
      {error && (
        <Notification kind="error" title="Goal not saved" role="alert" className="mt-6">
          <p>Your goal has not been saved. Correct the target above and try again.</p>
        </Notification>
      )}
    </form>
  );
}
