import type { ReactNode } from 'react';
import { Icon } from './Icon';
import type { IconName } from './Icon';

export type NoticeKind = 'error' | 'success' | 'warning' | 'info';

const STYLE: Record<NoticeKind, { box: string; icon: IconName; iconColor: string; role: 'alert' | 'status' }> = {
  error: { box: 'bg-danger-bg border-danger', icon: 'err', iconColor: 'text-danger', role: 'alert' },
  success: { box: 'bg-success-bg border-success', icon: 'ok', iconColor: 'text-success', role: 'status' },
  warning: { box: 'bg-warn-bg border-warn', icon: 'warn', iconColor: 'text-warn-icon', role: 'alert' },
  info: { box: 'bg-info-bg border-info', icon: 'info', iconColor: 'text-info', role: 'status' },
};

interface NoticeProps {
  kind: NoticeKind;
  title?: string;
  children?: ReactNode;
  /** Override the live-region role (e.g. a timeout warning that is a status). */
  role?: 'alert' | 'status';
}

export function Notice({ kind, title, children, role }: NoticeProps) {
  const s = STYLE[kind];
  return (
    <div className={`flex min-h-[3rem] items-start gap-4 border-l-[3px] px-4 py-3 ${s.box}`} role={role ?? s.role}>
      <Icon name={s.icon} size={20} className={`mt-0.5 ${s.iconColor}`} />
      <div className="space-y-1">
        {title && <p className="font-semibold">{title}</p>}
        {children && <div>{children}</div>}
      </div>
    </div>
  );
}
