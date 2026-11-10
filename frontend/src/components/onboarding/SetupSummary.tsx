import { STEP_LABELS } from '../../types/onboarding';
import type { OnboardingStep } from '../../types/onboarding';
import Notification from '../common/Notification';

const ORDER: OnboardingStep[] = ['profile', 'goal', 'device', 'consent'];

export default function SetupSummary({ remaining }: { remaining: OnboardingStep[] }) {
  const left = ORDER.filter((s) => remaining.includes(s));
  return (
    <aside aria-labelledby="sum-h">
      <div className="bg-layer p-4">
        <h2 id="sum-h" className="text-base font-semibold leading-[1.375rem]">
          Setup summary
        </h2>
        <ul className="mt-2 list-none p-0">
          {ORDER.map((step) => {
            const done = !remaining.includes(step);
            return (
              <li key={step} className="flex items-start gap-2 border-b border-border-subtle py-2">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  className={`mt-0.5 flex-none ${done ? 'fill-support-success' : 'fill-support-warning'}`}
                  aria-hidden="true"
                >
                  <path
                    d={
                      done
                        ? 'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z'
                        : 'M8,1C4.2,1,1,4.2,1,8s3.2,7,7,7s7-3.1,7-7S11.9,1,8,1z M7.5,4h1v5h-1z M8,12.2c-0.4,0-0.8-0.4-0.8-0.8s0.3-0.8,0.8-0.8c0.4,0,0.8,0.4,0.8,0.8S8.4,12.2,8,12.2z'
                    }
                  />
                </svg>
                <span>
                  {STEP_LABELS[step]}
                  <span className="block text-xs text-text-helper">
                    {done ? 'Completed' : 'Required step remaining'}
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      </div>
      <Notification kind="info" title="Welcome back" className="mt-4">
        {left.length > 0
          ? `You have ${left.length} required step${left.length === 1 ? '' : 's'} left: ${left
              .map((s) => STEP_LABELS[s])
              .join(', ')}. Your earlier answers are saved.`
          : 'All required steps are complete. Your answers are saved.'}
      </Notification>
      <p className="mt-4 text-xs text-text-helper">
        FitConnect supports everyday wellness. It does not diagnose or treat conditions.
      </p>
    </aside>
  );
}
