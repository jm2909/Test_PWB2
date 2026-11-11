import { formatNumber } from '../../lib/format';

export interface ChartPoint {
  time: number;
  value: number;
}

interface Props {
  points: ChartPoint[];
  title: string;
  description: string;
  unitLabel: string;
  /** Gap (ms) above which the line is broken because no reading was recorded. */
  gapMs: number;
}

const W = 640;
const H = 260;
const LEFT = 56;
const RIGHT = 624;
const TOP = 20;
const BOTTOM = 220;
const dayFmt = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short' });

/** Static SVG line chart; lines are not drawn across gaps with no reading. */
export function TrendChart({ points, title, description, unitLabel, gapMs }: Props) {
  const times = points.map((p) => p.time);
  const values = points.map((p) => p.value);
  const minT = Math.min(...times);
  const maxT = Math.max(...times);
  let minV = Math.min(...values);
  let maxV = Math.max(...values);
  if (minV === maxV) {
    minV -= 1;
    maxV += 1;
  }
  const pad = (maxV - minV) * 0.1;
  minV -= pad;
  maxV += pad;
  const x = (t: number) => (maxT === minT ? (LEFT + RIGHT) / 2 : LEFT + ((t - minT) / (maxT - minT)) * (RIGHT - LEFT));
  const y = (v: number) => BOTTOM - ((v - minV) / (maxV - minV)) * (BOTTOM - TOP);

  const segments: ChartPoint[][] = [];
  points.forEach((p, i) => {
    if (i === 0 || p.time - points[i - 1].time > gapMs) segments.push([p]);
    else segments[segments.length - 1].push(p);
  });

  const ticks = [0, 1, 2, 3, 4].map((i) => minV + ((maxV - minV) * i) / 4);
  return (
    <figure className="border border-line-subtle bg-white p-4">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby="ch-t ch-d" className="block h-auto w-full">
        <title id="ch-t">{title}</title>
        <desc id="ch-d">{description}</desc>
        <g stroke="#e0e0e0" strokeWidth="1">
          {ticks.map((v) => (
            <line key={v} x1={LEFT} x2={RIGHT} y1={y(v)} y2={y(v)} stroke={v === ticks[0] ? '#8d8d8d' : '#e0e0e0'} />
          ))}
        </g>
        <g fill="#525252" fontSize="12">
          {ticks.map((v) => (
            <text key={v} x={LEFT - 8} y={y(v) + 4} textAnchor="end">
              {formatNumber(v, 1)}
            </text>
          ))}
          <text x={LEFT} y={244}>
            {dayFmt.format(new Date(minT))}
          </text>
          <text x={RIGHT} y={244} textAnchor="end">
            {dayFmt.format(new Date(maxT))}
          </text>
          <text x="14" y="130" transform="rotate(-90 14 130)" textAnchor="middle">
            {unitLabel}
          </text>
        </g>
        {segments
          .filter((s) => s.length > 1)
          .map((s) => (
            <polyline
              key={s[0].time}
              fill="none"
              stroke="#6929c4"
              strokeWidth="2"
              points={s.map((p) => `${x(p.time)},${y(p.value)}`).join(' ')}
            />
          ))}
        <g fill="#6929c4">
          {points.map((p) => (
            <circle key={p.time} cx={x(p.time)} cy={y(p.value)} r="3" />
          ))}
        </g>
      </svg>
      <div className="mt-2 flex flex-wrap gap-4 text-xs text-ink-secondary">
        <span>
          <i className="mr-2 inline-block h-3 w-3 bg-[#6929c4]" />
          {unitLabel}
        </span>
        <span>Gaps mean no reading was recorded; lines are not drawn across them.</span>
      </div>
    </figure>
  );
}
