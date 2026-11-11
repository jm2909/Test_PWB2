/** Tokens extracted from the wireframes (Carbon-style palette, IBM Plex Sans). */
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#0f62fe', hover: '#0050e6', link: '#0043ce' },
        ink: { DEFAULT: '#161616', secondary: '#525252', helper: '#6f6f6f', disabled: '#8d8d8d' },
        surface: { DEFAULT: '#f4f4f4', hover: '#e8e8e8', selected: '#e0e0e0' },
        line: { DEFAULT: '#e0e0e0', subtle: '#c6c6c6', strong: '#8d8d8d' },
        shell: { DEFAULT: '#161616', text: '#f4f4f4', hover: '#353535' },
        danger: { DEFAULT: '#da1e28', bg: '#fff1f1' },
        success: { DEFAULT: '#24a148', bg: '#defbe6' },
        warn: { DEFAULT: '#f1c21b', icon: '#b28600', major: '#ff832b', bg: '#fdf6dd' },
        info: { DEFAULT: '#0043ce', bg: '#edf5ff' },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
      maxWidth: { page: '99rem' },
      letterSpacing: { body: '0.16px', label: '0.32px' },
    },
  },
  plugins: [],
};
