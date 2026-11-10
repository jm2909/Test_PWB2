import { STEP_LABELS } from '../../types/onboarding';
import type { OnboardingStep } from '../../types/onboarding';

const ORDER: OnboardingStep[] = ['profile', 'goal', 'device', 'consent'];
const OK =
  'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z';
const INFO =
  'M8.5,11 L8.5,6.5 L6.5,6.5 L6.5,7.5 L7.5,7.5 L7.5,11 L6,11 L6,12 L10,12 L10,11 Z M8,3.5 a0.8,0.8 0 1 0 0.01,0 Z M8,15 c-3.9,0 -7,-3.1 -7,-7 s3.1,-7 7,-7 s7,3.1 7,7 S11.9,15 8,15 Z M8,2 C4.7,2 2,4.7 2,8 s2.7,6 6,6 s6,-2.7 6,-6 S11.3,2 8,2 Z';

/** Done steps are green; the first remaining step is current (blue); later ones are neutral. */
export default function ProgressSteps({ remaining }: { remaining: OnboardingStep[] }) {
  const current = ORDER.find((s) => remaining.includes(s));
  return (
    <nav aria-label="Setup progress" className="mt-8">
      <ol className="mb-8 flex list-none flex-wrap p-0">
        {ORDER.map((step) => {
          const done = !remaining.includes(step);
          const isCurrent = step === current;
          const color = done ? 'border-support-success' : isCurrent ? 'border-link' : 'border-border-strong';
          const fill = done ? 'fill-support-success' : isCurrent ? 'fill-link' : 'fill-border-strong';
          return (
            <li
              key={step}
              aria-current={isCurrent ? 'step' : undefined}
              className={`min-w-[140px] flex-1 basis-[140px] border-t-[3px] pr-2 pt-2 ${color}`}
            >
              <span className="flex items-center gap-2 font-semibold">
                <svg width="16" height="16" viewBox="0 0 16 16" className={fill} aria-hidden="true">
                  <path d={done ? OK : INFO} />
                </svg>
                {STEP_LABELS[step]}
              </span>
              <span className="block pl-6 text-xs text-text-secondary">
                {done ? 'Complete' : isCurrent ? 'Current step' : 'Not started'}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
