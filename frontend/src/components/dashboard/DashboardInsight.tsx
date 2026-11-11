import { Link } from 'react-router-dom';
import type { DashboardInsightItem } from '../../types/dashboard';
import { METRIC_LABELS } from './MeasurementTile';

/** Mini insight card: observation and wellness guidance kept apart, with the uncertainty note. */
export function DashboardInsight({ insight }: { insight: DashboardInsightItem | undefined }) {
  return (
    <div className="tile-white">
      <h2 id="ins-h">Insight</h2>
      {!insight ? (
        <p>No insight is available yet. We need more readings before we can describe a pattern.</p>
      ) : (
        <article aria-labelledby="in1">
          <h3 id="in1">{METRIC_LABELS[insight.metric_type] ?? insight.metric_type} · last 7 days</h3>
          <p className="mt-2">
            <strong>What we measured:</strong> {insight.observation}
          </p>
          <p className="mt-2">
            <strong>Wellness guidance:</strong> {insight.wellness_guidance}
          </p>
          <p className="mt-2 text-xs tracking-label text-ink-secondary">
            {insight.uncertainty} This is general wellness information, not medical advice.
          </p>
          <p className="mt-2">
            <Link to="/trends">See trends and give feedback</Link>
          </p>
        </article>
      )}
    </div>
  );
}
