import type { TrendPoint } from '../../types/trend';
import { formatDate } from './TrendTable';

interface Props {
  points: TrendPoint[];
  metricLabel: string;
  unit: string;
}

const X0 = 60;
const X1 = 770;
const Y0 = 40;
const Y1 = 290;

function bounds(values: number[]): [number, number] {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const pad = max === min ? Math.max(1, Math.abs(max) * 0.05) : (max - min) * 0.1;
  return [min - pad, max + pad];
}

export default function TrendChart({ points, metricLabel, unit }: Props) {
  if (points.length === 0) return null;
  const times = points.map((p) => new Date(p.observed_at).getTime());
  const t0 = Math.min(...times);
  const t1 = Math.max(...times);
  const [lo, hi] = bounds(points.map((p) => p.value));
  const x = (t: number) => (t1 === t0 ? (X0 + X1) / 2 : X0 + 10 + ((t - t0) / (t1 - t0)) * (X1 - X0 - 10));
  const y = (v: number) => Y1 - ((v - lo) / (hi - lo)) * (Y1 - Y0);
  const coords = points.map((p, i) => ({ cx: x(times[i]), cy: y(p.value) }));
  const ticks = [0, 1, 2, 3, 4].map((i) => lo + ((hi - lo) * i) / 4);
  const xTicks = [0, 1, 2, 3, 4].map((i) => t0 + ((t1 - t0) * i) / 4);
  const first = points[0];
  const last = points[points.length - 1];
  const lastC = coords[coords.length - 1];
  const title = `Line chart of ${metricLabel.toLowerCase()} in ${unit}, ${formatDate(first.observed_at, false)} to ${formatDate(last.observed_at, false)}`;
  const desc = `${metricLabel} moved from ${first.value} ${unit} on ${formatDate(first.observed_at, false)} to ${last.value} ${unit} on ${formatDate(last.observed_at, false)}. A table with the same values follows the chart.`;
  const labelX = Math.min(lastC.cx, 800 - 50);

  return (
    <svg className="block h-auto w-full" viewBox="0 0 800 360" role="img" aria-labelledby="ch-t ch-d" data-testid="trend-chart">
      <title id="ch-t">{title}</title>
      <desc id="ch-d">{desc}</desc>
      <g stroke="#e0e0e0" strokeWidth="1">
        {ticks.slice(1).map((t) => (
          <line key={t} x1={X0} y1={y(t)} x2={780} y2={y(t)} />
        ))}
      </g>
      <line x1={X0} y1={Y1} x2={780} y2={Y1} stroke="#8d8d8d" strokeWidth="1" />
      <g textAnchor="end" fontSize="12" fill="#525252">
        {ticks.map((t) => (
          <text key={t} x={52} y={y(t) + 4}>{t.toFixed(1)}</text>
        ))}
      </g>
      <text x={14} y={165} transform="rotate(-90 14 165)" textAnchor="middle" fontSize="12" fill="#525252">
        {metricLabel} ({unit})
      </text>
      <g textAnchor="middle" fontSize="12" fill="#525252">
        {xTicks.map((t, i) => (
          <text key={i} x={x(t)} y={310}>{formatDate(new Date(t).toISOString(), false)}</text>
        ))}
      </g>
      <text x={420} y={342} textAnchor="middle" fontSize="12" fill="#525252">Date</text>
      <polyline
        fill="none"
        stroke="#6929c4"
        strokeWidth="2"
        strokeLinejoin="round"
        points={coords.map((c) => `${c.cx.toFixed(1)},${c.cy.toFixed(1)}`).join(' ')}
      />
      <g fill="#6929c4">
        {coords.map((c, i) => (
          <circle key={i} cx={c.cx} cy={c.cy} r={3} />
        ))}
      </g>
      <g>
        <rect x={labelX - 46} y={lastC.cy - 36} width={92} height={22} fill="#161616" />
        <text x={labelX} y={lastC.cy - 21} textAnchor="middle" fontSize="12" fill="#fff">
          {last.value} {unit}
        </text>
      </g>
    </svg>
  );
}
