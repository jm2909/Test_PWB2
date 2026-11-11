import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth-context";
import { ROUTES } from "../routes";
import { Footer } from "./Footer";
import { Header } from "./Header";

/** App shell: skip link, header, primary navigation (signed in only), main, wellness footer. */
const navClass = ({ isActive }: { isActive: boolean }) =>
  `flex min-h-[2.5rem] items-center border-b-[3px] px-4 lg:border-b-0 lg:border-l-[3px] ${
    isActive
      ? "border-primary bg-surface-selected font-semibold !text-ink"
      : "border-transparent !text-ink-secondary hover:bg-surface-hover hover:!text-ink"
  }`;

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const signOut = async () => {
    await logout();
    navigate(ROUTES.login, { replace: true, state: { signedOut: true } });
  };

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main-content"
        className="absolute -left-[999px] top-0 z-20 bg-white px-4 py-3 text-ink focus:left-0"
      >
        Skip to main content
      </a>
      <Header onSignOut={signOut} />
      <div className="flex flex-1 flex-col lg:flex-row lg:items-start">
        {
          <nav
            aria-label="Primary"
            className="border-b border-line bg-white lg:sticky lg:top-12 lg:h-[calc(100vh-3rem)] lg:w-64 lg:flex-none lg:overflow-auto lg:border-b-0 lg:border-r lg:py-4"
          >
            <p className="hidden px-4 py-2 text-xs tracking-label text-ink-helper lg:block">
              Your wellness
            </p>
            <ul className="flex overflow-x-auto lg:block">
              {user && (
                <>
                  <li className="flex-none">
                <NavLink to="/dashboard" className={navClass}>
                  Dashboard
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/connections" className={navClass}>
                  Connections
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/trends" className={navClass}>
                  Trends
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/alerts" className={navClass}>
                  Alerts
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/goals" className={navClass}>
                  Goals
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/support" className={navClass}>
                  Support
                </NavLink>
              </li>
                  <li className="flex-none">
                <NavLink to="/consent" className={navClass}>
                  Privacy and data rights
                </NavLink>
              </li>
                </>
              )}
              <li className="flex-none">
                <NavLink to="/account" className={navClass}>
                  Account access
                </NavLink>
              </li>
            </ul>
          </nav>
        }
        <main id="main-content" className="min-w-0 flex-1 pb-12">
          <Outlet />
        </main>
      </div>
      <Footer />
    </div>
  );
}
