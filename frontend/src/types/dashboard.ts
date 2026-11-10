export interface SignalGroup {
  key: string;
  group?: string;
  title: string;
  value: string | null;
  unit: string | null;
  details: string[];
  metrics?: Record<string, number | null>;
}

export interface SourceGap {
  key: string;
  group?: string;
  title: string;
  reason: string;
  recovery_action: string | null;
  link?: string | null;
}

export interface GoalSummary {
  id: string;
  goal_type: string;
  target_value: number;
  target_unit: string;
  status: string;
}

export interface DashboardResponse {
  display_name?: string;
  last_synced_at?: string | null;
  signal_groups: SignalGroup[];
  source_gaps: SourceGap[];
  active_goals: GoalSummary[];
  unread_alert_count?: number;
}

/** Tile titles as the wireframe names them (the goal group is "Goal signals"). */
export function tileTitle(key: string, title: string): string {
  return key === 'goals' ? 'Goal signals' : title;
}
