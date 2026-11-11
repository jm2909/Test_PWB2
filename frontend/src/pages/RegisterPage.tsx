import { RegisterForm } from '../components/account/RegisterForm';

export function RegisterPage() {
  return (
    <>
      <section className="border-b border-line pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Wellness support for your own data</p>
          <h1 id="page-title">Create your account</h1>
          <p className="mt-2 max-w-[44rem] text-base leading-6 text-ink-secondary">
            Create an account to see only your own wellness information. Sapphire FitConnect supports
            general wellness; it does not diagnose or treat any condition.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-label="Register">
        <div className="page-grid max-w-[44rem] lg:ml-0">
          <RegisterForm />
        </div>
      </section>
    </>
  );
}
