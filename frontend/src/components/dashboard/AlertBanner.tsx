import { Link } from 'react-router-dom';

export default function AlertBanner({ count }: { count: number }) {
  if (count <= 0) return null;
  return (
    <div role="status" className="mt-8 flex gap-3 border-l-[3px] border-l-support-warning bg-notify-warning px-4 py-3">
      <div>
        <strong className="block font-semibold">
          You have {count} new wellness {count === 1 ? 'alert' : 'alerts'}
        </strong>
        <Link to="/insights" className="text-link">
          Read the alert and suggested next step
        </Link>
      </div>
    </div>
  );
}
