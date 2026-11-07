/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a5bbfc',
          400: '#8197f8',
          500: '#6475f1',
          600: '#4f56e4',
          700: '#4044c9',
          800: '#3639a2',
          900: '#313680',
          950: '#1e1f4b',
        },
        surface: {
          900: '#0d0e17',
          800: '#13141f',
          700: '#1a1b2e',
          600: '#1e2035',
          500: '#252740',
          400: '#2e3050',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
