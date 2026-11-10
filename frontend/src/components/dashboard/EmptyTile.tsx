import { Link } from 'react-router-dom';
import type { SourceGap } from '../../types/dashboard';
import { tileTitle } from '../../types/dashboard';
import { TILE_CLASS } from './SignalTile';

export default function EmptyTile({ gap }: { gap: SourceGap }) {
  const isGoal = gap.key === 'goals';
  const title = tileTitle(gap.key, gap.title);
  const id = `gap-${gap.key}`;
  const heading = isGoal ? 'No goal set' : `No ${gap.title.toLowerCase()} data yet`;
  const reason = isGoal ? 'Pick a goal to see how your readings relate to it.' : gap.reason;
  const to = isGoal ? '/goals' : '/devices/sync';
  return (
    <section aria-labelledby={id} className={`${TILE_CLASS} border border-dashed border-[#8d8d8d] bg-white`}>
      <h2 id={id} className="text-xs text-text-secondary">
        {title}
      </h2>
      <p className="mt-4 font-semibold">{heading}</p>
      <p className="mt-2 text-text-secondary">{reason}</p>
      {gap.recovery_action && (
        <Link to={to} className="mt-auto pt-4 text-link">
          {gap.recovery_action} <span aria-hidden="true">→</span>
        </Link>
      )}
    </section>
  );
}
