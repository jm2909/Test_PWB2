export interface Account {
  id: string;
  email: string;
  display_name: string;
  next_step: 'consent_setup';
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_at: string;
  account: Account;
}

export interface RegisterRequest {
  display_name: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
