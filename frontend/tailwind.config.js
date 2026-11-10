/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: { sm: '672px', lg: '1056px', xl: '1312px' },
    extend: {
      gridTemplateColumns: { 16: 'repeat(16, minmax(0, 1fr))' },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "'Helvetica Neue'", 'Arial', 'sans-serif'],
      },
      colors: {
        background: 'var(--cds-background)',
        layer: 'var(--cds-layer-01)',
        field: 'var(--cds-field-01)',
        'border-subtle': 'var(--cds-border-subtle-01)',
        'border-strong': 'var(--cds-border-strong-01)',
        'text-primary': 'var(--cds-text-primary)',
        'text-secondary': 'var(--cds-text-secondary)',
        'text-helper': 'var(--cds-text-helper)',
        'text-error': 'var(--cds-text-error)',
        link: 'var(--cds-link-primary)',
        'button-primary': 'var(--cds-button-primary)',
        'support-error': 'var(--cds-support-error)',
        'support-success': 'var(--cds-support-success)',
        'support-warning': 'var(--cds-support-warning)',
        'support-info': 'var(--cds-support-info)',
        'notify-error': 'var(--cds-notification-error-background-color)',
        'notify-success': 'var(--cds-notification-success-background-color)',
        'notify-warning': 'var(--cds-notification-warning-background-color)',
        'notify-info': 'var(--cds-notification-info-background-color)',
        focus: 'var(--cds-focus)',
      },
    },
  },
  plugins: [],
};
