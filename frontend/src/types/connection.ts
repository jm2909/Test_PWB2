export type ConnectionStatus = 'current' | 'pending' | 'stale' | 'failed' | 'disconnected';

export type RecoveryAction = 'retry_sync' | 'retry' | 'contact_support' | 'retry_or_contact_support' | 'retry_or_disconnect';

/** One row of GET /v1/connections. */
export interface ConnectionItem {
  id: string;
  source: 'scale' | 'wearable';
  provider: string | null;
  display_label: string;
  status: ConnectionStatus;
  last_successful_sync_at: string | null;
  recovery_action: RecoveryAction | null;
}

export interface ScaleConnectRequest {
  device_identifier: string;
  device_label: string;
}

/** Response of POST /v1/connections/scale and the wearable callback. */
export interface ConnectionResult {
  id: string;
  source: string;
  external_identifier: string;
  status: ConnectionStatus;
  last_successful_sync_at: string | null;
  recovery_action: RecoveryAction | null;
  message: string | null;
  provider: string | null;
  authorization_state: string | null;
}

export interface WearableProvider {
  provider: string;
  display_name: string;
  authorization_mode: string;
}

export interface WearableAuthorization {
  connection_id: string;
  authorization_url: string;
  expires_at: string;
}

export interface WearableCallback {
  connection_id: string;
  state: string;
  code?: string;
  error?: string;
}
