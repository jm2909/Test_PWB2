export type GoalCategory = 'weight_management' | 'fitness' | 'sleep_improvement' | 'general_wellness';
export type GoalState = 'active' | 'paused' | 'closed';
export type GoalMetric = 'weight' | 'steps' | 'sleep_duration';

export interface GoalCreateRequest {
  category: GoalCategory;
  metric_type: GoalMetric;
  target_value: number;
  target_unit: string;
  target_date: string;
}

export interface Goal {
  id: string;
  state: GoalState | string;
  category: GoalCategory | string;
  metric_type: string;
  /** Decimals are serialised as strings by the API. */
  target_value: string | number;
  target_unit: string;
  target_date: string;
  progress_status: 'available' | 'data_gap';
  current_value: string | number | null;
}
