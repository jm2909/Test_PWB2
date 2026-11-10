import { METRIC_OPTIONS, PERIOD_OPTIONS } from '../../types/trend';
import type { TrendMetric, TrendPeriod } from '../../types/trend';

interface Props {
  metric: TrendMetric;
  period: TrendPeriod;
  onMetric: (m: TrendMetric) => void;
  onPeriod: (p: TrendPeriod) => void;
}

export default function MetricControls({ metric, period, onMetric, onPeriod }: Props) {
  return (
    <form className="mb-6 flex flex-wrap items-end gap-6" aria-label="Trend options" onSubmit={(e) => e.preventDefault()}>
      <div>
        <label htmlFor="metric" className="mb-2 block text-xs text-text-secondary">Metric</label>
        <select
          id="metric"
          aria-describedby="metric-h"
          value={metric}
          onChange={(e) => onMetric(e.target.value as TrendMetric)}
          className="block h-10 min-w-[220px] border-0 border-b border-[#8d8d8d] bg-layer px-4 text-text-primary"
        >
          {METRIC_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <p id="metric-h" className="mt-1 text-xs text-[#6f6f6f]">
          Weight, body fat, sleep duration, resting heart rate, steps
        </p>
      </div>
      <div>
        <span id="per-l" className="mb-2 block text-xs text-text-secondary">Period</span>
        <div role="group" aria-labelledby="per-l" className="inline-flex flex-wrap bg-layer">
          {PERIOD_OPTIONS.map((p) => (
            <button
              key={p}
              type="button"
              aria-pressed={p === period}
              onClick={() => onPeriod(p)}
              className={`min-h-10 border-r border-white px-4 ${p === period ? 'bg-[#161616] text-white' : 'bg-transparent text-text-primary'}`}
            >
              {p} days
            </button>
          ))}
        </div>
      </div>
    </form>
  );
}
