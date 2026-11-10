import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { DISCLAIMER } from '../layout/Footer';
import Notification from '../common/Notification';

export type AuthTab = 'create' | 'signin';

const CHECK =
  'M8,1C4.1,1,1,4.1,1,8c0,3.9,3.1,7,7,7s7-3.1,7-7C15,4.1,11.9,1,8,1z M7,11L4.3,8.3l0.9-0.8L7,9.3l4-3.9l0.9,0.8L7,11z';
const ITEMS = [
  'Connect a Sapphire smart scale or a supported wearable.',
  'See your trends in plain language, with the reasons behind them.',
  'Set a wellness goal and get suggestions that fit your data.',
];

export function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" className="fill-current" aria-hidden="true">
      <polygon points="9.3,3.7 13.1,7.5 1,7.5 1,8.5 13.1,8.5 9.3,12.3 10,13 15,8 10,3" />
    </svg>
  );
}

/** Wireframe 01 shell: brand-only header, intro column, card with Create account / Sign in tabs. */
export default function AuthTabs({ active, children }: { active: AuthTab; children: ReactNode }) {
  const tab = (id: AuthTab, to: string, label: string) => (
    <Link
      role="tab"
      id={`t-${id}`}
      to={to}
      replace
      aria-selected={active === id}
      aria-controls={`${id}-panel`}
      tabIndex={active === id ? 0 : -1}
      className={`border-b-[3px] px-4 pb-[9px] pt-3 no-underline ${
        active === id
          ? 'border-link font-semibold text-text-primary'
          : 'border-transparent text-text-secondary'
      }`}
    >
      {label}
    </Link>
  );
  return (
    <>
      <a href="#main" className="skip">
        Skip to main content
      </a>
      <header className="flex h-12 items-center border-b border-[#393939] bg-[#161616] px-4 text-[#f4f4f4]">
        <span className="font-semibold tracking-[.1px]">
          <span className="font-normal">Sapphire</span> FitConnect
        </span>
      </header>
      <main id="main" className="px-4 py-12">
        <div className="mx-auto grid max-w-[99rem] grid-cols-4 gap-8 sm:grid-cols-8 lg:grid-cols-16">
          <section className="col-span-full lg:col-span-6" aria-labelledby="intro-h">
            <h1 id="intro-h" className="text-[2rem] leading-10">
              Understand your everyday wellness in one place
            </h1>
            <p className="mt-4 text-base leading-6 text-text-secondary">
              Sapphire FitConnect brings together readings from your smart scale and wearable so you can
              see how your weight, sleep, heart rate and activity change over time.
            </p>
            <ul className="mt-6 list-none p-0">
              {ITEMS.map((item) => (
                <li key={item} className="flex gap-3 py-2">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    className="mt-0.5 flex-none fill-support-success"
                    aria-hidden="true"
                  >
                    <path d={CHECK} />
                  </svg>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <Notification kind="info" role="note" title="Wellness information only" className="mt-8">
              FitConnect supports everyday wellness. It does not diagnose or treat conditions.
            </Notification>
            <p className="mt-4 text-xs text-text-helper">Your health information is hidden until you sign in.</p>
          </section>
          <section className="col-span-full lg:col-span-8 lg:col-start-9" aria-labelledby="form-h">
            <div className="border border-border-subtle bg-white p-6">
              <h2 id="form-h" className="mb-4 text-xl leading-7">
                {active === 'create' ? 'Create your account' : 'Sign in to your account'}
              </h2>
              <div
                role="tablist"
                aria-label="Account options"
                className="-mt-2 mb-6 flex border-b border-border-subtle"
              >
                {tab('create', '/register', 'Create account')}
                {tab('signin', '/login', 'Sign in')}
              </div>
              <div role="tabpanel" aria-labelledby={`t-${active}`} id={`${active}-panel`}>
                {children}
              </div>
            </div>
          </section>
        </div>
        <footer className="mx-auto mt-12 max-w-[99rem] border-t border-border-subtle pt-4 text-xs text-text-secondary">
          {DISCLAIMER}
        </footer>
      </main>
    </>
  );
}
