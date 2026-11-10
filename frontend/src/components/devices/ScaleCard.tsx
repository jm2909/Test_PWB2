import Notification from '../common/Notification';
import type { DeviceConnection } from '../../types/device';
import CategoryChips from './CategoryChips';

interface Props {
  connection?: DeviceConnection;
  failed: boolean;
  busy: boolean;
  paused: boolean;
  onPair: () => void;
}

export default function ScaleCard({ connection, failed, busy, paused, onPair }: Props) {
  const connected = connection?.status === 'connected' && !failed;
  const showFailure = failed || (!!connection && connection.status !== 'connected');
  return (
    <section className="bg-layer p-6 lg:col-span-8" aria-labelledby="scale-h">
      <h2 id="scale-h" className="text-xl">Sapphire smart scale</h2>
      <p className="mt-1 text-sm text-text-secondary">Provides weight and body fat percentage.</p>

      {connected && connection ? (
        <div className="mt-4 bg-background p-4">
          <p className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 16 16" className="fill-support-success" aria-hidden="true">
              <path d="M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z" />
            </svg>
            <strong>Connected</strong>
          </p>
          <p className="mt-2">Sapphire Scale S2, living room</p>
          <CategoryChips categories={connection.permitted_categories} />
        </div>
      ) : (
        <>
          {showFailure ? (
            <Notification kind="error" title="Scale not paired" role="alert" className="mt-4">
              <p>We could not pair your scale. Make sure it is powered on and within 2 metres.</p>
              <div className="mt-2 flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={onPair}
                  disabled={busy || paused}
                  className="inline-flex min-h-10 items-center bg-button-primary px-4 text-white disabled:opacity-50"
                >
                  Try again
                </button>
                <a href="#tips" className="text-link underline">Pairing tips</a>
              </div>
            </Notification>
          ) : (
            <>
              <ol className="mt-3 mb-4 list-none">
                {['Step on the scale so it wakes up.', 'Keep Bluetooth on for your phone or computer.', 'Select Pair scale below.'].map(
                  (step, i) => (
                    <li key={step} className="flex gap-3 py-2">
                      <span
                        className="inline-flex h-6 w-6 flex-none items-center justify-center rounded-full bg-[#161616] text-xs text-white"
                        aria-hidden="true"
                      >
                        {i + 1}
                      </span>
                      {step}
                    </li>
                  ),
                )}
              </ol>
              <button
                type="button"
                onClick={onPair}
                disabled={busy || paused}
                className="inline-flex min-h-12 items-center gap-8 bg-button-primary px-4 text-white disabled:opacity-50"
              >
                <span>Pair scale</span>
                <span aria-hidden="true">→</span>
              </button>
            </>
          )}
          {showFailure && (
            <p id="tips" className="mt-3 text-sm text-text-secondary">
              Pairing tips: replace the scale batteries if the display stays dark, and move away from other
              Bluetooth devices.
            </p>
          )}
        </>
      )}
    </section>
  );
}
