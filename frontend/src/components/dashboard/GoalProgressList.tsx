import { Link } from 'react-router-dom';
import { formatDateTime, formatNumber } from '../../lib/format';
import type { DashboardGoal } from '../../types/dashboard';
import { StatusBadge } from '../ui/StatusBadge';
import { METRIC_LABELS } from './MeasurementTile';

const UNITS: Record<string, string> = { count: 'steps per day', hours: 'h', minutes: 'min' };

/** Active goals with progress, or an explicit data gap. */
export function GoalProgressList({ goals }: { goals: DashboardGoal[] }) {
  return (
    <div className="tile">
      <h2 id="goal-h">Goal progress</h2>
      {goals.length === 0 && (
        <p>
          No active goals yet. <Link to="/goals">Set a goal</Link>
        </p>
      )}
      <ul className="list-none space-y-4 p-0">
        {goals.map((g) => {
          const unit = UNITS[g.target_unit] ?? g.target_unit;
          const available = g.progress_status === 'available' && g.current_value !== null;
          return (
            <li key={g.id}>
              <p>
                <strong>{METRIC_LABELS[g.metric_type] ?? g.metric_type}</strong> · target {formatNumber(Number(g.target_value))}{' '}
                {unit} by {formatDateTime(`${g.target_date}T00:00:00Z`).split(',')[0]}
              </p>
              {available ? (
                <p className="text-xs tracking-label text-ink-secondary">
                  Progress available: current {formatNumber(Number(g.current_value))} {unit}
                </p>
              ) : (
                <>
                  <p className="mt-2">
                    <StatusBadge status="stale" label="Data gap" />
                  </p>
                  <p className="text-xs tracking-label text-ink-secondary">
                    No recent readings since this goal was set, so progress cannot be shown.{' '}
                    <Link to="/goals">View goals</Link>
                  </p>
                </>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
