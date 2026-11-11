export interface Insight {
  id: string;
  metric_type: string;
  observation_period: { start: string; end: string };
  observation: string;
  wellness_guidance: string;
  uncertainty: string;
  created_at: string;
}

export interface InsightFeedback {
  id: string;
  insight_id: string;
  useful: boolean;
  submitted_at: string;
}
