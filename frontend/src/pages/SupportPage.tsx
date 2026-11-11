import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SupportForm } from '../components/support/SupportForm';
import { Notice } from '../components/ui/Notice';
import { StatusBadge } from '../components/ui/StatusBadge';
import { formatDateTime } from '../lib/format';
import type { SupportContextType, SupportRequestReceipt } from '../types/support';

function contextFromParam(value: string | null): SupportContextType {
  return value === 'alert' || value === 'account' || value === 'device' ? value : 'device';
}

export function SupportPage() {
  const [params] = useSearchParams();
  const [receipt, setReceipt] = useState<{ data: SupportRequestReceipt; category: string } | null>(null);
  const [failed, setFailed] = useState(false);

  return (
    <>
      <section className="border-b border-line-subtle pb-4 pt-6" aria-labelledby="page-title">
        <div className="page-grid">
          <p className="mb-2 text-xs text-ink-secondary">Help</p>
          <h1 id="page-title">Contact support</h1>
          <p className="mt-2 max-w-[44rem] text-base text-ink-secondary">
            Tell us what went wrong with a connection, your data, your account, or an alert. We reply about the problem
            itself and never ask for passwords or health readings.
          </p>
        </div>
      </section>

      <section className="mt-8" aria-label="Support request">
        <div className="page-grid grid gap-8 lg:grid-cols-[5fr_3fr]">
          <div className="tile">
            <h2 id="ctx-h">Support request</h2>
            <SupportForm
              initialContext={contextFromParam(params.get('context'))}
              initialId={params.get('id')}
              onSubmitted={(data, category) => {
                setFailed(false);
                setReceipt({ data, category });
              }}
              onFailed={() => {
                setReceipt(null);
                setFailed(true);
              }}
            />
          </div>

          <div className="tile-white self-start">
            <h2>After you send</h2>
            {receipt && (
              <Notice kind="success" role="status">
                <p>
                  <strong>Request received.</strong> Keep this reference.
                </p>
                <dl className="mt-2 grid grid-cols-[minmax(6rem,9rem)_1fr] gap-x-4 gap-y-2">
                  <dt className="text-ink-secondary">Reference</dt>
                  <dd>{receipt.data.reference}</dd>
                  <dt className="text-ink-secondary">Status</dt>
                  <dd>
                    <StatusBadge status="pending" label="Submitted" />
                  </dd>
                  <dt className="text-ink-secondary">Submitted</dt>
                  <dd>{formatDateTime(receipt.data.submitted_at)}</dd>
                  <dt className="text-ink-secondary">Category</dt>
                  <dd>{receipt.category}</dd>
                </dl>
              </Notice>
            )}
            {failed && (
              <Notice kind="error" role="alert">
                <p>An unexpected error occurred. Your request was not sent. Please try again in a few minutes.</p>
              </Notice>
            )}
            {!receipt && !failed && (
              <p className="text-xs tracking-label text-ink-secondary">
                After you send, you will see a reference, the status and the time here. Keep the reference.
              </p>
            )}
            <h3 className="mt-6 text-xs font-normal tracking-label text-ink-helper">What support can see</h3>
            <p className="text-xs tracking-label text-ink-secondary">
              Only your message, the category, and the area you came from. Support messages never show logs,
              credentials, or technical details.
            </p>
            <h3 className="mt-6 text-xs font-normal tracking-label text-ink-helper">Wellness boundary</h3>
            <p className="text-xs tracking-label text-ink-secondary">
              Support helps with using Sapphire FitConnect. It cannot give medical advice. If you feel unwell, speak to
              a qualified health professional; in an emergency, contact your local emergency services.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
