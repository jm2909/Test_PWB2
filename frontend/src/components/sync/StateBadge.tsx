const ICONS = {
  ok: 'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z',
  pend: 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M8,13.5c-3,0-5.5-2.5-5.5-5.5S5,2.5,8,2.5s5.5,2.5,5.5,5.5S11,13.5,8,13.5z M8.5,4h-1v4.5l3,1.8l0.5-0.8L8.5,8z',
  warn: 'M8,1C4.2,1,1,4.2,1,8s3.2,7,7,7s7-3.1,7-7S11.9,1,8,1z M7.5,4h1v5h-1z M8,12.2c-0.4,0-0.8-0.4-0.8-0.8s0.3-0.8,0.8-0.8c0.4,0,0.8,0.4,0.8,0.8S8.4,12.2,8,12.2z',
  err: 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z',
};

interface Kind {
  icon: keyof typeof ICONS;
  fill: string;
  label: string;
}

const CONNECTED: Kind = { icon: 'ok', fill: 'fill-support-success', label: 'Connected' };
const PENDING: Kind = { icon: 'pend', fill: 'fill-support-info', label: 'Pending' };
const ACTION: Kind = { icon: 'warn', fill: 'fill-[#8e6a00]', label: 'Action required' };
const FAILED: Kind = { icon: 'err', fill: 'fill-support-error', label: 'Failed' };
const REVOKED: Kind = { icon: 'err', fill: 'fill-support-error', label: 'Revoked' };

const KINDS: Record<string, Kind> = {
  connected: CONNECTED,
  pending: PENDING,
  action_required: ACTION,
  failed: FAILED,
  revoked: REVOKED,
};

function Icon({ kind }: { kind: Kind }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" className={kind.fill} aria-hidden="true">
      <path d={ICONS[kind.icon]} />
    </svg>
  );
}

export function StateKey() {
  const legend: Kind[] = [CONNECTED, PENDING, ACTION, { ...FAILED, label: 'Failed or revoked' }];
  return (
    <ul aria-label="State key" className="mt-4 flex flex-wrap gap-x-6 gap-y-2">
      {legend.map((k) => (
        <li key={k.label} className="inline-flex items-center gap-1">
          <Icon kind={k} />
          {k.label}
        </li>
      ))}
    </ul>
  );
}

export default function StateBadge({ status }: { status: string }) {
  const k = KINDS[status] ?? PENDING;
  return (
    <span className="inline-flex items-center gap-1 whitespace-nowrap">
      <Icon kind={k} />
      {k.label}
    </span>
  );
}
