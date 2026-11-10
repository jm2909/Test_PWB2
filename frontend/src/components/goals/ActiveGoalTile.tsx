import { Link } from 'react-router-dom';
import { goalLabel } from '../../types/goal';
import type { Goal } from '../../types/goal';

export default function ActiveGoalTile({ goal }: { goal: Goal }) {
  return (
    <div className="bg-layer p-4" data-testid="active-goal">
      <p className="text-[2rem] leading-10 font-light">
        {goal.target_value} <span className="text-base text-text-secondary">{goal.target_unit}</span>
      </p>
      <p className="mt-1">{goalLabel(goal.goal_type)}</p>
      <p className="mt-3 text-sm text-text-secondary">
        See it next to your latest readings on your{' '}
        <Link to="/" className="text-link underline">dashboard</Link>.
      </p>
    </div>
  );
}
