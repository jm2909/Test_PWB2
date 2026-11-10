import { NavLink } from 'react-router-dom';

function linkClass({ isActive }: { isActive: boolean }): string {
  return `block border-l-[3px] px-4 py-3 no-underline ${
    isActive
      ? 'border-l-link bg-layer font-semibold text-text-primary'
      : 'border-l-transparent text-text-secondary'
  }`;
}

export default function SideNav() {
  return (
    <nav
      aria-label="Primary"
      className="border-b border-border-subtle bg-white lg:border-b-0 lg:border-r"
    >
      <ul className="flex flex-wrap lg:block lg:pt-4">
        <li>
          <NavLink to="/" end className={linkClass}>
            Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink to="/trends" className={linkClass}>
            Trends
          </NavLink>
        </li>
        <li>
          <NavLink to="/insights" className={linkClass}>
            Insights and alerts
          </NavLink>
        </li>
        <li>
          <NavLink to="/devices" className={linkClass}>
            Devices
          </NavLink>
        </li>
        <li>
          <NavLink to="/goals" className={linkClass}>
            Goals
          </NavLink>
        </li>
        <li>
          <NavLink to="/onboarding" className={linkClass}>
            Account setup
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
