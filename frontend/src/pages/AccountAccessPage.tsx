import { RegisterForm } from '../components/account/RegisterForm';
import { SignInForm } from '../components/account/SignInForm';

/** Combined "Account access" screen of wireframe_account_access.html: register and sign in side by side. */
export function AccountAccessPage() {
  return (
    <>
      <section className="border-b border-line pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Wellness support for your own data</p>
          <h1 id="page-title">Account access</h1>
          <p className="mt-2 max-w-[44rem] text-base leading-6 text-ink-secondary">
            Create an account or sign in to see only your own wellness information. Sapphire FitConnect
            supports general wellness; it does not diagnose or treat any condition.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-label="Register and sign in">
        <div className="page-grid grid gap-8 lg:grid-cols-2">
          <RegisterForm />
          <SignInForm />
        </div>
      </section>
    </>
  );
}
