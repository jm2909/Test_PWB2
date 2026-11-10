export const DISCLAIMER =
  'FitConnect shares wellness information, not medical advice. It cannot diagnose conditions or respond to emergencies.';

export default function Footer() {
  return (
    <footer className="mt-12 border-t border-border-subtle pt-4 text-xs text-text-secondary">
      {DISCLAIMER}
    </footer>
  );
}
