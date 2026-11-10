export type ConsentPurpose = 'device_processing' | 'personalized_insights';
export type ConsentStatus = 'accepted' | 'declined';

export interface ConsentRecord {
  id: string;
  purpose: ConsentPurpose;
  version: string;
  status: ConsentStatus;
  recorded_at: string;
}

export interface ConsentListResponse {
  items: ConsentRecord[];
  total: number;
  latest: ConsentRecord[];
}

export const POLICY_VERSION = '1.0';
