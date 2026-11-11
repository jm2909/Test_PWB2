export type ConsentDecision = 'granted' | 'withdrawn';

export type DataCategory = 'weight' | 'body_composition' | 'steps' | 'sleep_duration' | 'active_minutes';

export interface ConsentRequest {
  decision: ConsentDecision;
  notice_version: string;
  data_categories: DataCategory[];
  purpose: 'wellness_support';
}

export interface ConsentRecord {
  id: string;
  decision: ConsentDecision;
  notice_version: string;
  recorded_at: string;
  collection_allowed: boolean;
  data_rights_path: string | null;
}
