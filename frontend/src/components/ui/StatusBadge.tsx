import { Icon } from './Icon';
import type { IconName } from './Icon';

export type StatusKind = 'current' | 'stale' | 'failed' | 'pending' | 'active' | 'acknowledged' | 'unavailable';

const CONFIG: Record<StatusKind, { label: string; icon: IconName; color: string }> = {
  current: { label: 'Current', icon: 'ok', color: 'text-success' },
  stale: { label: 'Stale', icon: 'warn', color: 'text-warn-icon' },
  failed: { label: 'Failed', icon: 'err', color: 'text-danger' },
  pending: { label: 'Pending', icon: 'pending', color: 'text-info' },
  active: { label: 'Active', icon: 'warn', color: 'text-warn-icon' },
  acknowledged: { label: 'Acknowledged', icon: 'ok', color: 'text-ink-helper' },
  unavailable: { label: 'Unavailable', icon: 'off', color: 'text-ink-helper' },
};

/** Status shown as icon + text, never colour alone. */
export function StatusBadge({ status, label }: { status: StatusKind; label?: string }) {
  const cfg = CONFIG[status];
  return (
    <span className="inline-flex items-center gap-2" data-status={status}>
      <Icon name={cfg.icon} className={cfg.color} />
      <span>{label ?? cfg.label}</span>
    </span>
  );
}
