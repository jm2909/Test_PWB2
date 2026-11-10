import type { TrendPoint } from '../../types/trend';

interface Props {
  points: TrendPoint[];
  caption: string;
  column: string;
  label: string;
}

export function formatDate(iso: string, withYear = true): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    ...(withYear ? { year: 'numeric' } : {}),
    timeZone: 'UTC',
  });
}

export default function TrendTable({ points, caption, column, label }: Props) {
  return (
    <div className="mt-4 overflow-x-auto border border-[#e0e0e0]" role="region" aria-label={label} tabIndex={0}>
      <table className="w-full min-w-[360px] border-collapse">
        <caption className="bg-layer px-4 py-3 text-left font-semibold">{caption}</caption>
        <thead>
          <tr>
            <th scope="col" className="h-10 bg-[#e0e0e0] px-4 text-left font-semibold">Date</th>
            <th scope="col" className="h-10 bg-[#e0e0e0] px-4 text-left font-semibold">{column}</th>
          </tr>
        </thead>
        <tbody>
          {points.map((p) => (
            <tr key={p.observed_at}>
              <td className="border-t border-[#e0e0e0] px-4 py-2">{formatDate(p.observed_at)}</td>
              <td className="border-t border-[#e0e0e0] px-4 py-2">{p.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
