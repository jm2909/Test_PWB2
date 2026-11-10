export type GoalType =
  | 'weight_loss'
  | 'muscle_gain'
  | 'sleep_improvement'
  | 'blood_pressure_control'
  | 'other_supported';

export interface Goal {
  id: string;
  goal_type: GoalType;
  target_value: number;
  target_unit: string;
  status: string;
}

export interface GoalOption {
  type: GoalType;
  label: string;
  units: string[];
  help?: string;
}

export const WELLNESS_GOAL_OPTIONS: GoalOption[] = [
  { type: 'weight_loss', label: 'Weight loss', units: ['kg'] },
  { type: 'muscle_gain', label: 'Muscle gain', units: ['kg'] },
  { type: 'sleep_improvement', label: 'Sleep improvement', units: ['h'] },
  {
    type: 'blood_pressure_control',
    label: 'Blood-pressure control',
    units: ['mmHg'],
    help: 'A lifestyle wellness goal. Track your readings over time as part of your wellness routine. FitConnect does not give medical advice about blood pressure.',
  },
  { type: 'other_supported', label: 'Other wellness goal', units: ['kg', 'h', 'mmHg', 'min'] },
];

export function goalLabel(type: string): string {
  return WELLNESS_GOAL_OPTIONS.find((o) => o.type === type)?.label ?? type;
}
