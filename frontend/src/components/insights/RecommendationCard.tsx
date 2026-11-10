import { Link } from 'react-router-dom';
import type { Recommendation } from '../../types/insight';

export default function RecommendationCard({ recommendation }: { recommendation: Recommendation | null }) {
  if (!recommendation || recommendation.status === 'none' || !recommendation.action_text) {
    return (
      <div className="bg-layer p-4" role="status">
        <p>No action to suggest right now. We only suggest steps that fit your data.</p>
      </div>
    );
  }
  const goalAction = recommendation.suggested_goal_type === 'sleep_improvement';
  return (
    <div className="border border-[#e0e0e0] bg-white p-6" data-testid="recommendation">
      <h3 className="text-base font-semibold">{recommendation.action_text}</h3>
      <dl className="mt-3 grid grid-cols-[minmax(120px,160px)_1fr] gap-x-4 gap-y-1">
        <dt className="text-text-secondary">Why</dt>
        <dd>{recommendation.reason_text}</dd>
      </dl>
      {recommendation.suggested_goal_type && (
        <p className="mt-4">
          <Link
            to="/goals"
            className="inline-flex min-h-10 items-center gap-2 border border-[#0f62fe] px-4 text-[#0f62fe] no-underline"
          >
            {goalAction ? 'Set a sleep goal' : 'Set a goal'}
            <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="currentColor">
              <polygon points="9.3,3.7 13.1,7.5 1,7.5 1,8.5 13.1,8.5 9.3,12.3 10,13 15,8 10,3" />
            </svg>
          </Link>
        </p>
      )}
    </div>
  );
}
