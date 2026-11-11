import { useCallback, useEffect, useState } from 'react';
import { GoalCard } from '../components/goals/GoalCard';
import { GoalForm } from '../components/goals/GoalForm';
import { Notice } from '../components/ui/Notice';
import { listGoals, updateGoalState } from '../lib/api-client';
import { ApiError } from '../types/api';
import type { Goal } from '../types/goal';

export function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const page = await listGoals();
      setGoals(page.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Goals could not be loaded. Try again.');
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const change = async (goal: Goal, state: 'active' | 'paused' | 'closed') => {
    setBusy(true);
    try {
      await updateGoalState(goal.id, state);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'The goal could not be updated. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Your own data only</p>
          <h1 id="page-title">Goals</h1>
          <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
            Set a wellness goal for a measurement you track. Progress is based on your recorded readings, and we tell
            you when data is missing.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="new-h">
        <div className="page-grid grid gap-8 lg:grid-cols-2">
          <GoalForm onSaved={() => void load()} />
          <div className="tile-white">
            <h2>About goals</h2>
            <ul className="list-disc space-y-3 pl-4">
              <li>Goals are for general wellness and are your own choice. They are not medical targets.</li>
              <li>Pausing or closing a goal never deletes your past readings.</li>
              <li>If a source has not provided recent data, progress shows as a data gap instead of a guess.</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="mt-8" aria-labelledby="list-h">
        <div className="page-grid">
          <h2 id="list-h">Your goals</h2>
          {!loaded && <p role="status">Loading your goals…</p>}
          {error && (
            <div className="mb-4">
              <Notice kind="error">
                <p>{error}</p>
              </Notice>
            </div>
          )}
          {loaded && goals.length === 0 && !error && <p>You have not set any goals yet.</p>}
          {goals.map((g) => (
            <GoalCard key={g.id} goal={g} onChange={change} busy={busy} />
          ))}
        </div>
      </section>
    </>
  );
}
