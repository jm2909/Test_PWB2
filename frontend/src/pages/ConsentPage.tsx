import { useCallback, useEffect, useState } from 'react';
import { ConsentForm, NOTICE_VERSION } from '../components/consent/ConsentForm';
import { ConsentStatus } from '../components/consent/ConsentStatus';
import { DataRightsForm } from '../components/consent/DataRightsForm';
import { DataRightsList } from '../components/consent/DataRightsList';
import { Notice } from '../components/ui/Notice';
import { getCurrentConsent, listDataRightsRequests } from '../lib/api-client';
import { ApiError } from '../types/api';
import type { ConsentRecord } from '../types/consent';
import type { DataRightsRequest } from '../types/dataRights';

export function ConsentPage() {
  const [consent, setConsent] = useState<ConsentRecord | null>(null);
  const [requests, setRequests] = useState<DataRightsRequest[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([getCurrentConsent(), listDataRightsRequests()])
      .then(([record, page]) => {
        if (!active) return;
        setConsent(record);
        setRequests(page.items);
        setLoaded(true);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof ApiError ? err.detail : 'This page could not be loaded. Try again.');
        setLoaded(true);
      });
    return () => {
      active = false;
    };
  }, []);

  const onCreated = useCallback((created: DataRightsRequest) => {
    setRequests((prev) => [created, ...prev]);
  }, []);

  return (
    <>
      <section className="border-b border-line pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Account settings</p>
          <h1 id="page-title">Privacy consent and data rights</h1>
          <p className="mt-2 max-w-[44rem] text-base leading-6 text-ink-secondary">
            Choose what Sapphire FitConnect may collect for wellness support, and ask for a copy of your data
            or for it to be deleted. Only you can see your requests.
          </p>
        </div>
      </section>

      {!loaded && (
        <p role="status" className="page-grid mt-8">
          Loading your privacy settings…
        </p>
      )}
      {error && (
        <div className="page-grid mt-8">
          <Notice kind="error" title="Could not load.">
            <p>{error}</p>
          </Notice>
        </div>
      )}

      {loaded && !error && (
        <>
          <section className="mt-8" aria-label="Consent">
            <div className="page-grid grid gap-8 lg:grid-cols-[10fr_6fr]">
              <div className="tile">
                <h2 id="consent-h" className="!mb-3 text-xl">
                  Privacy notice and consent
                </h2>
                <dl className="grid grid-cols-[minmax(8rem,12rem)_1fr] gap-x-4 gap-y-2">
                  <dt className="text-ink-secondary">Notice version</dt>
                  <dd className="m-0">{NOTICE_VERSION}</dd>
                  <dt className="text-ink-secondary">Purpose</dt>
                  <dd className="m-0">
                    Wellness support only: showing your readings, trends, and general wellness guidance. Not
                    used for diagnosis or treatment.
                  </dd>
                </dl>
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full min-w-[30rem] border-collapse">
                    <caption className="py-3 text-left font-semibold">
                      Data categories covered by this notice
                    </caption>
                    <thead>
                      <tr className="bg-surface-selected text-left">
                        <th scope="col" className="px-4 py-3 font-semibold">Category</th>
                        <th scope="col" className="px-4 py-3 font-semibold">What it includes</th>
                        <th scope="col" className="px-4 py-3 font-semibold">Why it is collected</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white">
                      <tr className="border-b border-line">
                        <th scope="row" className="px-4 py-3 text-left align-top font-normal">Body measurements</th>
                        <td className="px-4 py-3 align-top">Weight readings from your Sapphire scale</td>
                        <td className="px-4 py-3 align-top">Show your progress and trends</td>
                      </tr>
                      <tr className="border-b border-line">
                        <th scope="row" className="px-4 py-3 text-left align-top font-normal">Activity and sleep</th>
                        <td className="px-4 py-3 align-top">
                          Steps, active time, and sleep duration from an approved wearable
                        </td>
                        <td className="px-4 py-3 align-top">Show your daily wellness picture</td>
                      </tr>
                      <tr className="border-b border-line">
                        <th scope="row" className="px-4 py-3 text-left align-top font-normal">Account details</th>
                        <td className="px-4 py-3 align-top">Display name, email address, and your goals</td>
                        <td className="px-4 py-3 align-top">Keep your account and goals working</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <ConsentForm current={consent} onSaved={setConsent} />
              </div>
              <div>
                <ConsentStatus record={consent} />
              </div>
            </div>
          </section>

          <section className="mt-8" aria-label="Data rights">
            <div className="page-grid grid gap-8 lg:grid-cols-2">
              <div>
                <DataRightsForm onCreated={onCreated} />
              </div>
              <div>
                <DataRightsList items={requests} />
              </div>
            </div>
          </section>
        </>
      )}
    </>
  );
}
