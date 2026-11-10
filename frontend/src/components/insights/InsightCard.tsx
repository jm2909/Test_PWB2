import { Link } from 'react-router-dom';
import Notification from '../common/Notification';
import type { Insight } from '../../types/insight';

export default function InsightCard({ insight }: { insight: Insight | null }) {
  if (!insight || insight.status === 'suppressed') {
    return (
      <Notification kind="info" title="We don't have enough reliable data to give you an insight yet.">
        <p>Keep syncing your devices and check back soon.</p>
      </Notification>
    );
  }
  return (
    <div className="border border-[#e0e0e0] bg-white p-6" data-testid="insight-published">
      <h3 className="text-base font-semibold">Your latest insight</h3>
      <dl className="mt-3 grid grid-cols-[minmax(120px,160px)_1fr] gap-x-4 gap-y-1">
        <dt className="text-text-secondary">Observed trend</dt>
        <dd>{insight.observed_trend}</dd>
        <dt className="text-text-secondary">Wellness implication</dt>
        <dd>{insight.wellness_implication}</dd>
      </dl>
      <p className="mt-4">
        <Link to="/trends" className="text-link underline">View the sleep trend</Link>
      </p>
    </div>
  );
}
