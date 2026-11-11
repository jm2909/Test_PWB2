import type { ChangeEvent, ReactNode } from 'react';

interface Props {
  id: string;
  labelText: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void;
  helperText?: string;
  children: ReactNode;
}

/** Labelled native select with optional helper text, matching the shared field styles. */
export function LabelledSelect({ id, labelText, value, onChange, helperText, children }: Props) {
  const helpId = `${id}-help`;
  return (
    <div className="mb-6">
      <label className="field-label" htmlFor={id}>
        {labelText}
      </label>
      <select
        className="field-input"
        id={id}
        name="category"
        value={value}
        aria-describedby={helperText ? helpId : undefined}
        onChange={onChange}
      >
        {children}
      </select>
      {helperText && (
        <p className="field-help" id={helpId}>
          {helperText}
        </p>
      )}
    </div>
  );
}
