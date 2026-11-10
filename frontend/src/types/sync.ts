import type { DeviceConnection } from './device';

export interface SyncSummary {
  new_readings: number;
  by_metric: Record<string, number>;
  duplicates: number;
}

export type SyncState = 'connected' | 'pending' | 'action_required' | 'failed' | 'revoked';

export const PROVIDER_NAMES: Record<string, string> = {
  sapphire_scale: 'Sapphire smart scale',
  wearable_platform_a: 'Wearable platform A',
  wearable_platform_b: 'Wearable platform B',
  wearable_platform_c: 'Wearable platform C',
  fitband: 'Wearable platform A, permissions',
};

export const METRIC_LABELS: Record<string, string> = {
  weight: 'Weight',
  body_fat: 'Body fat',
  resting_heart_rate: 'Heart rate',
  heart_rate: 'Heart rate',
  sleep_hours: 'Sleep',
  sleep_duration: 'Sleep',
  steps: 'Steps',
};

export function providerName(provider: string): string {
  return PROVIDER_NAMES[provider] ?? provider.replace(/_/g, ' ');
}

export function metricLabel(metric: string): string {
  return METRIC_LABELS[metric] ?? metric.replace(/_/g, ' ');
}

export interface SyncResult {
  connection: DeviceConnection;
  summary: SyncSummary | null;
  at: Date;
}

/** "Today, 07:42", "Yesterday, 21:10", "3 days ago" or "Never". */
export function formatLastSync(iso: string | null, now: Date = new Date()): string {
  if (!iso) return 'Never';
  const d = new Date(iso);
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  const day = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const diff = Math.round((day(now) - day(d)) / 86_400_000);
  if (diff <= 0) return `Today, ${time}`;
  if (diff === 1) return `Yesterday, ${time}`;
  return `${diff} days ago`;
}
