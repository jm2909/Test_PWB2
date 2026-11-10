export interface Alert {
  id: string;
  trend_name: string;
  urgency: 'routine' | 'urgent_direction';
  what_we_saw: string;
  recommended_next_action: string;
  care_direction: string | null;
  created_at: string;
}
