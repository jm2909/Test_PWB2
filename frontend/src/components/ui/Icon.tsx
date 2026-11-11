export type IconName = 'ok' | 'warn' | 'err' | 'info' | 'pending' | 'off';

const PATHS: Record<IconName, { viewBox: string; d?: string }> = {
  ok: {
    viewBox: '0 0 16 16',
    d: 'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z',
  },
  warn: {
    viewBox: '0 0 16 16',
    d: 'M8,1C4.2,1,1,4.2,1,8s3.2,7,7,7s7-3.1,7-7S11.9,1,8,1z M7.5,4h1v5h-1C7.5,9,7.5,4,7.5,4z M8,12.2c-0.4,0-0.8-0.4-0.8-0.8s0.3-0.8,0.8-0.8c0.4,0,0.8,0.4,0.8,0.8S8.4,12.2,8,12.2z',
  },
  err: {
    viewBox: '0 0 16 16',
    d: 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z',
  },
  info: {
    viewBox: '0 0 16 16',
    d: 'M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M8.75,12H7.25V7.25h1.5V12z M8,6.25c-0.55,0-1-0.45-1-1s0.45-1,1-1s1,0.45,1,1S8.55,6.25,8,6.25z',
  },
  pending: {
    viewBox: '0 0 32 32',
    d: 'M7.7,4.7a14.7,14.7,0,0,0-3,3.1L6.3,9A13.26,13.26,0,0,1,8.9,6.3Z M4.6,12.3l-1.9-.6A12.51,12.51,0,0,0,2,16H4A11.48,11.48,0,0,1,4.6,12.3Z M2.7,20.4a14.4,14.4,0,0,0,2,3.9l1.6-1.2a12.89,12.89,0,0,1-1.7-3.3Z M7.8,27.3a14.4,14.4,0,0,0,3.9,2l.6-1.9A12.89,12.89,0,0,1,9,25.7Z M11.7,2.7l.6,1.9A11.48,11.48,0,0,1,16,4V2A12.51,12.51,0,0,0,11.7,2.7Z M24.2,27.3a15.18,15.18,0,0,0,3.1-3.1L25.7,23A11.53,11.53,0,0,1,23,25.7Z M27.4,19.7l1.9.6A15.47,15.47,0,0,0,30,16H28A11.48,11.48,0,0,1,27.4,19.7Z M29.2,11.6a14.4,14.4,0,0,0-2-3.9L25.6,8.9a12.89,12.89,0,0,1,1.7,3.3Z M24.1,4.6a14.4,14.4,0,0,0-3.9-2l-.6,1.9a12.89,12.89,0,0,1,3.3,1.7Z M20.3,29.3l-.6-1.9A11.48,11.48,0,0,1,16,28v2A21.42,21.42,0,0,0,20.3,29.3Z',
  },
  off: { viewBox: '0 0 16 16' },
};

/** Decorative status icon (always paired with visible text). */
export function Icon({ name, size = 16, className }: { name: IconName; size?: number; className?: string }) {
  const icon = PATHS[name];
  return (
    <svg
      width={size}
      height={size}
      viewBox={icon.viewBox}
      aria-hidden="true"
      focusable="false"
      className={`flex-none ${className ?? ''}`}
      fill="currentColor"
    >
      {icon.d ? (
        <path d={icon.d} />
      ) : (
        <circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" strokeWidth="1.5" />
      )}
    </svg>
  );
}
