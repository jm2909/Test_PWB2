import type { Alert } from '../../types/alert';

const ICON_WARN =
  'M8,1C4.2,1,1,4.2,1,8s3.2,7,7,7s7-3.1,7-7S11.9,1,8,1z M7.5,4h1v5h-1z M8,12.2c-0.4,0-0.8-0.4-0.8-0.8s0.3-0.8,0.8-0.8c0.4,0,0.8,0.4,0.8,0.8S8.4,12.2,8,12.2z';
const ICON_ERR =
  'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z';

export default function AlertCard({ alert }: { alert: Alert }) {
  const urgent = alert.urgency === 'urgent_direction';
  return (
    <div
      role={urgent ? 'alert' : 'status'}
      data-testid={urgent ? 'alert-urgent' : 'alert-routine'}
      className={`flex gap-3 border-l-[3px] p-4 ${urgent ? 'border-support-error bg-notify-error' : 'border-support-warning bg-notify-warning'}`}
    >
      <svg
        className={`mt-0.5 flex-none ${urgent ? 'fill-support-error' : 'fill-support-warning'}`}
        width="20"
        height="20"
        viewBox="0 0 16 16"
        aria-hidden="true"
      >
        <path d={urgent ? ICON_ERR : ICON_WARN} />
      </svg>
      <div>
        <span className="mb-1 inline-flex text-xs font-semibold">{urgent ? 'Needs attention' : 'Routine'}</span>
        <strong className="block text-base font-semibold">{alert.trend_name}</strong>
        <dl className="mt-3 grid grid-cols-[minmax(120px,160px)_1fr] gap-x-4 gap-y-1">
          <dt className="text-text-secondary">What we saw</dt>
          <dd>{alert.what_we_saw}</dd>
          {!urgent && (
            <>
              <dt className="text-text-secondary">Suggested next step</dt>
              <dd>{alert.recommended_next_action}</dd>
            </>
          )}
        </dl>
        {urgent && alert.care_direction && (
          <p className="mt-3 border-t border-[#f1c0c3] pt-3">
            <strong className="block text-sm font-semibold">Where to turn</strong>
            {alert.care_direction}
          </p>
        )}
      </div>
    </div>
  );
}
