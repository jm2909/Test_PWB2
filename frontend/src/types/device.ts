export type DeviceProvider =
  | 'sapphire_scale'
  | 'wearable_platform_a'
  | 'wearable_platform_b'
  | 'wearable_platform_c';

export interface DeviceConnection {
  id: string;
  provider: string;
  status: string;
  permitted_categories: string[];
  last_successful_sync_at: string | null;
  failure_reason: string | null;
  recovery_action: string | null;
  last_sync_summary: { new_readings: number; by_metric: Record<string, number>; duplicates: number } | null;
}

export interface WearableInfo {
  provider: DeviceProvider;
  name: string;
  /** Categories shown before the user authorizes. */
  categories: string[];
}

export const WEARABLES: WearableInfo[] = [
  { provider: 'wearable_platform_a', name: 'Wearable platform A', categories: ['sleep', 'heart_rate', 'activity'] },
  {
    provider: 'wearable_platform_b',
    name: 'Wearable platform B',
    categories: ['sleep', 'heart_rate', 'activity', 'weight'],
  },
  { provider: 'wearable_platform_c', name: 'Wearable platform C', categories: ['sleep', 'activity'] },
];

export const CATEGORY_LABELS: Record<string, string> = {
  weight: 'Weight',
  body_fat: 'Body fat %',
  sleep: 'Sleep',
  heart_rate: 'Heart rate',
  activity: 'Activity',
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category.replace(/_/g, ' ');
}
