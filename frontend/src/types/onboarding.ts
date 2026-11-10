export type DeviceNextStep = 'scale' | 'wearable' | 'later';
export type OnboardingStep = 'profile' | 'goal' | 'device' | 'consent';

export interface OnboardingProfile {
  display_name?: string;
  date_of_birth?: string;
  height_cm?: string;
  [key: string]: unknown;
}

export interface OnboardingData {
  profile: OnboardingProfile;
  goal_intent: string;
  device_next_step: DeviceNextStep | '';
  status: 'not_started' | 'in_progress' | 'complete';
  remaining_steps: OnboardingStep[];
}

export interface OnboardingUpdate {
  profile: OnboardingProfile;
  goal_intent: string;
  device_next_step: DeviceNextStep;
}

export const GOAL_OPTIONS: { value: string; label: string }[] = [
  { value: 'lose_weight', label: 'Lose weight' },
  { value: 'build_muscle', label: 'Build muscle' },
  { value: 'sleep_better', label: 'Sleep better' },
  { value: 'manage_blood_pressure', label: 'Manage blood pressure' },
];

export const DEVICE_OPTIONS: { value: DeviceNextStep; label: string }[] = [
  { value: 'scale', label: 'Connect my Sapphire smart scale' },
  { value: 'wearable', label: 'Connect a smartwatch or wearable' },
  { value: 'later', label: "I'll do this later" },
];

export const STEP_LABELS: Record<OnboardingStep, string> = {
  profile: 'Profile',
  goal: 'Goal intent',
  device: 'Device next step',
  consent: 'Consent',
};
