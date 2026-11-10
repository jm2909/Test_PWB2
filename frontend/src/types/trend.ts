export type TrendMetric = 'weight' | 'body_fat' | 'sleep_duration' | 'resting_heart_rate' | 'steps';
export type TrendPeriod = 7 | 30 | 90 | 365;

export interface TrendPoint {
  observed_at: string;
  value: number;
}

export interface TrendResponse {
  metric_type: string;
  period_days: number;
  status: 'available' | 'insufficient_history';
  points: TrendPoint[];
  explanation: string;
  reading_count: number;
  source_label: string;
}

export interface MetricExplanation {
  status: 'available' | 'unavailable' | 'insufficient_history';
  direction: 'up' | 'down' | 'steady' | null;
  explanation: string;
  reading_count: number;
  source_label: string;
}

export interface MetricOption {
  value: TrendMetric;
  label: string;
  unit: string;
}

export const METRIC_OPTIONS: MetricOption[] = [
  { value: 'weight', label: 'Weight', unit: 'kg' },
  { value: 'body_fat', label: 'Body fat', unit: '%' },
  { value: 'sleep_duration', label: 'Sleep duration', unit: 'h' },
  { value: 'resting_heart_rate', label: 'Resting heart rate', unit: 'bpm' },
  { value: 'steps', label: 'Steps', unit: 'steps' },
];

export const PERIOD_OPTIONS: TrendPeriod[] = [7, 30, 90, 365];
