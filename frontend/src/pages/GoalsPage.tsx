import { useCallback, useEffect, useState } from 'react';
import ActiveGoalTile from '../components/goals/ActiveGoalTile';
import GoalForm from '../components/goals/GoalForm';
import Notification from '../components/common/Notification';
import { ApiError, api } from '../lib/api-client';
import type { Goal, ListResponse } from '../types';

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const list = await api.get<ListResponse<Goal>>('/goals');
      setGoals(list.items);
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Your goals could not be loaded.');
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section aria-labelledby="goals-h">
      <h1 id="goals-h" className="text-[2rem] leading-10">Goals</h1>
      <p className="mt-2 max-w-3xl text-base text-text-secondary">
        Choose a wellness goal and a target. Your dashboard will show how your latest readings sit next to it.
      </p>
      <div className="mt-8 grid gap-6 lg:grid-cols-16">
        <div className="lg:col-span-10">
          <GoalForm onSaved={() => void load()} />
        </div>
        <aside className="lg:col-span-6" aria-labelledby="ag-h">
          <h2 id="ag-h" className="mb-3 text-base font-semibold">Your active goal</h2>
          {error && (
            <Notification kind="error" title="Goals not loaded" role="alert" className="mb-3">
              <p>{error}</p>
            </Notification>
          )}
          <div className="space-y-3">
            {goals.length === 0 && !error && (
              <p className="bg-layer p-4 text-sm text-text-secondary">No active goal yet. Save one to see it here.</p>
            )}
            {goals.map((g) => (
              <ActiveGoalTile key={g.id} goal={g} />
            ))}
          </div>
          <Notification kind="info" title="Goals are for everyday wellness" role="note" className="mt-4">
            <p>FitConnect does not set clinical targets or give medical advice.</p>
          </Notification>
        </aside>
      </div>
    </section>
  );
}
