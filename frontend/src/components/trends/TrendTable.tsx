import { formatNumber } from '../../lib/format';
import type { ChartPoint } from './TrendChart';

interface Props {
  points: ChartPoint[];
  valueHeading: string;
  source: string;
}

const dateFmt = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

/** The data behind the chart: Date, value, Source. */
export function TrendTable({ points, valueHeading, source }: Props) {
  return (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full min-w-[20rem] border-collapse">
        <caption className="py-3 text-left font-semibold">Data behind the chart</caption>
        <thead>
          <tr>
            <th scope="col" className="bg-surface-selected px-4 py-2 text-left font-semibold">
              Date
            </th>
            <th scope="col" className="bg-surface-selected px-4 py-2 text-left font-semibold">
              {valueHeading}
            </th>
            <th scope="col" className="bg-surface-selected px-4 py-2 text-left font-semibold">
              Source
            </th>
          </tr>
        </thead>
        <tbody>
          {points.map((p) => (
            <tr key={p.time} className="border-b border-line bg-white">
              <td className="px-4 py-2 align-top">{dateFmt.format(new Date(p.time))}</td>
              <td className="px-4 py-2 align-top">{formatNumber(p.value, 2)}</td>
              <td className="px-4 py-2 align-top">{source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
