import { Link } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';
import { ROUTES } from '../routes';

export function Header({ onSignOut }: { onSignOut: () => void }) {
  const { user } = useAuth();
  return (
    <header className="sticky top-0 z-10 flex min-h-[3rem] items-center gap-4 bg-shell px-4 text-shell-text">
      <Link to={user ? ROUTES.dashboard : ROUTES.login} className="whitespace-nowrap font-semibold !text-shell-text">
        Sapphire <span className="font-normal">FitConnect</span>
      </Link>
      <span className="flex-1" />
      {user ? (
        <>
          <span className="text-xs text-line-subtle">Signed in as {user.display_name}</span>
          <button
            type="button"
            onClick={onSignOut}
            className="inline-flex min-h-[3rem] items-center px-4 text-shell-text hover:bg-shell-hover"
          >
            Sign out
          </button>
        </>
      ) : (
        <span className="text-xs text-line-subtle">Signed out</span>
      )}
    </header>
  );
}
