export interface Insight {
  id: string | null;
  status: 'published' | 'suppressed';
  observed_trend: string | null;
  wellness_implication: string | null;
  suppression_reason: string | null;
}

export interface Recommendation {
  status: 'available' | 'none';
  action_text: string | null;
  reason_text: string | null;
  insight_id: string | null;
  suggested_goal_type: string | null;
}
