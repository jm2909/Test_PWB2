import type { ConnectionStatus } from './connection';

export interface DashboardMeasurement {
  metric_type: string;
  /** Decimals are serialised as strings by the API. */
  value: string | number;
  unit: string;
  source: string;
  captured_at: string;
  status: 'current' | 'stale';
}

export interface DashboardSourceStatus {
  id: string;
  source: 'scale' | 'wearable' | string;
  provider: string;
  display_label: string;
  status: ConnectionStatus;
  last_successful_sync_at: string | null;
}

export interface DashboardAlert {
  id: string;
  metric_type: string;
  event_at: string;
  reason: string;
  state: string;
  acknowledged_at: string | null;
  wellness_boundary: string;
}

export interface DashboardGoal {
  id: string;
  category: string;
  metric_type: string;
  target_value: string | number;
  target_unit: string;
  target_date: string;
  state: string;
  progress_status: 'available' | 'data_gap' | string;
  current_value: string | number | null;
}

export interface DashboardInsightItem {
  id: string | null;
  metric_type: string;
  status: 'available' | 'insufficient_data';
  observation_period_start: string | null;
  observation_period_end: string | null;
  observation: string;
  wellness_guidance: string;
  uncertainty: string;
}

export interface UnavailableCategory {
  metric_type: string;
  status: 'unavailable';
}

export interface DashboardData {
  measurements: DashboardMeasurement[];
  source_statuses: DashboardSourceStatus[];
  alerts: DashboardAlert[];
  goals: DashboardGoal[];
  insights: DashboardInsightItem[];
  unavailable_categories: UnavailableCategory[];
}
