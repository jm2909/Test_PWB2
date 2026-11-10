import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, ApiError } from '../lib/api-client';
import AlertBanner from '../components/dashboard/AlertBanner';
import EmptyTile from '../components/dashboard/EmptyTile';
import SignalTile from '../components/dashboard/SignalTile';
import { useAuth } from '../lib/auth-context';
import type { DashboardResponse } from '../types/dashboard';

function nameFromEmail(email: string): string {
  const local = email.split('@')[0] ?? '';
  const first = (local.split(/[._-]/)[0] ?? '').trim();
  return first ? first.charAt(0).toUpperCase() + first.slice(1) : 'there';
}

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

function formatSynced(iso: string): string {
  const d = new Date(iso);
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  return d.toDateString() === new Date().toDateString() ? `today at ${time}` : `${d.toLocaleDateString()} at ${time}`;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await api.get<DashboardResponse>('/dashboard'));
    } catch (err) {
      setData(null);
      setError(err instanceof ApiError ? err.detail : 'Your dashboard could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const name = data?.display_name ?? (user ? nameFromEmail(user.email) : 'there');
  const needsSetup = user !== null && user.onboarding_status !== 'complete';

  return (
    <div>
      <h1 className="text-[2rem] leading-10">
        {greeting()}, {name}
      </h1>
      <p className="mt-2 text-base text-text-secondary">
        {data?.last_synced_at ? `Last synced ${formatSynced(data.last_synced_at)}` : 'Your connected wellness signals in one place.'}
      </p>

      {needsSetup && (
        <div
          role="status"
          className="mt-8 flex gap-3 border-l-[3px] border-l-[#0043ce] bg-[#edf5ff] px-4 py-3"
        >
          <div>
            <strong className="block font-semibold">Finish setting up your account</strong>
            <Link to="/onboarding" className="text-link">
              Continue account setup
            </Link>
          </div>
        </div>
      )}

      {loading && (
        <p role="status" className="mt-8 text-text-secondary">
          Loading your dashboard…
        </p>
      )}

      {error && (
        <div
          role="alert"
          className="mt-8 flex gap-3 border-l-[3px] border-l-[#f1c21b] bg-[#fcf4d6] px-4 py-3"
        >
          <div>
            <strong className="block font-semibold">Dashboard unavailable</strong>
            <span>{error}</span>{' '}
            <button type="button" onClick={() => void load()} className="text-link underline">
              Try again
            </button>
          </div>
        </div>
      )}

      {data && (
        <>
          <AlertBanner count={data.unread_alert_count ?? 0} />
          <div className="mt-8 grid grid-cols-4 gap-8 md:grid-cols-8 lg:grid-cols-16">
            {data.signal_groups.map((group) => (
              <SignalTile key={group.key} group={group} />
            ))}
            {data.source_gaps.map((gap) => (
              <EmptyTile key={gap.key} gap={gap} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
