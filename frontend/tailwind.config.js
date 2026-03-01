/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        felt: {
          900: '#0a1a0a',
          800: '#112211',
        },
      },
    },
  },
  plugins: [],
}
