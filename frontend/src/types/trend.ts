export type TrendMetric = 'weight' | 'steps' | 'sleep_duration';
export type TrendRange = '7d' | '30d' | '90d' | '365d';

export interface TrendPoint {
  captured_at: string;
  /** Decimal serialised by the API; may arrive as a string. */
  value: number | string;
}

export interface TrendResponse {
  metric_type: string;
  unit: string;
  range: TrendRange;
  range_label: string;
  points: TrendPoint[];
  status: 'available' | 'insufficient_data';
  explanation: string | null;
}
