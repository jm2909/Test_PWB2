export type OnboardingStatus = 'not_started' | 'in_progress' | 'complete';

export interface AccountUser {
  id: number;
  email: string;
  onboarding_status: OnboardingStatus | string;
}

export interface SessionResponse {
  access_token: string;
  token_type: 'bearer';
  expires_at: string;
  user: AccountUser;
}

export interface StoredSession {
  access_token: string;
  expires_at: string;
  user: AccountUser;
}
