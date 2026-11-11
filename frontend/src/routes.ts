export const ROUTES = {
  login: '/login',
  account: '/account',
  register: '/register',
  consent: '/consent',
  dashboard: '/dashboard',
  connections: '/connections',
  trends: '/trends',
  alerts: '/alerts',
  goals: '/goals',
  support: '/support',
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES];

/** Header/sidebar navigation: only these destinations plus sign-out. */
export const NAV_ITEMS: ReadonlyArray<{ label: string; to: RoutePath }> = [
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Connections', to: '/connections' },
  { label: 'Trends', to: '/trends' },
  { label: 'Alerts', to: '/alerts' },
  { label: 'Goals', to: '/goals' },
  { label: 'Support', to: '/support' },
  { label: 'Privacy and data rights', to: '/consent' },
  { label: 'Account access', to: '/account' },
];
