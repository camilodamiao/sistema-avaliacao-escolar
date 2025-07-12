/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'solare-orange': '#FF6B35',
        'solare-yellow': '#FFC107',
        'solare-red': '#DC3545',
      }
    },
  },
  plugins: [],
}