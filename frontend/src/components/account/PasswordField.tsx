import { useState } from 'react';

interface Props {
  id: string;
  label?: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete: 'new-password' | 'current-password';
  helper?: string;
  error?: string | null;
}

export default function PasswordField({
  id,
  label = 'Password',
  value,
  onChange,
  autoComplete,
  helper,
  error,
}: Props) {
  const [visible, setVisible] = useState(false);
  const describedBy = error ? `${id}-error` : helper ? `${id}-help` : undefined;
  return (
    <div className="mb-6">
      <label htmlFor={id} className="mb-2 block text-xs text-text-secondary">
        {label}
      </label>
      <div className="flex">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          autoComplete={autoComplete}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={`block h-10 w-full flex-1 border-0 border-b bg-field px-4 ${
            error ? 'border-b-transparent outline outline-2 -outline-offset-2 outline-support-error' : 'border-border-strong'
          }`}
        />
        <button
          type="button"
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
          onClick={() => setVisible((v) => !v)}
          className="flex w-10 items-center justify-center border-0 border-b border-border-strong bg-field text-text-primary"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" className="fill-current" aria-hidden="true">
            <path d="M15.5,7.8C14.3,4.7,11.3,2.6,8,2.5C4.7,2.6,1.7,4.7,0.5,7.8c0,0.1,0,0.2,0,0.3c1.2,3.1,4.1,5.2,7.5,5.3c3.3-0.1,6.3-2.2,7.5-5.3C15.5,8.1,15.5,7.9,15.5,7.8z M8,12.5c-2.7,0-5.4-2-6.5-4.5c1-2.5,3.8-4.5,6.5-4.5s5.4,2,6.5,4.5C13.4,10.5,10.6,12.5,8,12.5z M8,5C6.3,5,5,6.3,5,8s1.3,3,3,3s3-1.3,3-3S9.7,5,8,5z" />
          </svg>
        </button>
      </div>
      {helper && !error && (
        <p id={`${id}-help`} className="mt-1 text-xs text-text-helper">
          {helper}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="mt-1 flex items-start gap-1 text-xs text-text-error">
          <svg width="16" height="16" viewBox="0 0 16 16" className="fill-support-error" aria-hidden="true">
            <path d="M8,1C4.1,1,1,4.1,1,8s3.1,7,7,7s7-3.1,7-7S11.9,1,8,1z M10.7,11.5L4.5,5.3l0.8-0.8l6.2,6.2L10.7,11.5z" />
          </svg>
          <span>{error}</span>
        </p>
      )}
    </div>
  );
}
