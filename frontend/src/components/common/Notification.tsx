import type { ReactNode } from 'react';

export type NotificationKind = 'info' | 'error' | 'warning' | 'success';

const STYLES: Record<NotificationKind, string> = {
  info: 'border-support-info bg-notify-info',
  error: 'border-support-error bg-notify-error',
  warning: 'border-support-warning bg-notify-warning',
  success: 'border-support-success bg-notify-success',
};

const ICON_FILL: Record<NotificationKind, string> = {
  info: 'fill-support-info',
  error: 'fill-support-error',
  warning: 'fill-support-warning',
  success: 'fill-support-success',
};

const ICON_PATH: Record<NotificationKind, string> = {
  info: 'M8.5,11 L8.5,6.5 L6.5,6.5 L6.5,7.5 L7.5,7.5 L7.5,11 L6,11 L6,12 L10,12 L10,11 Z M8,3.5 a0.8,0.8 0 1 0 0.01,0 Z M8,15 c-3.9,0 -7,-3.1 -7,-7 s3.1,-7 7,-7 s7,3.1 7,7 S11.9,15 8,15 Z M8,2 C4.7,2 2,4.7 2,8 s2.7,6 6,6 s6,-2.7 6,-6 S11.3,2 8,2 Z',
  error: 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z',
  warning: 'M8,1C4.2,1,1,4.2,1,8s3.2,7,7,7s7-3.1,7-7S11.9,1,8,1z M7.5,4h1v5h-1z M8,12.2c-0.4,0-0.8-0.4-0.8-0.8s0.3-0.8,0.8-0.8c0.4,0,0.8,0.4,0.8,0.8S8.4,12.2,8,12.2z',
  success: 'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z',
};

interface Props {
  kind: NotificationKind;
  title: string;
  children?: ReactNode;
  role?: 'alert' | 'status' | 'note';
  className?: string;
}

export default function Notification({ kind, title, children, role = 'status', className = '' }: Props) {
  return (
    <div role={role} className={`flex gap-3 border-l-[3px] px-4 py-3 ${STYLES[kind]} ${className}`}>
      <svg
        className={`mt-0.5 flex-none ${ICON_FILL[kind]}`}
        width="16"
        height="16"
        viewBox="0 0 16 16"
        aria-hidden="true"
      >
        <path d={ICON_PATH[kind]} />
      </svg>
      <div>
        <strong className="block font-semibold">{title}</strong>
        {children}
      </div>
    </div>
  );
}
