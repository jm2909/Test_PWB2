import { Link } from 'react-router-dom';
import type { SignalGroup } from '../../types/dashboard';
import { tileTitle } from '../../types/dashboard';

export const TILE_CLASS = 'col-span-full flex min-h-[220px] flex-col p-4 md:col-span-4 lg:col-span-5';

export default function SignalTile({ group }: { group: SignalGroup }) {
  const isGoal = group.key === 'goals';
  const id = `sig-${group.key}`;
  return (
    <section aria-labelledby={id} className={`${TILE_CLASS} bg-layer`}>
      <h2 id={id} className="text-xs text-text-secondary">
        {tileTitle(group.key, group.title)}
      </h2>
      <p className="mt-4 text-[2.625rem] font-light leading-[3.125rem]">
        {group.value ?? '—'}{' '}
        {group.unit && <small className="text-base font-normal text-text-secondary">{group.unit}</small>}
      </p>
      {group.details.map((line) => (
        <p key={line} className="mt-2 text-text-secondary">
          {line}
        </p>
      ))}
      <Link to={isGoal ? '/goals' : '/trends'} className="mt-auto pt-4 text-link">
        {isGoal ? 'Review goal' : 'View trend'} <span aria-hidden="true">→</span>
      </Link>
    </section>
  );
}
