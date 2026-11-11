import { SignInForm } from '../components/account/SignInForm';

export function LoginPage() {
  return (
    <>
      <section className="border-b border-line pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Wellness support for your own data</p>
          <h1 id="page-title">Account access</h1>
          <p className="mt-2 max-w-[44rem] text-base leading-6 text-ink-secondary">
            Sign in to see only your own wellness information. Sapphire FitConnect supports general
            wellness; it does not diagnose or treat any condition.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-label="Sign in">
        <div className="page-grid max-w-[44rem] lg:ml-0">
          <SignInForm />
        </div>
      </section>
    </>
  );
}
