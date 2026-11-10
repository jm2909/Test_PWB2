import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError, api, getStoredSession, storeSession } from '../lib/api-client';
import Header from '../components/layout/Header';
import { DISCLAIMER } from '../components/layout/Footer';
import Notification from '../components/common/Notification';
import ProgressSteps from '../components/onboarding/ProgressSteps';
import SetupSummary from '../components/onboarding/SetupSummary';
import ConsentGroup from '../components/onboarding/ConsentGroup';
import { DEVICE_OPTIONS, GOAL_OPTIONS } from '../types/onboarding';
import type { DeviceNextStep, OnboardingData, OnboardingUpdate } from '../types/onboarding';
import { POLICY_VERSION } from '../types/consent';
import type { ConsentListResponse, ConsentPurpose, ConsentRecord, ConsentStatus } from '../types/consent';

const FIELD = 'block h-10 w-full border-0 border-b border-border-strong bg-field px-4';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<OnboardingData | null>(null);
  const [consents, setConsents] = useState<Partial<Record<ConsentPurpose, ConsentRecord>>>({});
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [height, setHeight] = useState('');
  const [goal, setGoal] = useState('');
  const [device, setDevice] = useState<DeviceNextStep | ''>('');
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const applyServer = useCallback((next: OnboardingData) => {
    setData(next);
    const session = getStoredSession();
    if (session && session.user.onboarding_status !== next.status) {
      storeSession({ ...session, user: { ...session.user, onboarding_status: next.status } });
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [onboarding, list] = await Promise.all([
          api.get<OnboardingData>('/onboarding'),
          api.get<ConsentListResponse>('/consents'),
        ]);
        if (cancelled) return;
        applyServer(onboarding);
        setName(String(onboarding.profile.display_name ?? ''));
        setDob(String(onboarding.profile.date_of_birth ?? ''));
        setHeight(String(onboarding.profile.height_cm ?? ''));
        setGoal(onboarding.goal_intent);
        setDevice(onboarding.device_next_step);
        const byPurpose: Partial<Record<ConsentPurpose, ConsentRecord>> = {};
        for (const rec of list.latest) byPurpose[rec.purpose] = rec;
        setConsents(byPurpose);
      } catch {
        if (!cancelled) setLoadError('We could not load your setup. Try again.');
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, [applyServer]);

  /** Persist one step with PUT /onboarding. Device is required by the API, so wait for it. */
  async function persist(patch: { goal?: string; device?: DeviceNextStep | ''; profile?: boolean }) {
    if (!data) return null;
    const nextDevice = patch.device ?? device;
    if (nextDevice === '') {
      setNotice('Choose a device next step to save your other answers.');
      return null;
    }
    const body: OnboardingUpdate = {
      profile: { ...data.profile, display_name: name.trim(), date_of_birth: dob.trim(), height_cm: height.trim() },
      goal_intent: patch.goal ?? goal,
      device_next_step: nextDevice,
    };
    try {
      const saved = await api.put<OnboardingData>('/onboarding', body);
      applyServer(saved);
      setNotice(null);
      return saved;
    } catch (err) {
      setNotice(err instanceof ApiError ? err.detail : 'We could not save that answer. Try again.');
      return null;
    }
  }

  async function chooseConsent(purpose: ConsentPurpose, status: ConsentStatus) {
    try {
      const rec = await api.post<ConsentRecord>('/consents', { purpose, version: POLICY_VERSION, status });
      setConsents((prev) => ({ ...prev, [purpose]: rec }));
      setNotice(null);
      applyServer(await api.get<OnboardingData>('/onboarding'));
    } catch (err) {
      setNotice(err instanceof ApiError ? err.detail : 'We could not record that choice. Try again.');
    }
  }

  async function finish() {
    setBusy(true);
    try {
      const saved = await persist({});
      if (!saved) return;
      if (saved.remaining_steps.length > 0) {
        setNotice('Finish the remaining required steps to complete setup.');
        return;
      }
      navigate('/', { replace: true });
    } finally {
      setBusy(false);
    }
  }

  const remaining = data?.remaining_steps ?? [];
  const device_c = consents.device_processing;
  const insights_c = consents.personalized_insights;

  return (
    <>
      <a href="#main" className="skip">
        Skip to main content
      </a>
      <Header />
      <main id="main" className="px-4 pb-12 pt-8">
        <div className="mx-auto max-w-[99rem]">
          <h1 className="text-[2rem] leading-10">Set up FitConnect</h1>
          <p className="mt-2 max-w-3xl text-base leading-6 text-text-secondary">
            Four short steps. Your answers are saved as you go, so you can leave and pick up where you stopped.
          </p>
          {loadError && (
            <Notification kind="error" role="alert" title="Setup unavailable" className="mt-6">
              {loadError}
            </Notification>
          )}
          {!data && !loadError && (
            <p role="status" className="mt-6 text-text-secondary">
              Loading your setup…
            </p>
          )}
          {data && (
            <>
              <ProgressSteps remaining={remaining} />
              <div className="grid grid-cols-4 gap-8 sm:grid-cols-8 lg:grid-cols-16">
                <div className="col-span-full min-w-0 lg:col-span-10">
                  <section className="border border-border-subtle bg-white p-6" aria-labelledby="done-h">
                    <h2 id="done-h" className="text-xl leading-7">
                      Your saved answers
                    </h2>
                    <p className="mb-4 mt-1 text-xs text-text-helper">
                      Your answers are saved as you change them. You can review them before you continue.
                    </p>
                    <h3 className="mb-2 text-base font-semibold">1. Profile</h3>
                    <div className="mb-6 grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4">
                      <div>
                        <label htmlFor="p-name" className="mb-2 block text-xs text-text-secondary">
                          Display name
                        </label>
                        <input
                          id="p-name"
                          className={FIELD}
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          onBlur={() => void persist({})}
                        />
                      </div>
                      <div>
                        <label htmlFor="p-dob" className="mb-2 block text-xs text-text-secondary">
                          Date of birth
                        </label>
                        <input
                          id="p-dob"
                          className={FIELD}
                          value={dob}
                          onChange={(e) => setDob(e.target.value)}
                          onBlur={() => void persist({})}
                        />
                      </div>
                      <div>
                        <label htmlFor="p-ht" className="mb-2 block text-xs text-text-secondary">
                          Height (cm)
                        </label>
                        <input
                          id="p-ht"
                          inputMode="numeric"
                          className={FIELD}
                          value={height}
                          onChange={(e) => setHeight(e.target.value)}
                          onBlur={() => void persist({})}
                        />
                      </div>
                    </div>

                    <fieldset className="mb-6 border-0 p-0">
                      <legend className="mb-2 p-0 text-xs text-text-secondary">
                        2. What would you like to focus on?
                      </legend>
                      <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-2">
                        {GOAL_OPTIONS.map((o) => (
                          <label
                            key={o.value}
                            className={`block bg-layer p-4 ${
                              goal === o.value ? 'outline outline-1 outline-link' : ''
                            }`}
                          >
                            <input
                              type="radio"
                              name="intent"
                              className="mr-2"
                              checked={goal === o.value}
                              onChange={() => {
                                setGoal(o.value);
                                void persist({ goal: o.value });
                              }}
                            />
                            {o.label}
                          </label>
                        ))}
                      </div>
                      <p className="mt-1 text-xs text-text-helper">
                        Blood pressure is a lifestyle wellness focus. FitConnect does not give medical advice
                        about it.
                      </p>
                    </fieldset>

                    <fieldset className="mb-6 border-0 p-0">
                      <legend className="mb-2 p-0 text-xs text-text-secondary">3. Device next step</legend>
                      <div className="grid gap-2">
                        {DEVICE_OPTIONS.map((o) => (
                          <label
                            key={o.value}
                            className={`flex min-h-10 items-center gap-2 bg-layer px-4 py-2 ${
                              device === o.value ? 'outline outline-2 -outline-offset-2 outline-link' : ''
                            }`}
                          >
                            <input
                              type="radio"
                              name="dev"
                              checked={device === o.value}
                              onChange={() => {
                                setDevice(o.value);
                                void persist({ device: o.value });
                              }}
                            />
                            {o.label}
                          </label>
                        ))}
                      </div>
                    </fieldset>
                  </section>

                  <section className="mt-8 border border-border-subtle bg-white p-6" aria-labelledby="cons-h">
                    <h2 id="cons-h" className="text-xl leading-7">
                      4. Consent
                    </h2>
                    <p className="mb-4 mt-1 text-xs text-text-helper">
                      Each choice is separate. You can accept one and decline the other.
                    </p>
                    <ConsentGroup
                      purpose="device_processing"
                      title="Device data processing"
                      description="Process readings from my connected devices, such as weight, sleep, heart rate and activity, so they can appear in FitConnect."
                      meta="Purpose: device_processing. Used for wellness information only."
                      policyVersion={POLICY_VERSION}
                      record={device_c}
                      onChoose={(s) => void chooseConsent('device_processing', s)}
                    />
                    <ConsentGroup
                      purpose="personalized_insights"
                      title="Personalized insights"
                      description="Use my data to generate personal wellness insights, such as how your sleep or weight has changed over time."
                      meta="Purpose: personalized_insights. Insights describe trends and are not medical advice."
                      policyVersion={POLICY_VERSION}
                      record={insights_c}
                      onChoose={(s) => void chooseConsent('personalized_insights', s)}
                    >
                      {insights_c?.status === 'declined' && (
                        <Notification kind="warning" title="Insights will stay off" className="mt-4">
                          Without this, FitConnect will not generate personal wellness insights from your data.
                          You can change this choice later.
                        </Notification>
                      )}
                    </ConsentGroup>
                    {device_c?.status !== 'accepted' && (
                      <Notification kind="warning" title="If you decline device data processing">
                        Without this, FitConnect will not read data from your devices, so your dashboard will
                        stay empty.
                      </Notification>
                    )}
                    {notice && (
                      <Notification kind="error" role="alert" title="Not saved" className="mt-4">
                        {notice}
                      </Notification>
                    )}
                    <div className="mt-6 flex flex-wrap gap-4">
                      <button
                        type="button"
                        onClick={() => navigate(-1)}
                        className="inline-flex min-h-12 items-center border border-button-primary px-4 text-button-primary"
                      >
                        Back
                      </button>
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() => void finish()}
                        className="inline-flex min-h-12 min-w-[200px] items-center justify-between gap-4 bg-button-primary px-4 text-white disabled:opacity-60"
                      >
                        <span>Save and finish setup</span>
                        <svg width="16" height="16" viewBox="0 0 16 16" className="fill-current" aria-hidden="true">
                          <polygon points="9.3,3.7 13.1,7.5 1,7.5 1,8.5 13.1,8.5 9.3,12.3 10,13 15,8 10,3" />
                        </svg>
                      </button>
                    </div>
                  </section>
                </div>
                <div className="col-span-full min-w-0 lg:col-span-6">
                  <SetupSummary remaining={remaining} />
                </div>
              </div>
            </>
          )}
          <footer className="mt-12 border-t border-border-subtle pt-4 text-xs text-text-secondary">
            {DISCLAIMER}
          </footer>
        </div>
      </main>
    </>
  );
}
