import { useState } from 'react';
import type { FormEvent } from 'react';
import { createGoal } from '../../lib/api-client';
import { ApiError } from '../../types/api';
import type { Goal, GoalCategory, GoalMetric } from '../../types/goal';
import { Notice } from '../ui/Notice';

export const CATEGORIES: ReadonlyArray<{ value: GoalCategory; label: string }> = [
  { value: 'weight_management', label: 'Weight management' },
  { value: 'fitness', label: 'Fitness' },
  { value: 'sleep_improvement', label: 'Sleep improvement' },
  { value: 'general_wellness', label: 'General wellness' },
];

export const METRICS: ReadonlyArray<{ value: GoalMetric; label: string; unit: string }> = [
  { value: 'weight', label: 'Weight', unit: 'kg' },
  { value: 'steps', label: 'Steps per day', unit: 'count' },
  { value: 'sleep_duration', label: 'Sleep duration', unit: 'hours' },
];

const METRIC_FOR_CATEGORY: Record<GoalCategory, ReadonlyArray<GoalMetric>> = {
  weight_management: ['weight'],
  fitness: ['steps'],
  sleep_improvement: ['sleep_duration'],
  general_wellness: ['weight', 'steps', 'sleep_duration'],
};

interface Errors {
  target?: string;
  unit?: string;
  date?: string;
}

interface Props {
  onSaved: (goal: Goal) => void;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function GoalForm({ onSaved }: Props) {
  const [category, setCategory] = useState<GoalCategory>('weight_management');
  const [metric, setMetric] = useState<GoalMetric>('weight');
  const [target, setTarget] = useState('');
  const [unit, setUnit] = useState('kg');
  const [date, setDate] = useState('');
  const [errors, setErrors] = useState<Errors>({});
  const [failed, setFailed] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  const metricOptions = METRICS.filter((m) => METRIC_FOR_CATEGORY[category].includes(m.value));

  const changeCategory = (next: GoalCategory) => {
    setCategory(next);
    if (!METRIC_FOR_CATEGORY[next].includes(metric)) changeMetric(METRIC_FOR_CATEGORY[next][0]);
  };

  const changeMetric = (next: GoalMetric) => {
    setMetric(next);
    setUnit(METRICS.find((m) => m.value === next)?.unit ?? '');
  };

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaved(false);
    setFailed(null);
    const found: Errors = {};
    const value = Number(target);
    if (target.trim() === '' || !Number.isFinite(value) || value <= 0) found.target = 'Enter a target greater than zero.';
    if (unit.trim() === '') found.unit = 'Enter the unit for this measurement.';
    if (date === '' || date <= todayIso()) found.date = 'Choose a date in the future.';
    setErrors(found);
    if (Object.keys(found).length > 0) return;
    setBusy(true);
    try {
      const goal = await createGoal({
        category,
        metric_type: metric,
        target_value: value,
        target_unit: unit.trim(),
        target_date: date,
      });
      setSaved(true);
      setTarget('');
      setDate('');
      onSaved(goal);
    } catch (err) {
      setFailed(err instanceof ApiError ? err.detail : 'Your goal could not be saved. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="tile">
      <h2 id="new-h">Set a new goal</h2>
      <form noValidate aria-labelledby="new-h" onSubmit={onSubmit}>
        <div className="mb-6">
          <label className="field-label" htmlFor="g-cat">
            Goal category
          </label>
          <select
            className="field-input"
            id="g-cat"
            value={category}
            onChange={(e) => changeCategory(e.target.value as GoalCategory)}
          >
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="g-metric">
            Measurement
          </label>
          <select
            className="field-input"
            id="g-metric"
            value={metric}
            onChange={(e) => changeMetric(e.target.value as GoalMetric)}
          >
            {metricOptions.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="g-target">
            Target value
          </label>
          <input
            className="field-input"
            id="g-target"
            type="text"
            inputMode="decimal"
            value={target}
            aria-invalid={errors.target ? true : undefined}
            aria-describedby={errors.target ? 'g-target-err' : undefined}
            onChange={(e) => setTarget(e.target.value)}
          />
          {errors.target && (
            <p className="mt-1 text-xs text-danger" id="g-target-err">
              {errors.target}
            </p>
          )}
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="g-unit">
            Unit
          </label>
          <input
            className="field-input"
            id="g-unit"
            type="text"
            value={unit}
            aria-invalid={errors.unit ? true : undefined}
            aria-describedby="g-unit-help"
            onChange={(e) => setUnit(e.target.value)}
          />
          <p className="field-help" id="g-unit-help">
            Use the unit that matches the measurement: kg, count (steps), or hours.
          </p>
          {errors.unit && <p className="mt-1 text-xs text-danger">{errors.unit}</p>}
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="g-date">
            Target date
          </label>
          <input
            className="field-input"
            id="g-date"
            type="date"
            value={date}
            aria-invalid={errors.date ? true : undefined}
            aria-describedby={errors.date ? 'g-date-err' : undefined}
            onChange={(e) => setDate(e.target.value)}
          />
          {errors.date && (
            <p className="mt-1 text-xs text-danger" id="g-date-err">
              {errors.date}
            </p>
          )}
        </div>
        <button className="btn" type="submit" disabled={busy}>
          Save goal
        </button>
      </form>
      {(Object.keys(errors).length > 0 || failed) && (
        <div className="mt-4">
          <Notice kind="error">
            <p>
              <strong>Goal not saved.</strong>{' '}
              {failed ?? 'Add a target value, unit, and a future target date.'}
            </p>
          </Notice>
        </div>
      )}
      {saved && (
        <div className="mt-4">
          <Notice kind="success">
            <p>
              <strong>Goal saved.</strong> It now appears below as Active.
            </p>
          </Notice>
        </div>
      )}
    </div>
  );
}
