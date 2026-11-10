import Notification from '../common/Notification';
import type { SyncSummary } from '../../types/sync';
import { metricLabel } from '../../types/sync';

interface Props {
  summary: SyncSummary | null;
  at: Date | null;
}

export default function SyncAddedPanel({ summary, at }: Props) {
  const when = at
    ? `Most recent sync, today at ${at.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}`
    : 'No sync has run in this session yet';
  const metrics = summary ? Object.entries(summary.by_metric) : [];
  return (
    <aside className="bg-layer p-4" aria-labelledby="added-h">
      <h2 id="added-h" className="font-semibold">What was added</h2>
      <p className="mt-1 text-xs text-text-helper">{when}</p>
      <p data-testid="added-count" className="mt-4 text-[2.625rem] font-light leading-[3.125rem]">
        {summary ? summary.new_readings : '—'}
      </p>
      <p>new readings added to your history</p>
      {metrics.length > 0 && (
        <ul className="mt-4">
          {metrics.map(([metric, count]) => (
            <li key={metric} className="border-t border-border-subtle py-2">
              {metricLabel(metric)}: {count}
            </li>
          ))}
        </ul>
      )}
      {summary && (
        <Notification kind="info" title="Duplicates" role="note" className="mt-4">
          <p>
            {summary.duplicates} {summary.duplicates === 1 ? 'reading was' : 'readings were'} received twice and counted once.
          </p>
        </Notification>
      )}
    </aside>
  );
}
