import type { ReactNode } from 'react';
import type { ConsentPurpose, ConsentRecord, ConsentStatus } from '../../types/consent';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

/** "14 Nov 2026" in the viewer's local time zone. */
export function formatRecordedDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

interface Props {
  purpose: ConsentPurpose;
  title: string;
  description: string;
  meta: string;
  policyVersion: string;
  record?: ConsentRecord;
  disabled?: boolean;
  onChoose: (status: ConsentStatus) => void;
  children?: ReactNode;
}

export default function ConsentGroup({
  purpose,
  title,
  description,
  meta,
  policyVersion,
  record,
  disabled,
  onChoose,
  children,
}: Props) {
  const titleId = `${purpose}-title`;
  const chip = (status: ConsentStatus, label: string) => {
    const on = record?.status === status;
    return (
      <label
        className={`inline-flex min-h-10 items-center gap-2 border px-4 ${
          on ? 'border-[#161616] bg-[#161616] text-white' : 'border-border-strong'
        }`}
      >
        <input
          type="radio"
          name={purpose}
          checked={on}
          disabled={disabled}
          onChange={() => onChoose(status)}
        />
        {label}
      </label>
    );
  };
  return (
    <div role="group" aria-labelledby={titleId} className="mb-4 border border-border-subtle p-4">
      <div className="flex flex-wrap justify-between gap-2">
        <h3 id={titleId} className="text-base font-semibold leading-[1.375rem]">
          {title}
        </h3>
        <span className="inline-block bg-[#161616] px-2 py-0.5 text-xs text-white">
          Policy v{policyVersion}
        </span>
      </div>
      <p className="mt-2">{description}</p>
      <p className="mt-1 text-xs text-text-secondary">{meta}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {chip('accepted', 'Accept')}
        {chip('declined', 'Decline')}
      </div>
      {record && (
        <p className="mt-2 text-xs text-text-secondary" data-testid={`${purpose}-recorded`}>
          Recorded {formatRecordedDate(record.recorded_at)}, policy v{record.version}
        </p>
      )}
      {children}
    </div>
  );
}
