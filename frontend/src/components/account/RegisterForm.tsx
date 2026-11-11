import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { Icon } from '../ui/Icon';
import { Notice } from '../ui/Notice';
import { api } from '../../lib/api-client';
import { useAuth } from '../../lib/auth-context';
import { ROUTES } from '../../routes';
import { ApiError } from '../../types/api';
import type { Account, RegisterRequest } from '../../types/auth';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface FieldErrors {
  display_name?: string;
  email?: string;
  password?: string;
}

function validate(form: RegisterRequest): FieldErrors {
  const errors: FieldErrors = {};
  if (!form.display_name.trim() || form.display_name.trim().length > 100) {
    errors.display_name = 'Enter a display name of 1 to 100 characters.';
  }
  if (!EMAIL_PATTERN.test(form.email.trim())) {
    errors.email = 'Enter a valid email address, such as name@example.com.';
  }
  if (form.password.length < 12 || form.password.length > 128) {
    errors.password = 'Password must be between 12 and 128 characters.';
  }
  return errors;
}

function FieldError({ id, message }: { id: string; message: string }) {
  return (
    <p className="mt-1 flex items-start gap-1 text-xs text-danger" id={id}>
      <Icon name="err" size={16} className="flex-none text-danger" />
      <span>{message}</span>
    </p>
  );
}

/** The "Create your account" tile of the account-access wireframe, with all its states. */
export function RegisterForm() {
  const { user, login } = useAuth();
  const registeredRef = useRef(false);
  const [form, setForm] = useState<RegisterRequest>({ display_name: '', email: '', password: '' });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [apiError, setApiError] = useState<ApiError | null>(null);
  const [created, setCreated] = useState<Account | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to={registeredRef.current ? ROUTES.consent : ROUTES.dashboard} replace />;
  }

  const set = (key: keyof RegisterRequest) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setApiError(null);
    setCreated(null);
    const found = validate(form);
    setErrors(found);
    if (Object.keys(found).length > 0) return;
    setBusy(true);
    try {
      const credentials = { email: form.email.trim(), password: form.password };
      const account = await api.post<Account>('/v1/auth/accounts', {
        display_name: form.display_name.trim(),
        ...credentials,
      });
      setCreated(account);
      setForm({ display_name: '', email: '', password: '' });
      // Continue straight to consent setup; if sign-in fails the notice offers a sign-in link.
      registeredRef.current = true;
      try {
        await login(credentials);
      } catch {
        registeredRef.current = false;
      }
    } catch (err) {
      setApiError(err instanceof ApiError ? err : new ApiError(0, 'Registration failed. Try again.'));
    } finally {
      setBusy(false);
    }
  };

  const duplicate = apiError?.status === 400;

  return (
    <div className="tile">
      <h2 id="reg-h" className="!mb-3 text-base font-semibold">
        Create your account
      </h2>
      <form noValidate aria-labelledby="reg-h" onSubmit={onSubmit}>
        <div className="mb-6">
          <label className="field-label" htmlFor="reg-name">
            Display name
          </label>
          <input
            className="field-input"
            id="reg-name"
            name="display_name"
            type="text"
            autoComplete="name"
            value={form.display_name}
            onChange={set('display_name')}
            aria-invalid={errors.display_name ? 'true' : undefined}
            aria-describedby={errors.display_name ? 'reg-name-err' : 'reg-name-help'}
          />
          {errors.display_name ? (
            <FieldError id="reg-name-err" message={errors.display_name} />
          ) : (
            <p className="field-help" id="reg-name-help">
              Shown in the app header after you sign in.
            </p>
          )}
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="reg-email">
            Email address
          </label>
          <input
            className="field-input"
            id="reg-email"
            name="email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={set('email')}
            aria-invalid={errors.email ? 'true' : undefined}
            aria-describedby={errors.email ? 'reg-email-err' : undefined}
          />
          {errors.email && <FieldError id="reg-email-err" message={errors.email} />}
        </div>
        <div className="mb-6">
          <label className="field-label" htmlFor="reg-pw">
            Password
          </label>
          <input
            className="field-input"
            id="reg-pw"
            name="password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            onChange={set('password')}
            aria-invalid={errors.password ? 'true' : undefined}
            aria-describedby={errors.password ? 'reg-pw-help reg-pw-err' : 'reg-pw-help'}
          />
          <p className="field-help" id="reg-pw-help">
            Use 12 to 128 characters. Your password is never shown or repeated back to you.
          </p>
          {errors.password && <FieldError id="reg-pw-err" message={errors.password} />}
        </div>
        {apiError && (
          <div className="mb-4">
            <Notice kind="error" title="Account not created.">
              <p>
                {duplicate
                  ? 'An account with this email address already exists. Sign in instead, or use a different email address.'
                  : apiError.detail}
              </p>
            </Notice>
          </div>
        )}
        {created && (
          <div className="mb-4">
            <Notice kind="success" title="Account created.">
              <p>
                Next step: review the privacy notice and choose your consent before connecting any scale or
                wearable.
              </p>
              <p>
                <Link to={ROUTES.login}>Sign in to set up privacy consent</Link>
              </p>
            </Notice>
          </div>
        )}
        <button className="btn" type="submit" disabled={busy}>
          Create account
        </button>
      </form>
      <p className="field-help mt-4">
        Already registered? <Link to={ROUTES.login}>Sign in</Link>
      </p>
    </div>
  );
}
