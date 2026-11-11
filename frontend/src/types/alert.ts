export type AlertState = 'active' | 'acknowledged';

export interface WellnessAlert {
  id: string;
  metric_type: string;
  event_at: string;
  reason: string;
  rule_identifier: string;
  rule_version: string;
  state: AlertState | string;
  acknowledged_at: string | null;
  wellness_boundary: string;
}
